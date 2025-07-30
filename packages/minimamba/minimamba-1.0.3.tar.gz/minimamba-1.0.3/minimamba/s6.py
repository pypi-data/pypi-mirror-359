import torch
import torch.nn as nn
import torch.nn.functional as F
from torch import Tensor
from typing import Optional, Tuple
import math

from .config import MambaConfig

class S6(nn.Module):
    """
    S6 (Selective State Space) layer - Core of Mamba architecture.
    Implements a selective scan mechanism to model long-range dependencies.
    
    This implementation includes a mathematically correct parallel scan
    that works efficiently on macOS M4 Pro (MPS backend).
    """
    def __init__(self, config: MambaConfig, layer_idx: Optional[int] = None):
        super().__init__()

        self.d_model = config.d_model
        self.d_state = config.d_state
        self.d_conv = config.d_conv
        self.expand = config.expand
        self.d_inner = config.d_inner
        self.dt_rank = config.dt_rank
        self.use_fast_path = config.use_fast_path
        self.layer_idx = layer_idx

        # Linear input projection
        self.in_proj = nn.Linear(self.d_model, self.d_inner * 2, bias=config.bias)

        # Depthwise convolution for local interaction
        self.conv1d = nn.Conv1d(
            in_channels=self.d_inner,
            out_channels=self.d_inner,
            kernel_size=config.d_conv,
            groups=self.d_inner,
            bias=config.conv_bias,
            padding=config.d_conv - 1
        )

        # Activation function (SiLU)
        self.act = nn.SiLU()

        # Projection for state-space parameters
        self.x_proj = nn.Linear(self.d_inner, self.dt_rank + self.d_state * 2, bias=False)
        self.dt_proj = nn.Linear(self.dt_rank, self.d_inner, bias=True)

        # Initialize dt_proj weight
        dt_init_std = self.dt_rank ** -0.5 * config.dt_scale
        if config.dt_init == "constant":
            nn.init.constant_(self.dt_proj.weight, dt_init_std)
        elif config.dt_init == "random":
            nn.init.uniform_(self.dt_proj.weight, -dt_init_std, dt_init_std)

        # Initialize dt bias using log-uniform sampling
        dt = torch.exp(
            torch.rand(self.d_inner) * (math.log(config.dt_max) - math.log(config.dt_min)) + math.log(config.dt_min)
        ).clamp(min=config.dt_init_floor)
        inv_dt = dt + torch.log(-torch.expm1(-dt))
        with torch.no_grad():
            self.dt_proj.bias.copy_(inv_dt)
        self.dt_proj.bias._no_reinit = True

        # A matrix (in log space for numerical stability)
        A = torch.arange(1, self.d_state + 1, dtype=torch.float32).repeat(self.d_inner, 1)
        self.A_log = nn.Parameter(torch.log(A))
        self.A_log._no_weight_decay = True

        # D parameter for skip connection
        self.D = nn.Parameter(torch.ones(self.d_inner))
        self.D._no_weight_decay = True

        # Output projection
        self.out_proj = nn.Linear(self.d_inner, self.d_model, bias=config.bias)

    def forward(self, hidden_states: Tensor, inference_params=None) -> Tensor:
        """
        Forward pass of the S6 layer.

        Args:
            hidden_states: Input tensor (batch, seq_len, d_model)
            inference_params: Optional inference cache for generation

        Returns:
            Output tensor (batch, seq_len, d_model)
        """
        batch, seqlen, _ = hidden_states.shape

        # === Handle empty input sequence early ===
        if seqlen == 0:
            return hidden_states.new_zeros(batch, 0, self.d_model)
            
        # Get cache state if in inference mode
        conv_state, ssm_state = None, None
        if inference_params is not None:
            conv_state, ssm_state = self._get_states_from_cache(inference_params, batch)
            if inference_params.seqlen_offset > 0:
                hidden_states = hidden_states[:, -1:, :]
                seqlen = 1

        # Linear projection and split
        xz = self.in_proj(hidden_states)
        x, z = xz.chunk(2, dim=-1)

        # Optimized convolution with in-place operations
        if conv_state is not None:
            if seqlen == 1:
                # Use in-place operations to reduce memory allocation
                conv_state = torch.roll(conv_state, shifts=-1, dims=-1)
                conv_state[:, :, -1] = x.squeeze(1)
                x = torch.sum(conv_state * self.conv1d.weight[:, 0, :], dim=-1)
                if self.conv1d.bias is not None:
                    x = x + self.conv1d.bias.unsqueeze(0)
                x = x.unsqueeze(1)
            else:
                # Preallocate output tensor
                x_conv = self.conv1d(x.transpose(1, 2))
                x = x_conv.transpose(1, 2)[:, :seqlen, :]
                # Use sliced views instead of copy
                conv_state[:] = x[:, -self.d_conv:, :].transpose(1, 2)
        else:
            x = self.conv1d(x.transpose(1, 2))[..., :seqlen].transpose(1, 2)

        # Non-linearity
        x = self.act(x)

        # Selective scan computation
        y = self.selective_scan(x, z, ssm_state, inference_params)
        return self.out_proj(y)

    def selective_scan(self, x: Tensor, z: Tensor, ssm_state=None, inference_params=None) -> Tensor:
        """
        Selective scan logic: parallel scan or inference step.
        """
        x_dbl = self.x_proj(x)
        dt, B, C = torch.split(x_dbl, [self.dt_rank, self.d_state, self.d_state], dim=-1)

        dt = self.dt_proj(dt)
        dt = F.softplus(dt + self.dt_proj.bias)

        A = -torch.exp(self.A_log.float())

        if inference_params is not None and inference_params.seqlen_offset > 0:
            return self._selective_scan_inference(x, dt, A, B, C, self.D, z, ssm_state)
        else:
            return self._selective_scan_forward(x, dt, A, B, C, self.D, z)

    def _selective_scan_forward(self, u, delta, A, B, C, D, z):
        """
        Optimized selective scan with fused operations.
        """
        batch_size, seq_len, d_inner = u.shape
        d_state = A.shape[-1]
        
        # Correct dimension computation
        # delta: (batch, seq_len, d_inner)
        # A: (d_inner, d_state)  
        # B: (batch, seq_len, d_state)
        # C: (batch, seq_len, d_state)
        
        # Expand A to correct shape
        delta_A = torch.exp(delta.unsqueeze(-1) * A.unsqueeze(0).unsqueeze(0))  # (batch, seq_len, d_inner, d_state)
        
        # Compute deltaB_u
        deltaB_u = delta.unsqueeze(-1) * B.unsqueeze(2) * u.unsqueeze(-1)  # (batch, seq_len, d_inner, d_state)
        
        # Parallel scan
        states = self._optimized_parallel_scan(delta_A, deltaB_u)  # (batch, seq_len, d_inner, d_state)
        
        # Correct output computation: multiply states and C along the d_state dimension
        # states: (batch, seq_len, d_inner, d_state)
        # C: (batch, seq_len, d_state)
        # Result: (batch, seq_len, d_inner)
        y = torch.sum(states * C.unsqueeze(2), dim=-1) + u * D
        
        # Gating
        y = y * z
        return y

    def _parallel_scan_log_space(self, A, Bu):
        """
        True parallel scan implementation using PyTorch's built-in operations.
        
        This implements the associative parallel scan algorithm that solves:
        h_k = A_k * h_{k-1} + B_k * u_k
        
        The key insight is using the associative operator:
        (A1, B1) ⊕ (A2, B2) = (A2 * A1, A2 * B1 + B2)
        
        Args:
            A: Transition matrices (batch, seq_len, d_inner, d_state)
            Bu: Input terms (batch, seq_len, d_inner, d_state)
            
        Returns:
            states: Hidden states (batch, seq_len, d_inner, d_state)
        """
        batch_size, seq_len, d_inner, d_state = A.shape
        
        # For very small sequences, sequential is actually faster
        if seq_len <= 8:
            return self._sequential_scan(A, Bu)
        
        # For medium sequences, use optimized parallel scan
        if seq_len <= 128:
            return self._true_parallel_scan(A, Bu)
        
        # For long sequences, use block-wise parallel scan to balance memory
        return self._block_parallel_scan(A, Bu)
    
    def _sequential_scan(self, A, Bu):
        """
        Sequential scan for short sequences or fallback.
        """
        batch_size, seq_len, d_inner, d_state = A.shape
        
        # Initialize states
        states = torch.zeros_like(Bu)
        h = torch.zeros(batch_size, d_inner, d_state, device=A.device, dtype=A.dtype)
        
        for i in range(seq_len):
            h = A[:, i] * h + Bu[:, i]
            states[:, i] = h
            
        return states
    
    def _true_parallel_scan(self, A, Bu):
        """
        Divide-and-conquer parallel scan algorithm - O(n log n)
        """
        batch_size, seq_len, d_inner, d_state = A.shape

        if seq_len <= 32:
            return self._sequential_scan(A, Bu)

        # Divide and conquer recursion
        mid = seq_len // 2

        # Left half
        left_A = A[:, :mid]
        left_Bu = Bu[:, :mid]
        left_states = self._true_parallel_scan(left_A, left_Bu)

        # Right half
        right_A = A[:, mid:]
        right_Bu = Bu[:, mid:]

        # Compute the effect of the left half on the right half
        left_carry = left_states[:, -1]  # Last state from the left half

        # Compute the propagation factor
        right_A_prefix = torch.ones_like(right_A[:, 0])
        for i in range(right_A.shape[1]):
            if i == 0:
                right_Bu[:, i] = right_Bu[:, i] + right_A[:, i] * left_carry
            else:
                right_A_prefix = right_A_prefix * right_A[:, i-1]

        right_states = self._true_parallel_scan(right_A, right_Bu)

        # Merge results
        states = torch.cat([left_states, right_states], dim=1)
        return states

    
    def _block_parallel_scan(self, A, Bu):
        """
        Block-wise parallel scan for long sequences to balance memory usage.
        
        This processes the sequence in blocks, where each block is computed
        with true parallel scan, and blocks are combined sequentially.
        """
        batch_size, seq_len, d_inner, d_state = A.shape
        
        # Choose block size based on available memory and sequence length
        block_size = min(64, max(16, seq_len // 8))
        num_blocks = (seq_len + block_size - 1) // block_size
        
        states = torch.zeros_like(Bu)
        carry_state = torch.zeros(batch_size, d_inner, d_state, device=A.device, dtype=A.dtype)
        
        for block_idx in range(num_blocks):
            start_idx = block_idx * block_size
            end_idx = min((block_idx + 1) * block_size, seq_len)
            
            # Extract block
            block_A = A[:, start_idx:end_idx]
            block_Bu = Bu[:, start_idx:end_idx]
            
            # Add carry state to the first element of Bu
            if block_idx > 0:
                block_Bu = block_Bu.clone()
                block_Bu[:, 0] = block_Bu[:, 0] + block_A[:, 0] * carry_state
            
            # Use true parallel scan within the block
            if end_idx - start_idx <= 8:
                block_states = self._block_scan(block_A, block_Bu,
                                              carry_state if block_idx == 0 else None)
            else:
                block_states = self._true_parallel_scan(block_A, block_Bu)
                if block_idx > 0:
                    # Apply carry state to all elements in the block
                    cumsum_log_A = torch.cumsum(torch.log(block_A.clamp(min=1e-20)), dim=1)
                    prefix_A = torch.exp(cumsum_log_A)
                    for i in range(end_idx - start_idx):
                        block_states[:, i] = block_states[:, i] + prefix_A[:, i] * carry_state
            
            states[:, start_idx:end_idx] = block_states
            
            # Update carry state for next block
            if end_idx < seq_len:
                carry_state = block_states[:, -1]
        
        return states
    
    def _block_scan(self, A, Bu, initial_state):
        """
        Scan within a single block.
        """
        batch_size, block_len, d_inner, d_state = A.shape
        
        states = torch.zeros_like(Bu)
        h = initial_state if initial_state is not None else torch.zeros(batch_size, d_inner, d_state, device=A.device, dtype=A.dtype)
        
        for i in range(block_len):
            h = A[:, i] * h + Bu[:, i]
            states[:, i] = h
            
        return states

    def _selective_scan_inference(self, u, delta, A, B, C, D, z, ssm_state):
        """
        Inference-time selective scan (single token).
        """
        deltaA = torch.exp(delta.squeeze(1).unsqueeze(-1) * A)
        deltaB_u = delta.squeeze(1).unsqueeze(-1) * B.squeeze(1).unsqueeze(1) * u.squeeze(1).unsqueeze(-1)

        ssm_state.copy_(deltaA * ssm_state + deltaB_u)

        y = torch.einsum('bds,bs->bd', ssm_state, C.squeeze(1))
        y = y + u.squeeze(1) * D
        return (y * z.squeeze(1)).unsqueeze(1)

    def _get_states_from_cache(self, inference_params, batch_size) -> Tuple[Tensor, Tensor]:
        """
        Optimized cache retrieval with pre-allocation.
        """
        assert self.layer_idx is not None
        cache = getattr(inference_params, 'cache', getattr(inference_params, 'key_value_memory_dict', {}))

        conv_key = f"conv_state_{self.layer_idx}"
        ssm_key = f"ssm_state_{self.layer_idx}"
        
        # Preallocate and reuse cache
        if conv_key not in cache:
            cache[conv_key] = torch.zeros(
                batch_size, self.d_inner, self.d_conv,
                device=self.A_log.device,
                dtype=self.A_log.dtype,
                pin_memory=False
            )
        
        if ssm_key not in cache:
            cache[ssm_key] = torch.zeros(
                batch_size, self.d_inner, self.d_state,
                device=self.A_log.device,
                dtype=self.A_log.dtype,
                pin_memory=False
            )
        
        return cache[conv_key], cache[ssm_key]

    def _optimized_parallel_scan(self, A, Bu):
        """
        Memory-optimized parallel scan - O(n) complexity
        """
        batch_size, seq_len, d_inner, d_state = A.shape
        
        # Use sequential scan for short sequences
        if seq_len <= 64:
            return self._sequential_scan(A, Bu)
        
        # Use a fixed-size sliding window
        window_size = 128
        overlap = 16
        
        states = torch.zeros_like(Bu)
        
        # Process with sliding window
        for start in range(0, seq_len, window_size - overlap):
            end = min(start + window_size, seq_len)
            
            window_A = A[:, start:end]
            window_Bu = Bu[:, start:end]
            
            # Handle overlapping region
            if start > 0:
                # Get initial state from previous window
                prev_state = states[:, start - 1]
                window_Bu[:, 0] = window_Bu[:, 0] + window_A[:, 0] * prev_state
            
            # Sequential scan within the current window
            window_states = self._sequential_scan(window_A, window_Bu)
            
            # Save results (including overlapping part)
            if start == 0:
                states[:, start:end] = window_states
            else:
                states[:, start:end] = window_states
        
        return states


    def _chunk_scan(self, A, Bu):
        """
        Regular chunk scan implementation without JIT compilation.
        """
        batch_size, chunk_len, d_inner, d_state = A.shape
        states = torch.zeros_like(Bu)
        
        h = torch.zeros(batch_size, d_inner, d_state, device=A.device, dtype=A.dtype)
        for i in range(chunk_len):
            h = A[:, i] * h + Bu[:, i]
            states[:, i] = h
        
        return states
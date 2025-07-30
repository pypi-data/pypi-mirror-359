import torch
import torch.nn as nn
import torch.nn.functional as F
import math

class RMSNorm(nn.Module):
    def __init__(self, dim, eps=1e-8):
        super().__init__()
        self.eps = eps
        self.weight = nn.Parameter(torch.ones(dim))

    def _norm(self, x):
        return x * torch.rsqrt(x.pow(2).mean(dim=-1, keepdim=True) + self.eps)

    def forward(self, x):
        output = self._norm(x.float()).type_as(x)
        return output * self.weight

class RotaryEmbedding(nn.Module):
    def __init__(self, dim, max_seq_len=2048):
        super().__init__()
        self.dim = dim
        self.max_seq_len = max_seq_len
        inv_freq = 1.0 / (10000 ** (torch.arange(0, dim, 2).float() / dim))
        self.register_buffer("inv_freq", inv_freq)
        self._set_cos_sin_cache(seq_len=max_seq_len, device="cpu", dtype=torch.float32)

    def _set_cos_sin_cache(self, seq_len, device, dtype):
        self.max_seq_len = seq_len
        t = torch.arange(self.max_seq_len, device=device, dtype=self.inv_freq.dtype)
        freqs = torch.einsum("i,j->ij", t, self.inv_freq)
        emb = torch.cat((freqs, freqs), dim=-1)
        self.register_buffer("cos_cached", emb.cos().to(dtype), persistent=False)
        self.register_buffer("sin_cached", emb.sin().to(dtype), persistent=False)

    def forward(self, x):
        seq_len = x.shape[-2]
        if seq_len > self.max_seq_len:
            self._set_cos_sin_cache(seq_len=seq_len, device=x.device, dtype=x.dtype)
        cos = self.cos_cached[:seq_len].unsqueeze(0).unsqueeze(1)
        sin = self.sin_cached[:seq_len].unsqueeze(0).unsqueeze(1)
        x1 = x[..., ::2]
        x2 = x[..., 1::2]
        x_rot = torch.stack((-x2, x1), dim=-1).flatten(-2)
        return x * cos + x_rot * sin

class Retention(nn.Module):
    def __init__(self, embed_dim, heads, dropout=0.1):
        super().__init__()
        self.heads = heads
        self.head_dim = embed_dim // heads
        self.scale = math.sqrt(self.head_dim)
        self.w_q = nn.Linear(embed_dim, embed_dim)
        self.w_k = nn.Linear(embed_dim, embed_dim)
        self.w_v = nn.Linear(embed_dim, embed_dim)
        self.w_g = nn.Linear(embed_dim, embed_dim)
        self.w_o = nn.Linear(embed_dim, embed_dim)
        self.group_norm = nn.GroupNorm(heads, embed_dim)
        self.dropout = nn.Dropout(dropout)
        self.rotary = RotaryEmbedding(self.head_dim)
        self.decay_predictor = nn.Sequential(
            nn.Linear(embed_dim, heads),
            nn.Sigmoid()
        )

    def forward(self, x):
        B, T, _ = x.shape
        Q = self.w_q(x).view(B, T, self.heads, self.head_dim).transpose(1, 2)
        K = self.w_k(x).view(B, T, self.heads, self.head_dim).transpose(1, 2)
        V = self.w_v(x).view(B, T, self.heads, self.head_dim).transpose(1, 2)
        
        Q = self.rotary(Q)
        K = self.rotary(K)
        
        scores = (Q @ K.transpose(-2, -1)) / self.scale
        
        predicted_decays = self.decay_predictor(x.mean(dim=1))
        scaled_decays = 8 * predicted_decays
        dynamic_log_decay = torch.log(1.0 - (2 ** (-5 - scaled_decays))).view(B, self.heads, 1, 1)

        m = torch.arange(T, device=x.device).view(1, T)
        n = torch.arange(T, device=x.device).view(T, 1)
        pos_diff = (m - n).clamp(min=0).unsqueeze(0).unsqueeze(0)
        decay_mask = pos_diff * dynamic_log_decay
        scores = scores + decay_mask
        
        attn_out = F.softmax(scores, dim=-1) @ V
        out = attn_out.transpose(1, 2).reshape(B, T, -1)
        out = self.group_norm(out.transpose(1, 2)).transpose(1, 2)
        return self.w_o(F.silu(self.w_g(x)) * out)

class DillNetBlock(nn.Module):
    def __init__(self, embed_dim, heads, ffn_dim=None, dropout=0.1):
        super().__init__()
        if ffn_dim is None:
            ffn_dim = embed_dim * 4
        self.norm1 = RMSNorm(embed_dim)
        self.attention_layer = Retention(embed_dim, heads, dropout)
        self.norm2 = RMSNorm(embed_dim)
        self.w1 = nn.Linear(embed_dim, ffn_dim, bias=False)
        self.w2 = nn.Linear(ffn_dim, embed_dim, bias=False)
        self.w3 = nn.Linear(embed_dim, ffn_dim, bias=False)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        attn_out = self.attention_layer(self.norm1(x))
        x = x + attn_out
        normed_x = self.norm2(x)
        ffn_out = self.w2(F.silu(self.w1(normed_x)) * self.w3(normed_x))
        x = x + self.dropout(ffn_out)
        return x

class DillNet(nn.Module):
    def __init__(self, embed_dim, depth, heads=8, ffn_dim=None):
        super().__init__()
        self.blocks = nn.ModuleList([
            DillNetBlock(embed_dim, heads, ffn_dim=ffn_dim, dropout=0.1)
            for _ in range(depth)
        ])
        self.final_norm = RMSNorm(embed_dim)

    def forward(self, x):
        for block in self.blocks:
            x = block(x)
        x = self.final_norm(x)
        return x
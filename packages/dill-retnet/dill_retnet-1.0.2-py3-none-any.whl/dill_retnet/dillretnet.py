import torch
import torch.nn as nn
import torch.nn.functional as F
import math

class Retention(nn.Module):
    def __init__(self, embed_dim, heads):
        super().__init__()
        self.embed_dim = embed_dim
        self.heads = heads
        self.head_dim = embed_dim // heads
        assert self.head_dim * heads == embed_dim, "embed_dim must be divisible by heads"
        
        self.w_q = nn.Linear(embed_dim, embed_dim)
        self.w_k = nn.Linear(embed_dim, embed_dim)
        self.w_v = nn.Linear(embed_dim, embed_dim)
        self.gate = nn.Linear(embed_dim, embed_dim)

    def forward(self, x):
        B, T, _ = x.shape
        
        gammas = 1.0 - (2.0 ** (-5 - torch.arange(self.heads, device=x.device)))
        
        Q = self.w_q(x)
        K = self.w_k(x)
        V = self.w_v(x)
        
        Q = Q.view(B, T, self.heads, self.head_dim).transpose(1, 2)
        K = K.view(B, T, self.heads, self.head_dim).transpose(1, 2)
        V = V.view(B, T, self.heads, self.head_dim).transpose(1, 2)
        
        idx = torch.arange(T, device=x.device)
        rel_pos = idx.view(1, -1) - idx.view(-1, 1)
        
        decay = gammas.view(-1, 1, 1) ** rel_pos.unsqueeze(0)
        decay_matrix = decay * (rel_pos.unsqueeze(0) >= 0).float()
        
        scores = torch.matmul(Q, K.transpose(-1, -2)) / math.sqrt(self.head_dim)
        scores = scores * decay_matrix.unsqueeze(0)
        output = torch.matmul(scores, V)
        
        output = output.transpose(1, 2).contiguous().view(B, T, self.embed_dim)
        output = F.silu(self.gate(x)) * output
        return output

class RetNetBlock(nn.Module):
    def __init__(self, embed_dim, heads, ffn_dim=None, groups=8):
        super().__init__()
        if ffn_dim is None:
            ffn_dim = 4 * embed_dim
        
        self.retention = Retention(embed_dim, heads)
        self.group_norm1 = nn.GroupNorm(groups, embed_dim)
        self.ffn = nn.Sequential(
            nn.Linear(embed_dim, ffn_dim),
            nn.GELU(),
            nn.Linear(ffn_dim, embed_dim)
        )
        self.group_norm2 = nn.GroupNorm(groups, embed_dim)

    def forward(self, x):
        y = self.retention(x)
        y = self.group_norm1(y.permute(0, 2, 1)).permute(0, 2, 1)
        x = x + y
        
        y = self.ffn(x)
        y = self.group_norm2(y.permute(0, 2, 1)).permute(0, 2, 1)
        x = x + y
        return x

class RetNet(nn.Module):
    def __init__(self, embed_dim, depth, heads=8, ffn_dim=None, groups=8):
        super().__init__()
        self.blocks = nn.ModuleList([
            RetNetBlock(embed_dim, heads, ffn_dim, groups) 
            for _ in range(depth)
        ])
    
    def forward(self, x):
        for block in self.blocks:
            x = block(x)
        return x
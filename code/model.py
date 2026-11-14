import torch
import torch.nn as nn
import torch.nn.functional as F


class SE(nn.Module):
    """压缩-激励通道注意力（式5-7）。"""

    def __init__(self, c, r=8):
        super().__init__()
        h = max(1, c // r)
        self.fc1 = nn.Linear(c, h)
        self.fc2 = nn.Linear(h, c)

    def forward(self, x):
        b, c, _, _ = x.shape
        s = x.mean(dim=(2, 3))
        s = torch.sigmoid(self.fc2(F.relu(self.fc1(s))))
        return x * s.view(b, c, 1, 1)


def conv_block(cin, cout, ds=False, se=False):
    """一组 = 两次 3x3 卷积（标准）或 深度卷积+逐点卷积（可分离），均含 BN+ReLU。"""
    layers = []
    if ds:
        layers += [nn.Conv2d(cin, cin, 3, padding=1, groups=cin, bias=False),
                   nn.BatchNorm2d(cin), nn.ReLU(inplace=True),
                   nn.Conv2d(cin, cout, 1, bias=False),
                   nn.BatchNorm2d(cout), nn.ReLU(inplace=True)]
    else:
        layers += [nn.Conv2d(cin, cout, 3, padding=1, bias=False),
                   nn.BatchNorm2d(cout), nn.ReLU(inplace=True),
                   nn.Conv2d(cout, cout, 3, padding=1, bias=False),
                   nn.BatchNorm2d(cout), nn.ReLU(inplace=True)]
    if se:
        layers.append(SE(cout))
    return nn.Sequential(*layers)


class UNet(nn.Module):
    """4 级下采样 U-Net；channels=32/64/128/256，瓶颈 512。"""

    def __init__(self, in_ch=9, ds=False, se=False, base=32, depth=4):
        super().__init__()
        chs = [base * 2 ** i for i in range(depth)]          # 32,64,128,256
        self.stem = nn.Sequential(
            nn.Conv2d(in_ch, chs[0], 3, padding=1, bias=False),
            nn.BatchNorm2d(chs[0]), nn.ReLU(inplace=True))
        self.enc = nn.ModuleList()
        cin = chs[0]
        for c in chs:
            self.enc.append(conv_block(cin, c, ds, se))
            cin = c
        self.pool = nn.MaxPool2d(2)
        self.bottleneck = conv_block(cin, base * 2 ** depth, ds, se)
        self.up = nn.ModuleList()
        self.dec = nn.ModuleList()
        cin = base * 2 ** depth
        for c in reversed(chs):
            self.up.append(nn.ConvTranspose2d(cin, c, 2, stride=2))
            self.dec.append(conv_block(c * 2, c, ds, se))
            cin = c
        self.head = nn.Conv2d(cin, 1, 1)

    def forward(self, x):
        x = self.stem(x)
        skips = []
        for blk in self.enc:
            x = blk(x)
            skips.append(x)
            x = self.pool(x)
        x = self.bottleneck(x)
        for u, d, s in zip(self.up, self.dec, reversed(skips)):
            x = u(x)
            x = torch.cat([x, s], dim=1)
            x = d(x)
        return self.head(x)


CONFIGS = {
    # 名称: (in_ch, ds, se, SE降维比例r)
    "base3":   (3, False, False, 8),
    "ds3":     (3, True, False, 8),
    "dsse3":   (3, True, True, 8),
    "dsmulti": (9, True, False, 8),
    "full":    (9, True, True, 8),
    "r4":      (9, True, True, 4),
    "r16":     (9, True, True, 16),
    # 特征组消融：tex7 = 后向散射3 + GLCM 4；ter5 = 后向散射3 + DEM 2
    "tex7":    (7, True, False, 8),
    "ter5":    (5, True, False, 8),
}

# 各配置在 9 通道特征张量中实际使用的通道下标
CHANNELS = {
    3: [0, 1, 2],
    5: [0, 1, 2, 7, 8],
    7: [0, 1, 2, 3, 4, 5, 6],
    9: None,
}


def build(name):
    in_ch, ds, se, r = CONFIGS[name]
    m = UNet(in_ch=in_ch, ds=ds, se=se)
    if se and r != 8:
        for mod in m.modules():
            if isinstance(mod, SE):
                mod.__init__(mod.fc1.in_features, r)
    return m


def count_params(m):
    return sum(p.numel() for p in m.parameters())

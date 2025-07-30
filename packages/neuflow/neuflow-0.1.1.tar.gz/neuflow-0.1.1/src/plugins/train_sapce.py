import torch

from .api import Plugin, PluginLoss


class TrainSpace(Plugin):
    def __init__(self, resolution: int, name: str = 'tsm'):
        super().__init__(name=name)
        self.register_buffer('aabb_std', torch.tensor([-1.0, -1.0, -1.0, 1.0, 1.0, 1.0]))  # [low_x, low_y, low_z, high_x, high_y, high_z]
        self.register_buffer('bound_std', torch.tensor([-1.0, -1.0, -1.0, 1.0, 1.0, 1.0]))  # [low_x, low_y, low_z, high_x, high_y, high_z]
        self.register_buffer('background_color', torch.tensor([0.0, 0.0, 0.0]))  # [r, g, b]
        self.register_buffer('trained_grids', torch.zeros((resolution, resolution, resolution), dtype=torch.int32))

        self.res = 256
        coords = torch.linspace(0, 1, steps=self.res + 1)
        centers = (coords[:-1] + coords[1:]) / 2
        x, y, z = torch.meshgrid(centers, centers, centers, indexing='ij')
        self.xyz = torch.stack([x, y, z], dim=-1).view(-1, 3)  # shape: (res^3, 1)

    def set_aabb_std(self, aabb_std: list):
        self.aabb_std = torch.tensor(aabb_std)

    def set_bound_std(self, bound_std: list):
        self.bound_std = torch.tensor(bound_std)

    def set_background_color(self, background_color: list):
        self.background_color = torch.tensor(background_color)

    def reset_plugin(self, dtype, device):
        if self.aabb_std.dtype != dtype:
            self.aabb_std = self.aabb_std.to(dtype=dtype)
        if self.aabb_std.device != device:
            self.aabb_std = self.aabb_std.to(device=device)
        if self.bound_std.dtype != dtype:
            self.bound_std = self.bound_std.to(dtype=dtype)
        if self.bound_std.device != device:
            self.bound_std = self.bound_std.to(device=device)
        if self.background_color.dtype != dtype:
            self.background_color = self.background_color.to(dtype=dtype)
        if self.background_color.device != device:
            self.background_color = self.background_color.to(device=device)
        if self.trained_grids.device != device:
            self.trained_grids = self.trained_grids.to(device=device)
        if self.xyz.dtype != dtype:
            self.xyz = self.xyz.to(dtype=dtype)
        if self.xyz.device != device:
            self.xyz = self.xyz.to(device=device)

    def update(self, xyz, index):
        assert xyz.max() <= 1.0 and xyz.min() >= 0.0, "Normalized xyz coordinates should be in [0, 1] range."
        assert index < 32, "Index must be less than 32."
        res = self.trained_grids.shape[0]  # Assuming trained_grids is a 4D tensor with shape (1, res, res, res)
        idx = (xyz * res).long().clamp(0, res - 1)
        x, y, z = idx[:, 0], idx[:, 1], idx[:, 2]

        bitmask = 1 << index
        before = self.trained_grids[x, y, z]
        changed = (before & bitmask) == 0
        self.trained_grids[x, y, z] = before | bitmask
        num_changed = changed.sum().item()
        return num_changed

    def exclusive_mask(self, xyz: torch.Tensor):
        pass

    def exclusive_grid(self):
        nonzero_mask = self.trained_grids != 0  # shape: (N, N, N)，bool
        # 初始化一个全 False 的 mask
        mask = torch.zeros_like(self.trained_grids, dtype=torch.bool)

        # 获取所有非零元素的索引
        indices = nonzero_mask.nonzero(as_tuple=False)  # shape: (M, 3)
        values = self.trained_grids[nonzero_mask]  # shape: (M,)

        # 判断是否是2的幂
        power_of_two_mask = (values & (values - 1)) == 0  # shape: (M,)

        # 只保留满足条件的位置
        selected_indices = indices[power_of_two_mask]  # shape: (K, 3)

        # 将这些位置设为 True
        mask[selected_indices[:, 0], selected_indices[:, 1], selected_indices[:, 2]] = True

        return mask  # shape: (N, N, N)，bool

    def exclusive_n_mask(self, xyz: torch.Tensor, n: int):
        res = self.trained_grids.shape[0]  # Assuming trained_grids is a 4D tensor with shape (1, res, res, res)
        idx = (xyz * res).long().clamp(0, res - 1)
        x, y, z = idx[:, 0], idx[:, 1], idx[:, 2]

        values = self.trained_grids[x, y, z]
        bit_counts = self.popcount32(values)
        mask = (bit_counts == n)
        return mask

    def exclusive_n_grid(self, n: int):
        assert 1 <= n <= 32
        grid = self.trained_grids  # shape: (res, res, res), dtype=torch.int32
        bit_counts = self.popcount32(grid)  # shape: (res, res, res), dtype=torch.int32
        mask = (bit_counts == n)  # shape: (res, res, res), dtype=torch.bool
        return mask

    def overlapped_grid(self):
        grid = self.trained_grids  # shape: (res, res, res), dtype=torch.int32
        bit_counts = self.popcount32(grid)  # 每个 voxel 有多少个 bit 被设置
        max_bits = bit_counts.max()  # 当前最大 bit 数
        mask = (bit_counts == max_bits)  # 哪些 voxel 的 bit 数是最大值
        return mask

    def empty_grid(self):
        return self.trained_grids == 0

    def occupied_grid(self):
        return self.trained_grids != 0

    @staticmethod
    def popcount32(x: torch.Tensor) -> torch.Tensor:
        """
        Bit-parallel population count for int32 tensor.
        Input: x (torch.int32 tensor)
        Output: int32 tensor of same shape, each value is the number of 1s in x[i].
        """
        x = x - ((x >> 1) & 0x55555555)
        x = (x & 0x33333333) + ((x >> 2) & 0x33333333)
        x = (x + (x >> 4)) & 0x0F0F0F0F
        x = (x * 0x01010101) >> 24
        return x


class SparseLoss(PluginLoss):
    def __init__(self, max_level: int, delay_iters: int, name: str = 'sparse_loss'):
        super().__init__(name=name)
        assert max_level < 4, "max_level should be less than 4, as the maximum level in EPINF is 3."

        self.max_level = max_level
        self.sparse_loss = None
        self.delay_iters = delay_iters
        self.total_iters = 0

    def reset_plugin(self, dtype, device):
        self.sparse_loss = torch.tensor(0.0, dtype=dtype, device=device)

    def compute(self, tsm: TrainSpace, xyz: torch.Tensor, sigma: torch.Tensor):
        self.total_iters += 1
        if self.total_iters < self.delay_iters:
            return

        assert self.sparse_loss is not None, "Sparse loss should be initialized before computing."

        for level in range(self.max_level):
            sparse_mask = tsm.exclusive_n_mask(xyz=xyz, n=level + 1)
            sigma_sparse = sigma[sparse_mask]
            if sigma_sparse.numel() > 0:
                sparse_loss = 10.0 ** (-level) * sigma_sparse.mean()
                self.sparse_loss += sparse_loss

    @property
    def loss(self):
        return self.sparse_loss


class CornerLoss(PluginLoss):
    def __init__(self, delay_iters: int, name: str = 'corner_loss'):
        super().__init__(name=name)
        self.corner_loss = None
        self.delay_iters = delay_iters
        self.total_iters = 0

    def reset_plugin(self, dtype, device):
        self.corner_loss = torch.tensor(0.0, dtype=dtype, device=device)

    @property
    def loss(self):
        return self.corner_loss

    def compute(self, tsm: TrainSpace, xyz: torch.Tensor, sigma: torch.Tensor):
        self.total_iters += 1
        if self.total_iters < self.delay_iters:
            return
        # TODO:


class ImageMaskLoss(PluginLoss):
    def __init__(self, name: str = 'image_mask_loss'):
        super().__init__(name=name)
        self.image_mask_loss = None

    @property
    def loss(self):
        return self.image_mask_loss

    def reset_plugin(self, dtype, device):
        self.image_mask_loss = torch.tensor(0.0, dtype=dtype, device=device)

    def compute(self, rgb_map, acc_map, pixels_mask, background_color):
        assert self.image_mask_loss is not None, "Image mask loss should be initialized before computing."
        masked_rgb_map = rgb_map[~pixels_mask]
        if masked_rgb_map.numel() > 0:
            masked_rgb_map = masked_rgb_map.view(-1, 3)
            background_color = background_color.view(1, 3)
            self.image_mask_loss += torch.mean(torch.sum((masked_rgb_map - background_color) ** 2, dim=-1))
        masked_acc_map = acc_map[~pixels_mask]
        if masked_acc_map.numel() > 0:
            masked_acc_map = masked_acc_map.view(-1)
            self.image_mask_loss += torch.mean(masked_acc_map)

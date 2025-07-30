import matplotlib.cm as cm
import torch

from .api import RendererAPI
from ..models.hyfluid import HyFluidModel
# ----- plugins -----
from ..plugins.velocity_loss import HyFluidVelocityLoss


class HyFluidRenderer(RendererAPI):
    def __init__(self,
                 num_sample_rays: int,
                 num_depth_samples: int,
                 num_importance_samples: int,
                 use_normalized_directions: bool,
                 chunk: int):
        super().__init__(
            num_sample_rays=num_sample_rays,
            num_depth_samples=num_depth_samples,
            num_importance_samples=num_importance_samples,
            use_normalized_directions=use_normalized_directions,
            chunk=chunk,
        )

        # ---------- PLUGINS ----------
        self.register_plugin(plugin=HyFluidVelocityLoss())
        # ---------- PLUGINS ----------

    def render_impl(self,
                    model: HyFluidModel,
                    rays_o: torch.Tensor,
                    rays_d: torch.Tensor,
                    nears: torch.Tensor,
                    fars: torch.Tensor,
                    pose_indices: torch.Tensor
                    ):
        num_sample_rays = rays_d.shape[0]

        xyz, z_vals = self.sample_points(
            rays_o=rays_o,
            rays_d=rays_d,
            nears=nears,
            fars=fars,
            num_depth_samples=self.num_depth_samples,
            use_perturb=model.training,
        )
        xyz_masked, mask = self.normalize_and_filter_xyz(xyz=xyz)
        view_dirs_masked = self.normalize_and_filter_view_dirs(view_dirs=rays_d, expand_shape=xyz.shape, mask=mask)

        if xyz_masked.numel() > 0:
            sigma_masked, geo_feat_masked, xyzt_encoded, xyzt_with_grad = model.sigma(xyz_masked)
            sigma = self.assemble_masked_tensor(mask, sigma_masked, (num_sample_rays, self.num_depth_samples, 1))

            rgb_masked = model.rgb(None, view_dirs_masked, geo_feat_masked)
            rgb = self.assemble_masked_tensor(mask, rgb_masked, (num_sample_rays, self.num_depth_samples, 3))  # shape: (num_sample_rays, num_depth_samples, 3)

            alpha = self.sigma_to_alpha(sigma=sigma, z_vals=z_vals)  # shape: (num_sample_rays, num_depth_samples)
            weights = self.alpha_to_weights(alpha=alpha)  # shape: (num_sample_rays, num_depth_samples)
            acc_map = self.weights_to_acc_map(weights=weights)  # shape: (num_sample_rays,)
            depth_map = self.weights_to_depth_map(weights=weights, z_vals=z_vals, nears=nears, fars=fars)  # shape: (num_sample_rays,)
            rgb_map = self.weights_to_rgb_map(weights=weights, rgb=rgb)  # shape: (num_sample_rays, 3)

            vel_masked = model.vel(xyz_masked)
            vel = self.assemble_masked_tensor(mask, vel_masked.detach(), (num_sample_rays, self.num_depth_samples, 3))
            vel_scalar = vel.norm(dim=-1, keepdim=False)  # shape: (num_sample_rays, num_depth_samples)
            alpha_vel = self.sigma_to_alpha(sigma=vel_scalar, z_vals=z_vals)  # shape: (num_sample_rays, num_depth_samples)
            weights_vel_scalar = self.alpha_to_weights(alpha=alpha_vel)  # shape: (num_sample_rays, num_depth_samples)
            vel_map = self.weights_to_rgb_map(weights=weights_vel_scalar, rgb=vel)  # shape: (num_sample_rays, 3)

            # 假设 vel_map 是 [H, W, 3] 的 tensor，表示每个像素的速度向量
            # Step 1: 计算速度大小（范数）
            magnitude = torch.norm(vel_map, dim=-1)  # [H, W]

            # Step 2: 归一化到 [0,1]，避免亮度差异太大
            magnitude_norm = (magnitude - magnitude.min()) / (magnitude.max() - magnitude.min() + 1e-8)  # [H, W]

            # Step 3: 映射到 colormap（如 'turbo', 'viridis', 'plasma'）
            colormap = cm.get_cmap('turbo')  # 你可以换成 viridis, jet, etc.
            colored_np = colormap(magnitude_norm.cpu().numpy())[..., :3]  # shape: [H, W, 3], numpy

            # Step 4: 转成 torch.Tensor 并送回 device
            vel_map = torch.from_numpy(colored_np).to(vel_map.device, dtype=vel_map.dtype)  # [H, W, 3]

            # ---------- PLUGINS ----------
            if self.training:
                self.tsm.update(xyz=xyz_masked, index=int(pose_indices[0].item()))
                hyfluid_velocity_losses = {v for v in self.plugins if isinstance(v, HyFluidVelocityLoss)}
                for hvl in hyfluid_velocity_losses:
                    hvl: HyFluidVelocityLoss
                    hvl.compute(
                        xyzt=xyzt_with_grad,
                        xyzt_encoded=xyzt_encoded,
                        sigma=sigma_masked,
                        vel=vel_masked,
                        fn=model.fn,
                    )
            # ---------- PLUGINS ----------
        else:
            rgb_map = torch.zeros_like(rays_d)  # shape: (num_sample_rays, 3)
            depth_map = torch.zeros_like(rays_d[..., 0])  # shape: (num_sample_rays,)
            acc_map = torch.zeros_like(rays_d[..., 0])  # shape: (num_sample_rays,)
            vel_map = torch.zeros_like(rays_d)  # shape: (num_sample_rays, 3)

        return {
            "rgb_map": rgb_map,
            "depth_map": depth_map,
            "acc_map": acc_map,
            "vel_map": vel_map,
        }

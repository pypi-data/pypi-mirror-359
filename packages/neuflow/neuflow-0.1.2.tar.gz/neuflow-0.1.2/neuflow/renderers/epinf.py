import torch

from .api import RendererAPI
from ..models.epinf import EPINFHybridModel
# ----- plugins -----
from ..plugins.train_sapce import SparseLoss, CornerLoss
from ..plugins.velocity_loss import VelocityLoss


class EPINFRenderer(RendererAPI):
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
        self.register_plugin(plugin=SparseLoss(max_level=3, delay_iters=300))
        self.register_plugin(plugin=CornerLoss(delay_iters=300))
        self.register_plugin(plugin=VelocityLoss())
        # ---------- PLUGINS ----------

    def render_impl(self,
                    model: EPINFHybridModel,
                    rays_o: torch.Tensor,
                    rays_d: torch.Tensor,
                    nears: torch.Tensor,
                    fars: torch.Tensor,
                    pose_indices: torch.Tensor,
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
            sigma_static_masked, geo_feat_static_masked = model.static_renderer.sigma(xyz_masked)
            sigma_dynamic_masked, geo_feat_dynamic_masked = model.dynamic_renderer.sigma(xyz_masked)
            sigma_static = self.assemble_masked_tensor(mask, sigma_static_masked, (num_sample_rays, self.num_depth_samples, 1))  # shape: (num_sample_rays, num_depth_samples, 1)
            sigma_dynamic = self.assemble_masked_tensor(mask, sigma_dynamic_masked, (num_sample_rays, self.num_depth_samples, 1))  # shape: (num_sample_rays, num_depth_samples, 1)

            rgb_static_masked = model.static_renderer.rgb(None, view_dirs_masked, geo_feat_static_masked)
            rgb_dynamic_masked = model.dynamic_renderer.rgb(None, view_dirs_masked, geo_feat_dynamic_masked)
            rgb_static = self.assemble_masked_tensor(mask, rgb_static_masked, (num_sample_rays, self.num_depth_samples, 3))  # shape: (num_sample_rays, num_depth_samples, 3)
            rgb_dynamic = self.assemble_masked_tensor(mask, rgb_dynamic_masked, (num_sample_rays, self.num_depth_samples, 3))  # shape: (num_sample_rays, num_depth_samples, 3)

            alpha_static = self.sigma_to_alpha(sigma=sigma_static, z_vals=z_vals)  # shape: (num_sample_rays, num_depth_samples)
            alpha_dynamic = self.sigma_to_alpha(sigma=sigma_dynamic, z_vals=z_vals)  # shape: (num_sample_rays, num_depth_samples)
            alpha_hybrid = 1 - (1.0 - alpha_static) * (1.0 - alpha_dynamic)  # shape: (num_sample_rays, num_depth_samples)

            eps = torch.finfo(alpha_hybrid.dtype).eps
            transmittance_hybrid = torch.cumprod(
                torch.cat([torch.ones_like(alpha_hybrid[:, :1]), 1. - alpha_hybrid + eps], dim=-1),
                dim=-1,
            )[:, :-1]  # shape: (num_sample_rays, num_depth_samples)
            weights_static = alpha_static * transmittance_hybrid  # shape: (num_sample_rays, num_depth_samples)
            weights_dynamic = alpha_dynamic * transmittance_hybrid  # shape: (num_sample_rays, num_depth_samples)

            acc_map = self.weights_to_acc_map(weights=weights_static) + self.weights_to_acc_map(weights=weights_dynamic)  # shape: (num_sample_rays,)
            depth_map = self.weights_to_depth_map(weights=weights_static, z_vals=z_vals, nears=nears, fars=fars) + self.weights_to_depth_map(weights=weights_dynamic, z_vals=z_vals, nears=nears, fars=fars)  # shape: (num_sample_rays,)
            rgb_map = self.weights_to_rgb_map(weights=weights_static, rgb=rgb_static) + self.weights_to_rgb_map(weights=weights_dynamic, rgb=rgb_dynamic)  # shape: (num_sample_rays, 3)
            rgb_map = rgb_map + (1 - acc_map).unsqueeze(-1) * self.tsm.background_color.to(rgb_map.dtype).to(rgb_map.device)

            weights_static_independent = self.alpha_to_weights(alpha=alpha_static)
            acc_map_static_independent = self.weights_to_acc_map(weights=weights_static_independent)
            depth_map_static_independent = self.weights_to_depth_map(weights=weights_static_independent, z_vals=z_vals, nears=nears, fars=fars)
            rgb_map_static_independent = self.weights_to_rgb_map(weights=weights_static_independent, rgb=rgb_static)
            rgb_map_static_independent = rgb_map_static_independent + (1 - acc_map_static_independent).unsqueeze(-1) * self.tsm.background_color.to(rgb_map.dtype).to(rgb_map.device)

            weights_dynamic_independent = self.alpha_to_weights(alpha=alpha_dynamic)
            acc_map_dynamic_independent = self.weights_to_acc_map(weights=weights_dynamic_independent)
            depth_map_dynamic_independent = self.weights_to_depth_map(weights=weights_dynamic_independent, z_vals=z_vals, nears=nears, fars=fars)
            rgb_map_dynamic_independent = self.weights_to_rgb_map(weights=weights_dynamic_independent, rgb=rgb_dynamic)
            rgb_map_dynamic_independent = rgb_map_dynamic_independent + (1 - acc_map_dynamic_independent).unsqueeze(-1) * self.tsm.background_color.to(rgb_map.dtype).to(rgb_map.device)

            # ---------- PLUGINS ----------
            if self.training:
                self.tsm.update(xyz=xyz_masked, index=int(pose_indices[0].item()))
                sparse_losses = {v for v in self.plugins if isinstance(v, SparseLoss)}
                for sl in sparse_losses:
                    sl: SparseLoss
                    sl.compute(tsm=self.tsm, xyz=xyz_masked, sigma=sigma_static_masked + sigma_dynamic_masked)
            # ---------- PLUGINS ----------

        else:
            rgb_map = torch.zeros_like(rays_d)  # shape: (num_sample_rays, 3)
            depth_map = torch.zeros_like(rays_d[..., 0])  # shape: (num_sample_rays,)
            acc_map = torch.zeros_like(rays_d[..., 0])  # shape: (num_sample_rays,)
            rgb_map_static_independent = torch.zeros_like(rays_d)  # shape: (num_sample_rays, 3)
            depth_map_static_independent = torch.zeros_like(rays_d[..., 0])  # shape: (num_sample_rays,)
            acc_map_static_independent = torch.zeros_like(rays_d[..., 0])  # shape: (num_sample_rays,)
            rgb_map_dynamic_independent = torch.zeros_like(rays_d)  # shape: (num_sample_rays, 3)
            depth_map_dynamic_independent = torch.zeros_like(rays_d[..., 0])  # shape: (num_sample_rays,)
            acc_map_dynamic_independent = torch.zeros_like(rays_d[..., 0])  # shape: (num_sample_rays,)

        return {
            "rgb_map": rgb_map,
            "depth_map": depth_map,
            "acc_map": acc_map,
            'rgb_map_static_independent': rgb_map_static_independent,
            'depth_map_static_independent': depth_map_static_independent,
            'acc_map_static_independent': acc_map_static_independent,
            'rgb_map_dynamic_independent': rgb_map_dynamic_independent,
            'depth_map_dynamic_independent': depth_map_dynamic_independent,
            'acc_map_dynamic_independent': acc_map_dynamic_independent,
        }

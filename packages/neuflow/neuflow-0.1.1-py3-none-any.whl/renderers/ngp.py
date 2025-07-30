import torch

from .api import RendererAPI
from ..models.ngp import NGPModel


def sample_pdf(bins, weights, n_samples, det=False):
    # This implementation is from NeRF
    # bins: [B, T], old_z_vals
    # weights: [B, T - 1], bin weights.
    # return: [B, n_samples], new_z_vals

    # Get pdf
    weights = weights + 1e-5  # prevent nans
    pdf = weights / torch.sum(weights, -1, keepdim=True)
    cdf = torch.cumsum(pdf, -1)
    cdf = torch.cat([torch.zeros_like(cdf[..., :1]), cdf], -1)
    # Take uniform samples
    if det:
        u = torch.linspace(0. + 0.5 / n_samples, 1. - 0.5 / n_samples, steps=n_samples).to(weights.dtype).to(weights.device)
        u = u.expand(list(cdf.shape[:-1]) + [n_samples])
    else:
        u = torch.rand(list(cdf.shape[:-1]) + [n_samples]).to(weights.dtype).to(weights.device)

    # Invert CDF
    u = u.contiguous()
    inds = torch.searchsorted(cdf, u, right=True)
    below = torch.max(torch.zeros_like(inds - 1), inds - 1)
    above = torch.min((cdf.shape[-1] - 1) * torch.ones_like(inds), inds)
    inds_g = torch.stack([below, above], -1)  # (B, n_samples, 2)

    matched_shape = [inds_g.shape[0], inds_g.shape[1], cdf.shape[-1]]
    cdf_g = torch.gather(cdf.unsqueeze(1).expand(matched_shape), 2, inds_g)
    bins_g = torch.gather(bins.unsqueeze(1).expand(matched_shape), 2, inds_g)

    denom = (cdf_g[..., 1] - cdf_g[..., 0])
    denom = torch.where(denom < 1e-5, torch.ones_like(denom), denom)
    t = (u - cdf_g[..., 0]) / denom
    samples = bins_g[..., 0] + t * (bins_g[..., 1] - bins_g[..., 0])

    return samples


class NGPRenderer(RendererAPI):
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

    def render_impl(self,
                    model: NGPModel,
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

        if xyz_masked.numel() > 0:
            sigma_masked, geo_feat_masked = model.sigma(xyz_masked)
            sigma = self.assemble_masked_tensor(mask, sigma_masked, (num_sample_rays, self.num_depth_samples, 1))  # shape: (num_sample_rays, num_depth_samples, 1)

            if self.num_importance_samples > 0 and self.training:
                geo_feat = self.assemble_masked_tensor(mask, geo_feat_masked, (num_sample_rays, self.num_depth_samples, model.geo_feat_dim))  # shape: (num_sample_rays, num_depth_samples, geo_feat_dim)
                with torch.no_grad():
                    alpha = self.sigma_to_alpha(sigma=sigma, z_vals=z_vals)  # shape: (num_sample_rays, num_depth_samples)
                    weights = self.alpha_to_weights(alpha=alpha)  # shape: (num_sample_rays, num_depth_samples)
                    new_z_vals = sample_pdf(0.5 * (z_vals.squeeze(-1)[..., 1:] + z_vals.squeeze(-1)[..., :-1]), weights[:, 1:-1], self.num_importance_samples, det=not self.training).detach()  # shape: (num_sample_rays, num_importance_samples)
                    new_xyz = rays_o.unsqueeze(-2) + rays_d.unsqueeze(-2) * new_z_vals.unsqueeze(-1)  # shape: (num_sample_rays, num_importance_samples, 3)
                    new_xyz_masked, new_mask = self.normalize_and_filter_xyz(xyz=new_xyz)

                # override z_vals, and prepare z_index
                z_vals = torch.cat([z_vals.squeeze(-1), new_z_vals], dim=1)  # shape: (num_sample_rays, num_depth_samples + num_importance_samples,)
                z_vals, z_index = torch.sort(z_vals, dim=1)  # shape: (num_sample_rays, num_depth_samples + num_importance_samples,)
                z_vals = z_vals.unsqueeze(-1)  # shape: (num_sample_rays, num_depth_samples + num_importance_samples, 1)

                # override xyz
                xyz = torch.cat([xyz, new_xyz], dim=1)  # shape: (num_sample_rays, num_depth_samples + num_importance_samples, 3)
                xyz = torch.gather(xyz, dim=1, index=z_index.unsqueeze(-1).expand_as(xyz))  # shape: (num_sample_rays, num_depth_samples + num_importance_samples, 3)

                # override mask
                mask = torch.cat([mask.reshape(num_sample_rays, self.num_depth_samples), new_mask.reshape(num_sample_rays, self.num_importance_samples)], dim=1)
                mask = torch.gather(mask, dim=1, index=z_index)  # shape: (num_sample_rays, num_depth_samples + num_importance_samples)
                mask = mask.flatten()

                # override sigma_masked and geo_feat_masked
                new_sigma_masked, new_geo_feat_masked = model.sigma(new_xyz_masked)  # shape: (num_sample_rays * num_importance_samples, 1), (num_sample_rays * num_importance_samples, geo_feat_dim)
                new_sigma = self.assemble_masked_tensor(new_mask, new_sigma_masked, (num_sample_rays, self.num_importance_samples, 1))  # shape: (num_sample_rays, num_importance_samples, 1)
                tmp_sigma = torch.cat([sigma, new_sigma], dim=1)  # shape: (num_sample_rays, num_depth_samples + num_importance_samples, 1)
                sigma = torch.gather(tmp_sigma, dim=1, index=z_index.unsqueeze(-1).expand_as(tmp_sigma))  # shape: (num_sample_rays, num_depth_samples + num_importance_samples, 1)

                new_geo_feat = self.assemble_masked_tensor(new_mask, new_geo_feat_masked, (num_sample_rays, self.num_importance_samples, model.geo_feat_dim))  # shape: (num_sample_rays, num_importance_samples, geo_feat_dim)
                tmp_geo_feat = torch.cat([geo_feat, new_geo_feat], dim=1)  # shape: (num_sample_rays, num_depth_samples + num_importance_samples, geo_feat_dim)
                geo_feat = torch.gather(tmp_geo_feat, dim=1, index=z_index.unsqueeze(-1).expand_as(tmp_geo_feat))  # shape: (num_sample_rays, num_depth_samples + num_importance_samples, geo_feat_dim)
                geo_feat_masked = geo_feat.reshape(-1, model.geo_feat_dim)[mask]  # shape: (num_valid_points + new_num_valid_points, geo_feat_dim)

            view_dirs_masked = self.normalize_and_filter_view_dirs(view_dirs=rays_d, expand_shape=xyz.shape, mask=mask)
            rgb_masked = model.rgb(None, view_dirs_masked, geo_feat_masked)
            rgb = self.assemble_masked_tensor(mask, rgb_masked, xyz.shape)  # shape: (num_sample_rays, num_depth_samples + num_importance_samples, 3)

            alpha = self.sigma_to_alpha(sigma=sigma, z_vals=z_vals)  # shape: (num_sample_rays, num_depth_samples + num_importance_samples,)
            weights = self.alpha_to_weights(alpha=alpha)  # shape: (num_sample_rays, num_depth_samples + num_importance_samples,)
            acc_map = self.weights_to_acc_map(weights=weights)  # shape: (num_sample_rays,)
            depth_map = self.weights_to_depth_map(weights=weights, z_vals=z_vals, nears=nears, fars=fars)  # shape: (num_sample_rays,)
            rgb_map = self.weights_to_rgb_map(weights=weights, rgb=rgb)  # shape: (num_sample_rays, 3)
        else:
            acc_map = torch.zeros_like(rays_d[..., 0])  # shape: (num_sample_rays,)
            depth_map = torch.zeros_like(rays_d[..., 0])  # shape: (num_sample_rays,)
            rgb_map = torch.zeros_like(rays_d)  # shape: (num_sample_rays, 3)

        rgb_map = rgb_map + (1 - acc_map).unsqueeze(-1) * self.tsm.background_color.to(rgb_map.dtype).to(rgb_map.device)

        return {
            "rgb_map": rgb_map,
            "depth_map": depth_map,
            "acc_map": acc_map,
        }

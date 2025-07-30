import dataclasses
import glob
import os
import typing

import lightning
import torch
import torchmetrics
import torchvision.utils

from .datasets.api import PIDatasetAPI
from .gui import BasicGUI, OrbitCameraGUI
from .models.epinf import EPINFHybridModel
from .plugins.api import PluginLoss
from .renderers.epinf import EPINFRenderer


@dataclasses.dataclass
class EPINFConfig:
    name: str = dataclasses.field(default='EPINF', metadata={'help': 'name of the model'})
    lrate: float = dataclasses.field(default=1e-3, metadata={'help': 'learning rate for the optimizer'})

    # dataset parameters
    dataset: typing.Literal['sphere', 'game', 'scalar', 'torch', 'torch_avo', 'torch2', 'torch2_avo'] = dataclasses.field(default='sphere', metadata={'help': 'dataset name'})

    # model parameters
    num_layers_sigma: int = dataclasses.field(default=3, metadata={'help': 'number of layers for the sigma network'})
    hidden_dim_sigma: int = dataclasses.field(default=64, metadata={'help': 'hidden dimension for the sigma network'})
    num_layers_rgb: int = dataclasses.field(default=3, metadata={'help': 'number of layers for the RGB network'})
    hidden_dim_rgb: int = dataclasses.field(default=64, metadata={'help': 'hidden dimension for the RGB network'})
    num_layers_vel_sigma: int = dataclasses.field(default=3, metadata={'help': 'number of layers for the velocity sigma network'})
    hidden_dim_vel_sigma: int = dataclasses.field(default=64, metadata={'help': 'hidden dimension for the velocity sigma network'})
    geo_feat_dim: int = dataclasses.field(default=32, metadata={'help': 'geometric feature dimension'})
    num_layers_bg: int = dataclasses.field(default=3, metadata={'help': 'number of layers for the background network'})
    hidden_dim_bg: int = dataclasses.field(default=64, metadata={'help': 'hidden dimension for the background network'})
    use_background: bool = dataclasses.field(default=False, metadata={'help': 'whether to use background in the dataset'})

    # renderer parameters
    num_sample_rays: int = dataclasses.field(default=1024 * 2, metadata={'help': 'number of rays to sample per batch'})
    num_depth_samples: int = dataclasses.field(default=64, metadata={'help': 'number of depth samples per ray'})
    num_importance_samples: int = dataclasses.field(default=64, metadata={'help': 'number of importance samples per ray'})
    use_normalized_directions: bool = dataclasses.field(default=True, metadata={'help': 'whether to use normalized directions for rendering'})
    chunk: int = dataclasses.field(default=1024 * 2, metadata={'help': 'chunk size for rendering'})

    # training parameters
    fading_step: int = dataclasses.field(default=3000, metadata={'help': 'step at which the static fading starts'})
    val_output: bool = dataclasses.field(default=False, metadata={'help': 'whether to output validation images'})
    export_sigmas: bool = dataclasses.field(default=False, metadata={'help': 'whether to export sigmas during validation'})
    gui: typing.Literal['none', 'validation', 'orbit_camera'] = dataclasses.field(default='none', metadata={'help': 'type of GUI to use'})


class EPINFTrainer(lightning.LightningModule):
    def __init__(self, cfg: EPINFConfig):
        super().__init__()
        self.save_hyperparameters()
        self.model = EPINFHybridModel(
            num_layers_sigma=cfg.num_layers_sigma,
            hidden_dim_sigma=cfg.hidden_dim_sigma,
            num_layers_rgb=cfg.num_layers_rgb,
            hidden_dim_rgb=cfg.hidden_dim_rgb,
            geo_feat_dim=cfg.geo_feat_dim,
            num_layers_bg=cfg.num_layers_bg,
            hidden_dim_bg=cfg.hidden_dim_bg,
            use_background=cfg.use_background,
        )
        self.renderer = EPINFRenderer(
            num_sample_rays=cfg.num_sample_rays,
            num_depth_samples=cfg.num_depth_samples,
            num_importance_samples=cfg.num_importance_samples,
            use_normalized_directions=cfg.use_normalized_directions,
            chunk=cfg.chunk,
        )
        self.psnr = torchmetrics.image.PeakSignalNoiseRatio(data_range=1.0)
        self.ssim = torchmetrics.image.StructuralSimilarityIndexMeasure(data_range=1.0)
        self.lpips = torchmetrics.image.lpip.LearnedPerceptualImagePatchSimilarity(net_type='vgg')
        if cfg.gui == 'validation':
            self.gui = BasicGUI()
        elif cfg.gui == 'orbit_camera':
            self.gui = OrbitCameraGUI(radius=3.0)
        else:
            self.gui = None
        self.cfg: EPINFConfig = cfg
        self.model_only_iter = 1

    def on_fit_start(self):
        dataset: PIDatasetAPI = self.trainer.datamodule
        self.renderer.tsm.set_aabb_std(dataset.aabb_std)
        self.renderer.tsm.set_bound_std(dataset.bound_std)
        self.renderer.tsm.set_background_color(dataset.background_color)

    def on_train_batch_start(self, batch, batch_idx):
        self.model.set_time(batch['times'])

    def training_step(self, batch, batch_idx):
        result_maps, pixels, pixels_mask = self.renderer(
            model=self.model,
            poses=batch['poses'],
            pose_indices=batch['pose_indices'],
            focals=batch['focals'],
            images=batch['images'],
            images_masks=batch['images_masks'] if 'images_masks' in batch else None,
        )
        rgb_map = result_maps['rgb_map']
        img_loss = torch.nn.functional.mse_loss(rgb_map, pixels[..., :3])
        loss = img_loss
        self.log("img_loss", img_loss, on_step=True, on_epoch=False, prog_bar=True)

        plugin_losses = {v for v in self.renderer.plugins if isinstance(v, PluginLoss)}
        for plugin_loss in plugin_losses:
            loss += plugin_loss.loss
            self.log(f"{plugin_loss.name}", plugin_loss.loss, on_step=True, on_epoch=False, prog_bar=True)

        if 'rgb_map_static_independent' in result_maps:
            tempo_fading = min(max(self.global_step / self.cfg.fading_step, 0.0), 1.0)
            img_loss_static = torch.nn.functional.mse_loss(result_maps['rgb_map_static_independent'], pixels[..., :3])
            img_static_loss = tempo_fading * img_loss + (1 - tempo_fading) * img_loss_static
            loss += img_static_loss
            self.log("img_static_loss", img_static_loss, on_step=True, on_epoch=False, prog_bar=True)

        self.log("loss", loss, on_step=True, on_epoch=False, prog_bar=True)
        return loss

    def on_train_batch_end(self, outputs, batch, batch_idx):
        if self.cfg.gui == 'validation':
            self.gui.update_gui(None)
        elif self.cfg.gui == 'orbit_camera':
            if batch_idx % 10 == 0:  # 每10个batch更新一次GUI
                with torch.no_grad():
                    self.eval()
                    pose, width, height = self.gui.get_camera_intrinsics(dtype=batch['poses'].dtype, device=batch['poses'].device)
                    self.renderer.width_user = width
                    self.renderer.height_user = height
                    result_maps, pixels = self.renderer(
                        model=self.model,
                        poses=pose.unsqueeze(0),
                        pose_indices=None,
                        focals=batch['focals'],
                        images=None,
                        images_masks=None,
                    )
                    final_map = self.generate_map(result_maps, pixels)
                    self.gui.update_gui(render_buffer=final_map.to(torch.float32).cpu().numpy())
                    self.train()
        # if self.global_step == 500:
        #     self.renderer.tsm.export(export_path=self.logger.log_dir)

    def on_validation_batch_start(self, batch, batch_idx, dataloader_idx=0):
        self.model.set_time(batch['times'])

    def validation_step(self, batch, batch_idx):
        result_maps, pixels, pixels_mask = self.renderer(
            model=self.model,
            poses=batch['poses'],
            pose_indices=batch['pose_indices'] if 'pose_indices' in batch else None,
            focals=batch['focals'],
            images=batch['images'],
            images_masks=batch['images_masks'] if 'images_masks' in batch else None,
        )
        val_loss = torch.nn.functional.mse_loss(result_maps['rgb_map'], pixels[..., :3])
        self.log("val_loss", val_loss, on_step=False, on_epoch=True, prog_bar=True)
        psnr = self.psnr(result_maps['rgb_map'], pixels[..., :3])
        self.log("val_psnr", psnr, on_step=False, on_epoch=True, prog_bar=True)
        ssim = self.ssim(result_maps['rgb_map'].permute(0, 3, 1, 2), pixels[..., :3].permute(0, 3, 1, 2))  # 如果是 HWC 格式，需转为 NCHW
        self.log("val_ssim", ssim, on_step=False, on_epoch=True, prog_bar=True)
        lpips = self.lpips(result_maps['rgb_map'].permute(0, 3, 1, 2), pixels[..., :3].permute(0, 3, 1, 2))
        self.log("val_lpips", lpips, on_step=False, on_epoch=True, prog_bar=True)

        if self.cfg.val_output or self.cfg.gui == 'validation':
            final_map = self.generate_map(result_maps, pixels, pixels_mask)
            if self.cfg.val_output:
                os.makedirs(os.path.join(self.logger.log_dir, 'validation_images'), exist_ok=True)
                torchvision.utils.save_image(final_map.permute(2, 0, 1), os.path.join(self.logger.log_dir, 'validation_images', f'{self.current_epoch}_{batch_idx}.png'))
            if self.cfg.gui == 'validation':
                self.gui.update_gui(final_map.to(torch.float32).cpu().numpy())

        return val_loss

    def on_test_start(self):
        os.makedirs(os.path.join(self.logger.log_dir, 'test_images'), exist_ok=True)

    def test_step(self, batch, batch_idx):
        self.model.set_time(batch['times'])
        result_maps, pixels, pixels_mask = self.renderer(
            model=self.model,
            poses=batch['poses'],
            pose_indices=batch['pose_indices'] if 'pose_indices' in batch else None,
            focals=batch['focals'],
            images=batch['images'],
            images_masks=batch['images_masks'] if 'images_masks' in batch else None,
        )
        final_map = self.generate_map(result_maps, pixels, pixels_mask)
        psnr = self.psnr(result_maps['rgb_map'], pixels[..., :3])
        self.log("test_psnr", psnr, on_step=False, on_epoch=True, prog_bar=True)
        ssim = self.ssim(result_maps['rgb_map'].permute(0, 3, 1, 2), pixels[..., :3].permute(0, 3, 1, 2))  # 如果是 HWC 格式，需转为 NCHW
        self.log("test_ssim", ssim, on_step=False, on_epoch=True, prog_bar=True)
        lpips = self.lpips(result_maps['rgb_map'].permute(0, 3, 1, 2), pixels[..., :3].permute(0, 3, 1, 2))
        self.log("test_lpips", lpips, on_step=False, on_epoch=True, prog_bar=True)
        os.makedirs(os.path.join(self.logger.log_dir, 'test_images'), exist_ok=True)
        torchvision.utils.save_image(final_map.permute(2, 0, 1), os.path.join(self.logger.log_dir, 'test_images', f'{batch_idx}.png'))

    def on_test_end(self):
        image_dir = os.path.join(self.logger.log_dir, 'test_images')
        video_path = os.path.join(self.logger.log_dir, 'test_images', 'test_video.mp4')

        image_paths = sorted(
            glob.glob(os.path.join(image_dir, '*.png')),
            key=lambda x: int(os.path.basename(x).split('_')[-1].split('.')[0])
        )

        frames = []
        for path in image_paths:
            img = torchvision.io.read_image(path)  # (C, H, W), dtype=torch.uint8, range [0,255]
            if img.shape[0] == 1:
                img = img.expand(3, -1, -1)
            frames.append(img.permute(1, 2, 0))  # (H, W, C)

        video_tensor = torch.stack(frames, dim=0)  # (T, H, W, 3)
        torchvision.io.write_video(video_path, video_tensor, fps=24)
        print(f"✅ Video saved at {video_path}")

    def on_save_checkpoint(self, checkpoint):
        path = os.path.join(self.logger.log_dir, 'model_only', f'model_only_{self.model_only_iter}.ckpt')
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path), exist_ok=True)
        torch.save({
            "state_dict": self.model.state_dict(),
            'model_name': self.model.__class__.__name__,
            "tsm": self.renderer.tsm.state_dict(),
            'num_layers_sigma': self.cfg.num_layers_sigma,
            'hidden_dim_sigma': self.cfg.hidden_dim_sigma,
            'num_layers_rgb': self.cfg.num_layers_rgb,
            'hidden_dim_rgb': self.cfg.hidden_dim_rgb,
            'geo_feat_dim': self.cfg.geo_feat_dim,
            'num_layers_bg': self.cfg.num_layers_bg,
            'hidden_dim_bg': self.cfg.hidden_dim_bg,
            'use_background': self.cfg.use_background,
        }, path)
        print(f"✅ Model checkpoint saved at {path}")
        self.model_only_iter += 1

    def configure_optimizers(self):
        optimizer = torch.optim.Adam(params=self.parameters(), lr=self.cfg.lrate, eps=1e-15)
        scheduler = {
            "scheduler": torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.9, patience=3),
            "monitor": "loss",  # 告诉 Lightning 要监控哪个指标
            "interval": "epoch",  # 默认：每个 epoch 后更新一次
            "frequency": 1,
        }
        return {"optimizer": optimizer, "lr_scheduler": scheduler}

    @staticmethod
    def generate_map(result_maps, pixels, pixels_mask):
        rgb_map_column = torch.cat([rgb for rgb in result_maps['rgb_map']], dim=1)
        depth_map_column = torch.cat([rgb for rgb in result_maps['depth_map']], dim=1)
        acc_map_column = torch.cat([rgb for rgb in result_maps['acc_map']], dim=1)

        rgb_map_static_column = torch.cat([rgb for rgb in result_maps['rgb_map_static_independent']], dim=1)
        acc_map_static_column = torch.cat([rgb for rgb in result_maps['acc_map_static_independent']], dim=1)
        depth_map_static_column = torch.cat([rgb for rgb in result_maps['depth_map_static_independent']], dim=1)

        rgb_map_dynamic_column = torch.cat([rgb for rgb in result_maps['rgb_map_dynamic_independent']], dim=1)
        acc_map_dynamic_column = torch.cat([rgb for rgb in result_maps['acc_map_dynamic_independent']], dim=1)
        depth_map_dynamic_column = torch.cat([rgb for rgb in result_maps['depth_map_dynamic_independent']], dim=1)

        rgb_map_col = torch.cat([rgb_map_static_column, rgb_map_column, rgb_map_dynamic_column], dim=0)
        acc_map_col = torch.cat([acc_map_static_column, acc_map_column, acc_map_dynamic_column], dim=0)
        depth_map_col = torch.cat([depth_map_static_column, depth_map_column, depth_map_dynamic_column], dim=0)

        pixels_column = torch.cat([pixel for pixel in pixels[..., :3]], dim=1) if pixels is not None else torch.zeros_like(rgb_map_column)
        pixels_mask_column = torch.cat([mask for mask in pixels_mask.unsqueeze(-1)], dim=1) if pixels_mask is not None else torch.zeros_like(rgb_map_column)

        left_side = torch.cat([torch.zeros_like(pixels_column), pixels_column, pixels_mask_column.expand_as(pixels_column)], dim=0)
        right_side = torch.cat([rgb_map_col, acc_map_col.expand_as(rgb_map_col), depth_map_col.expand_as(rgb_map_col)], dim=1)

        final_map = torch.cat([left_side, right_side], dim=1)

        return final_map

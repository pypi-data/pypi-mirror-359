import json
import os
import typing

import rich.progress
import torch
import torchvision

from .api import PIDataset, PIDatasetAPI


class NeRFSynthetic(PIDataset):
    def __init__(self, dataset_path: str, dataset_type: typing.Literal['train', 'val', 'test'], downscale: int, use_fp16: bool):
        super().__init__()
        downscale = downscale if dataset_type == 'train' else downscale * 2

        with open(os.path.join(dataset_path, 'transforms_' + dataset_type + '.json'), 'r') as f:
            transform = json.load(f)
            images = []
            poses = []
            with rich.progress.Progress() as progress:
                task = progress.add_task(f"[cyan]Loading Images ({dataset_type})...", total=len(transform['frames']))
                for frame in transform['frames']:
                    frame_path = os.path.join(dataset_path, frame['file_path'] + '.png')
                    image = torchvision.io.read_image(path=str(frame_path)).permute(1, 2, 0) / 255.0  # (H, W, C)
                    images.append(image)
                    pose = torch.tensor(frame['transform_matrix'])
                    poses.append(pose)
                    progress.update(task, advance=1)
            images = torch.stack(images, dim=0)
            poses = torch.stack(poses, dim=0)
            N, H, W, C = images.shape
            if downscale != 1:
                H, W = H // downscale, W // downscale
                images = torch.nn.functional.interpolate(images.permute(0, 3, 1, 2), size=(H, W), mode='bilinear', align_corners=False).permute(0, 2, 3, 1)
            focal = W / (2 * torch.tan(torch.tensor(transform['camera_angle_x']) / 2))

        self._images = images.to(dtype=torch.float16 if use_fp16 else torch.float32)
        self._poses = poses.to(dtype=torch.float16 if use_fp16 else torch.float32)
        self._focal = focal.to(dtype=torch.float16 if use_fp16 else torch.float32)

        self._near = 0.1
        self._far = 5.0

    @property
    def images(self):
        return self._images

    @property
    def poses(self):
        return self._poses

    @property
    def focal(self):
        return self._focal

    @property
    def width(self):
        return self.images.shape[-2]

    @property
    def height(self):
        return self.images.shape[-3]

    @property
    def near(self):
        return self._near

    @property
    def far(self):
        return self._far

    @property
    def num_poses(self):
        return self.poses.shape[0]

    def transform(self, translate, scale):
        self._poses[:, :3, 3] = (self._poses[:, :3, 3] + torch.as_tensor(translate, dtype=self._poses.dtype, device=self._poses.device).view(1, 3)) * scale
        self._near = self._near * scale
        self._far = self._far * scale

    def __getitem__(self, index):
        return {
            'image': self.images[index],
            'pose': self.poses[index],
            'focal': self.focal,
            'index': index,
            'min_near': self.near,
            'max_far': self.far,
        }

    def __len__(self):
        return len(self.images)


class NeRFSyntheticDataset(PIDatasetAPI):
    def __init__(self, base_data_dir: str, dataset_name: str, downscale: int, use_fp16: bool):
        super().__init__(base_data_dir=base_data_dir, dataset_name=dataset_name, downscale=downscale, use_fp16=use_fp16)

    def prepare_data(self):
        from huggingface_hub import snapshot_download
        snapshot_download(
            repo_id="XayahHina/nerf_synthetic",
            repo_type="dataset",
            local_dir=self.base_data_dir,
        )
        if not os.path.exists(os.path.join(self.base_data_dir, "README.txt")):
            import zipfile
            with zipfile.ZipFile(os.path.join(self.base_data_dir, "nerf_synthetic.zip"), 'r') as zip_ref:
                zip_ref.extractall(os.path.join(self.base_data_dir))

    def setup(self, stage: str):
        self._background_color = [0.0, 0.0, 0.0]
        self._complex_background = False
        if "lego" in self.dataset_path.lower():
            self._pre_translate = [0.0, 0.0, 0.0]
            self._pre_scale = 0.8
            self._aabb_std = [-1.0, -1.0, -1.0, 1.0, 1.0, 1.0]
            self._bound_std = [-0.68, -1.0, -0.6, 0.68, 1.0, 1.0]
        else:
            raise ValueError(f"Unsupported dataset path: {self.dataset_path}")
        super().setup(stage)

    def dataset(self, dataset_type: typing.Literal['train', 'val', 'test']) -> PIDataset:
        dataset = NeRFSynthetic(dataset_path=self.dataset_path, dataset_type=dataset_type, downscale=self.downscale, use_fp16=self.use_fp16)
        dataset.transform(translate=self._pre_translate, scale=self._pre_scale)
        return dataset

    @staticmethod
    def collate(batch: list):
        images = torch.stack([single['image'] for single in batch])
        poses = torch.stack([single['pose'] for single in batch])
        focals = torch.tensor([single['focal'] for single in batch])
        pose_indices = torch.tensor([single['index'] for single in batch])
        min_nears = torch.tensor([single['min_near'] for single in batch]).to(poses.dtype)
        max_fars = torch.tensor([single['max_far'] for single in batch]).to(poses.dtype)

        return {
            'images': images,
            'images_masks': images[..., 3] > 0,
            'poses': poses,
            'focals': focals,
            'pose_indices': pose_indices,
            'min_nears': min_nears,
            'max_fars': max_fars,
        }

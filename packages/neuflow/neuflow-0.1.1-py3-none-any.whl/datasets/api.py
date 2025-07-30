import os
import typing

import lightning
import torch


class PIDataset(torch.utils.data.Dataset):
    @property
    def images(self):
        raise NotImplementedError("This method should be implemented in subclasses.")

    @property
    def poses(self):
        raise NotImplementedError("This method should be implemented in subclasses.")

    @property
    def focal(self):
        raise NotImplementedError("This method should be implemented in subclasses.")

    @property
    def width(self):
        raise NotImplementedError("This method should be implemented in subclasses.")

    @property
    def height(self):
        raise NotImplementedError("This method should be implemented in subclasses.")

    @property
    def near(self):
        raise NotImplementedError("This method should be implemented in subclasses.")

    @property
    def far(self):
        raise NotImplementedError("This method should be implemented in subclasses.")

    @property
    def num_poses(self):
        raise NotImplementedError("This method should be implemented in subclasses.")

    def transform(self, translate, scale):
        raise NotImplementedError("This method should be implemented in subclasses.")


class PIDatasetAPI(lightning.LightningDataModule):
    def __init__(self, base_data_dir: str, dataset_name: str, downscale: int, use_fp16: bool):
        super().__init__()
        self.base_data_dir = base_data_dir
        self.dataset_name = dataset_name
        self.downscale = downscale
        self.use_fp16 = use_fp16
        self._aabb_std = None
        self._bound_std = None
        self._background_color = None
        self._complex_background = None
        self._pre_translate = None
        self._pre_scale = None

        self.dataset_train = None
        self.dataset_val = None
        self.dataset_test = None

    def prepare_data(self):
        raise NotImplementedError("This method should be implemented in subclasses.")

    def setup(self, stage: str):
        if stage == 'fit':
            self.dataset_train = self.dataset('train')
            self.dataset_val = self.dataset('val')
        elif stage == 'validate':
            self.dataset_val = self.dataset('val')
        elif stage == 'test':
            self.dataset_test = self.dataset('test')
        else:
            raise NotImplementedError('Unsupported stage: {}'.format(stage))

    def dataset(self, dataset_type: typing.Literal['train', 'val', 'test']) -> PIDataset:
        raise NotImplementedError("This method should be implemented in subclasses.")

    @staticmethod
    def collate(batch: list):
        raise NotImplementedError("This method should be implemented in subclasses.")

    def train_dataloader(self):
        return torch.utils.data.DataLoader(
            self.dataset_train,
            batch_size=1,
            shuffle=True,
            num_workers=min(os.cpu_count() - 3, 4),
            persistent_workers=True,
            collate_fn=self.collate,
        )

    def val_dataloader(self):
        return torch.utils.data.DataLoader(
            self.dataset_val,
            batch_size=1,
            shuffle=False,
            num_workers=min(os.cpu_count() - 3, 4),
            persistent_workers=True,
            collate_fn=self.collate,
        )

    def test_dataloader(self):
        return torch.utils.data.DataLoader(
            self.dataset_test,
            batch_size=1,
            shuffle=False,
            num_workers=min(os.cpu_count() - 3, 4),
            persistent_workers=True,
            collate_fn=self.collate,
        )

    @property
    def dataset_path(self):
        return os.path.join(self.base_data_dir, self.dataset_name)

    @property
    def aabb_std(self):
        return self._aabb_std

    @property
    def bound_std(self):
        return self._bound_std

    @property
    def background_color(self):
        return self._background_color

    @property
    def complex_background(self):
        return self._complex_background

    @property
    def num_train_poses(self):
        assert self.dataset_train is not None, "Dataset for training is not set up."
        return self.dataset_train.num_poses

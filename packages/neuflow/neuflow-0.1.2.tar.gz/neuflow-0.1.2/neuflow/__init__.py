import dataclasses
import typing

from .datasets.nerf_synthetic import NeRFSyntheticDataset
from .datasets.pi_neuflow import PINeuFlowDataset
from .epinf import EPINFTrainer, EPINFConfig
from .hyfluid import HyFluidTrainer, HyFluidConfig
from .ngp import NGPTrainer, NGPConfig


@dataclasses.dataclass
class AppConfig:
    model: typing.Literal['ngp', 'dngp', 'hyfluid', 'epinf'] = dataclasses.field(default='ngp', metadata={'help': 'model name'})
    ngp: NGPConfig = dataclasses.field(default_factory=NGPConfig, metadata={'help': 'NGP model configuration'})
    hyfluid: HyFluidConfig = dataclasses.field(default_factory=HyFluidConfig, metadata={'help': 'HyFluid model configuration'})
    epinf: EPINFConfig = dataclasses.field(default_factory=EPINFConfig, metadata={'help': 'EPINF model configuration'})

    base_data_dir: str = dataclasses.field(default='data', metadata={'help': 'base data directory'})
    gpu_ids: typing.List[int] = dataclasses.field(default_factory=lambda: [0], metadata={'help': 'list of GPU IDs to use for training'})
    downscale: int = dataclasses.field(default=1, metadata={'help': 'downscale factor for the dataset images'})
    fp16: bool = dataclasses.field(default=True, metadata={'help': 'use mixed precision training'})
    gui: bool = dataclasses.field(default=False, metadata={'help': 'enable GUI for training and testing'})
    test: bool = dataclasses.field(default=False, metadata={'help': 'test mode, load a checkpoint and test the model'})


def create_trainer(cfg: AppConfig):
    if cfg.model == 'ngp':
        if cfg.gui:
            cfg.ngp.gui = 'validation'
        dataset = NeRFSyntheticDataset(
            base_data_dir=cfg.base_data_dir + '/nerf_synthetic/',
            dataset_name=cfg.ngp.dataset,
            downscale=cfg.downscale,
            use_fp16=cfg.fp16,
        )
        model = NGPTrainer(cfg=cfg.ngp)
    elif cfg.model == 'hyfluid':
        if cfg.gui:
            cfg.ngp.hyfluid = 'validation'
        dataset = PINeuFlowDataset(
            base_data_dir=cfg.base_data_dir + '/pi_neuflow/',
            dataset_name=cfg.hyfluid.dataset,
            downscale=cfg.downscale,
            use_fp16=cfg.fp16,
        )
        model = HyFluidTrainer(cfg=cfg.hyfluid)
    elif cfg.model == 'epinf':
        if cfg.gui:
            cfg.ngp.epinf = 'validation'
        dataset = PINeuFlowDataset(
            base_data_dir=cfg.base_data_dir + '/pi_neuflow/',
            dataset_name=cfg.epinf.dataset,
            downscale=cfg.downscale,
            use_fp16=cfg.fp16,
        )
        model = EPINFTrainer(cfg=cfg.epinf)
    else:
        raise NotImplementedError(f'Unsupported config type: {type(cfg)}')
    return model, dataset


def create_trainer_from_ckpt(cfg: AppConfig, ckpt_path: str):
    for ModelClass in [NGPTrainer]:
        try:
            model = ModelClass.load_from_checkpoint(ckpt_path)
            print(f"Successfully loaded model type: {ModelClass.__name__}")
            dataset = NeRFSyntheticDataset(
                base_data_dir=cfg.base_data_dir + '/nerf_synthetic/',
                dataset_name=model.cfg.dataset,
                downscale=cfg.downscale,
                use_fp16=cfg.fp16,
            )
            return model, dataset
        except RuntimeError:
            pass

    for ModelClass in [HyFluidTrainer, EPINFTrainer]:
        try:
            model = ModelClass.load_from_checkpoint(ckpt_path)
            print(f"Successfully loaded model type: {ModelClass.__name__}")
            dataset = PINeuFlowDataset(
                base_data_dir=cfg.base_data_dir + '/pi_neuflow/',
                dataset_name=model.cfg.dataset,
                downscale=cfg.downscale,
                use_fp16=cfg.fp16,
            )
            return model, dataset
        except RuntimeError:
            pass

    raise RuntimeError(f"Failed to load model from checkpoint: {ckpt_path}. ")


__all__ = ['AppConfig', 'create_trainer', 'create_trainer_from_ckpt']

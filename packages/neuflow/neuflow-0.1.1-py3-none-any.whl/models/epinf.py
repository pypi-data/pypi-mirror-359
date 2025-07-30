import math

import tinycudann
import torch

from .api import ModelAPI


class EPINFStaticModel(ModelAPI):
    def __init__(self,
                 num_layers_sigma: int,
                 hidden_dim_sigma: int,
                 num_layers_rgb: int,
                 hidden_dim_rgb: int,
                 geo_feat_dim: int,
                 num_layers_bg: int,
                 hidden_dim_bg: int,
                 use_background: bool,
                 ):
        super().__init__()

        bound = 1
        self.encoder_sigma = tinycudann.Encoding(
            n_input_dims=3,
            encoding_config={
                "otype": "HashGrid",
                "n_levels": 16,
                "n_features_per_level": 2,
                "log2_hashmap_size": 19,
                "base_resolution": 16,
                "per_level_scale": 2 ** (math.log2(2048 * bound / 16) / (16 - 1)),
            },
        )
        self.sigma_net = tinycudann.Network(
            n_input_dims=int(self.encoder_sigma.n_output_dims),
            n_output_dims=1 + geo_feat_dim,
            network_config={
                "otype": "FullyFusedMLP",
                "activation": "ReLU",
                "output_activation": "None",
                "n_neurons": hidden_dim_sigma,
                "n_hidden_layers": num_layers_sigma - 1,
            },
        )

        self.encoder_dir = tinycudann.Encoding(
            n_input_dims=3,
            encoding_config={
                "otype": "SphericalHarmonics",
                "degree": 4,
            },
        )
        self.color_net = tinycudann.Network(
            n_input_dims=int(self.encoder_dir.n_output_dims) + geo_feat_dim,
            n_output_dims=3,
            network_config={
                "otype": "FullyFusedMLP",
                "activation": "ReLU",
                "output_activation": "None",
                "n_neurons": hidden_dim_rgb,
                "n_hidden_layers": num_layers_rgb - 1,
            },
        )

        if use_background:
            self.encoder_bg = tinycudann.Encoding(
                n_input_dims=2,
                encoding_config={
                    "otype": "HashGrid",
                    "n_levels": 4,
                    "n_features_per_level": 2,
                    "log2_hashmap_size": 19,
                    "base_resolution": 16,
                    "per_level_scale": 2 ** (math.log2(2048 * bound / 4) / (4 - 1)),
                },
            )
            self.bg_net = tinycudann.Network(
                n_input_dims=int(self.encoder_dir.n_output_dims) + int(self.encoder_bg.n_output_dims),
                n_output_dims=3,
                network_config={
                    "otype": "FullyFusedMLP",
                    "activation": "ReLU",
                    "output_activation": "None",
                    "n_neurons": hidden_dim_bg,
                    "n_hidden_layers": num_layers_bg - 1,
                },
            )

    @property
    def is_sparse_view_model(self):
        return True

    def sigma(self, xyz):
        xyz_encoded = self.encoder_sigma(xyz)
        h = self.sigma_net(xyz_encoded)
        sigma = torch.nn.functional.relu(h[..., :1])
        geo_feat = h[..., 1:]
        return sigma, geo_feat

    def rgb(self, xyz, view_dirs, geo_feat, cond=None):
        view_dirs_encoded = self.encoder_dir(view_dirs)
        h = self.color_net(torch.cat([view_dirs_encoded, geo_feat], dim=-1))
        rgb = torch.sigmoid(h)
        return rgb

    def background(self, sph, view_dirs):
        sph_encoded = self.encoder_bg(sph)
        view_dirs_encoded = self.encoder_dir(view_dirs)
        h = self.bg_net(torch.cat([view_dirs_encoded, sph_encoded], dim=-1))
        rgb_bg = torch.sigmoid(h)
        return rgb_bg


class EPINFDynamicModel(ModelAPI):
    def __init__(self,
                 num_layers_sigma: int,
                 hidden_dim_sigma: int,
                 num_layers_rgb: int,
                 hidden_dim_rgb: int,
                 geo_feat_dim: int,
                 use_background: bool,
                 ):
        super().__init__()

        bound = 1
        self.encoder = tinycudann.Encoding(
            n_input_dims=4,
            encoding_config={
                "otype": "HashGrid",
                "n_levels": 16,
                "n_features_per_level": 2,
                "log2_hashmap_size": 19,
                "base_resolution": 16,
                "per_level_scale": 2 ** (math.log2(2048 * bound / 16) / (16 - 1)),
            },
        )

        self.sigma_net = tinycudann.Network(
            n_input_dims=int(self.encoder.n_output_dims),
            n_output_dims=1 + geo_feat_dim,
            network_config={
                "otype": "FullyFusedMLP",
                "activation": "ReLU",
                "output_activation": "None",
                "n_neurons": hidden_dim_sigma,
                "n_hidden_layers": num_layers_sigma - 1,
            },
        )

        self.encoder_dir = tinycudann.Encoding(
            n_input_dims=3,
            encoding_config={
                "otype": "SphericalHarmonics",
                "degree": 4,
            },
        )

        self.color_net = tinycudann.Network(
            n_input_dims=int(self.encoder_dir.n_output_dims) + geo_feat_dim,
            n_output_dims=3,
            network_config={
                "otype": "FullyFusedMLP",
                "activation": "ReLU",
                "output_activation": "None",
                "n_neurons": hidden_dim_rgb,
                "n_hidden_layers": num_layers_rgb - 1,
            },
        )

        self._time = None

    @property
    def is_sparse_view_model(self):
        return True

    @property
    def time(self):
        assert self._time is not None
        assert isinstance(self._time, torch.Tensor)
        assert self._time.shape[0] == 1
        return self._time

    def set_time(self, time):
        self._time = time

    def sigma(self, xyz):
        xyzt = torch.cat([xyz, self.time.unsqueeze(0).expand_as(xyz[..., :1])], dim=-1)
        xyzt_encoded = self.encoder(xyzt)
        h = self.sigma_net(xyzt_encoded)
        sigma = torch.nn.functional.relu(h[..., :1])
        geo_feat = h[..., 1:]
        return sigma, geo_feat

    def rgb(self, xyz, view_dirs, geo_feat, cond=None):
        view_dirs_encoded = self.encoder_dir(view_dirs)
        h = self.color_net(torch.cat([view_dirs_encoded, geo_feat], dim=-1))
        rgb = torch.sigmoid(h)
        return rgb

    def background(self, sph, view_dirs):
        raise NotImplementedError("Background rendering is not implemented for dynamic models.")


class EPINFHybridModel(ModelAPI):
    def __init__(self,
                 num_layers_sigma: int,
                 hidden_dim_sigma: int,
                 num_layers_rgb: int,
                 hidden_dim_rgb: int,
                 geo_feat_dim: int,
                 num_layers_bg: int,
                 hidden_dim_bg: int,
                 use_background: bool,
                 ):
        super().__init__()

        self.static_renderer = EPINFStaticModel(
            num_layers_sigma=num_layers_sigma,
            hidden_dim_sigma=hidden_dim_sigma,
            num_layers_rgb=num_layers_rgb,
            hidden_dim_rgb=hidden_dim_rgb,
            geo_feat_dim=geo_feat_dim,
            num_layers_bg=num_layers_bg,
            hidden_dim_bg=hidden_dim_bg,
            use_background=use_background,
        )

        self.dynamic_renderer = EPINFDynamicModel(
            num_layers_sigma=num_layers_sigma,
            hidden_dim_sigma=hidden_dim_sigma,
            num_layers_rgb=num_layers_rgb,
            hidden_dim_rgb=hidden_dim_rgb,
            geo_feat_dim=geo_feat_dim,
            use_background=use_background,
        )

    @property
    def is_sparse_view_model(self):
        return True

    @property
    def time(self):
        return self.dynamic_renderer.time

    def set_time(self, time):
        self.dynamic_renderer.set_time(time)

    def sigma(self, xyz):
        sigma_static, geo_feat_static = self.static_renderer.sigma(xyz)
        sigma_dynamic, geo_feat_dynamic = self.dynamic_renderer.sigma(xyz)
        return sigma_static + sigma_dynamic, geo_feat_static + geo_feat_dynamic

    def rgb(self, xyz, view_dirs, geo_feat, cond=None):
        raise NotImplementedError("Hybrid model does not support direct RGB rendering. Use static or dynamic renderer instead.")

    def background(self, sph, view_dirs):
        raise NotImplementedError("Background rendering is not implemented for hybrid models. Use static or dynamic renderer instead.")

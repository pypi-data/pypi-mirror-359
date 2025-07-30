import math

import tinycudann
import torch

from .api import ModelAPI


class NGPModel(ModelAPI):
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

        self.geo_feat_dim = geo_feat_dim

    @property
    def is_sparse_view_model(self):
        return False

    def forward(self, xyz, view_dirs):
        sigma, geo_feat = self.sigma(xyz)
        rgb = self.rgb(xyz, view_dirs, geo_feat)
        return sigma, rgb

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
        raise NotImplementedError("Background calculation is not implemented in NGPModel. This model does not support background rendering.")

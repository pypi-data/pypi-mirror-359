import math

import tinycudann
import torch

from .api import ModelAPI


class HyFluidModel(ModelAPI):
    def __init__(self,
                 num_layers_sigma: int,
                 hidden_dim_sigma: int,
                 num_layers_rgb: int,
                 hidden_dim_rgb: int,
                 geo_feat_dim: int,
                 num_layers_vel_sigma: int,
                 hidden_dim_vel_sigma: int,
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

        sigma_net = []
        for l in range(num_layers_sigma):
            if l == 0:
                in_dim = self.encoder.n_output_dims
            else:
                in_dim = hidden_dim_sigma
            if l == num_layers_sigma - 1:
                out_dim = 1 + geo_feat_dim
            else:
                out_dim = hidden_dim_sigma
            sigma_net.append(torch.nn.Linear(in_dim, out_dim, bias=False))
        self.sigma_net = torch.nn.ModuleList(sigma_net)

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

        self.encoder_vel = tinycudann.Encoding(
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

        self.sigma_vel_net = tinycudann.Network(
            n_input_dims=int(self.encoder_vel.n_output_dims),
            n_output_dims=3,
            network_config={
                "otype": "FullyFusedMLP",
                "activation": "ReLU",
                "output_activation": "None",
                "n_neurons": hidden_dim_vel_sigma,
                "n_hidden_layers": num_layers_vel_sigma - 1,
            },
        )

        self.num_layers_sigma = num_layers_sigma
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

    def fn(self, hidden):
        h = hidden
        for l in range(self.num_layers_sigma):
            h = self.sigma_net[l](h)
            if l != self.num_layers_sigma - 1:
                h = torch.nn.functional.relu(h, inplace=True)
        return torch.nn.functional.relu(h[..., :1])

    def sigma(self, xyz):
        xyzt = torch.cat([xyz, self.time.unsqueeze(0).expand_as(xyz[..., :1])], dim=-1)
        if self.training:
            xyzt.requires_grad = True
        xyzt_encoded = self.encoder(xyzt)

        h = xyzt_encoded
        for l in range(self.num_layers_sigma):
            h = self.sigma_net[l](h)
            if l != self.num_layers_sigma - 1:
                h = torch.nn.functional.relu(h, inplace=True)

        sigma = torch.nn.functional.relu(h[..., :1])
        geo_feat = h[..., 1:]
        return sigma, geo_feat, xyzt_encoded, xyzt

    def rgb(self, xyz, view_dirs, geo_feat, cond=None):
        view_dirs_encoded = self.encoder_dir(view_dirs)
        h = self.color_net(torch.cat([view_dirs_encoded, geo_feat], dim=-1))
        rgb = torch.sigmoid(h)
        return rgb

    def vel(self, xyz):
        xyzt = torch.cat([xyz, self.time.unsqueeze(0).expand_as(xyz[..., :1])], dim=-1)
        xyzt_encoded = self.encoder_vel(xyzt)
        velocity = self.sigma_vel_net(xyzt_encoded)
        return velocity

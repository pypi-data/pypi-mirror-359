import torch


class ModelAPI(torch.nn.Module):
    def __init__(self):
        super().__init__()

    @property
    def is_sparse_view_model(self):
        raise NotImplementedError("Sparse view model check is not implemented in the base API class. Please implement this method in a subclass.")

    def sigma(self, xyz):
        raise NotImplementedError("Sigma calculation is not implemented in the base API class. Please implement this method in a subclass.")

    def rgb(self, xyz, view_dirs, geo_feat, cond=None):
        raise NotImplementedError("RGB calculation is not implemented in the base API class. Please implement this method in a subclass.")

    def background(self, sph, view_dirs):
        raise NotImplementedError("Background calculation is not implemented in the base API class. Please implement this method in a subclass.")

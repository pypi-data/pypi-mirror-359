import torch


class Plugin(torch.nn.Module):
    def __init__(self, name: str):
        super().__init__()
        self._name = name

    @property
    def name(self):
        return self._name

    def reset_plugin(self, dtype, device):
        raise NotImplementedError("Subclasses should implement this method.")


class PluginLoss(Plugin):
    def __init__(self, name: str):
        super().__init__(name)

    @property
    def loss(self):
        raise NotImplementedError("Subclasses should implement this method.")

import torch

from .api import PluginLoss


class HyFluidVelocityLoss(PluginLoss):
    def __init__(self, name: str = "hyfluid_velocity_loss"):
        super().__init__(name=name)
        self.velocity_loss = None
        self.total_iters = 0
        self.skip_iters = 3
        self.warmup_iters = 0

    @property
    def loss(self):
        return self.velocity_loss

    def reset_plugin(self, dtype, device):
        self.velocity_loss = torch.tensor(0.0, dtype=dtype, device=device)

    @staticmethod
    def get_minibatch_jacobian(y, x):
        """Computes the Jacobian of y wrt x assuming minibatch-mode.
        Args:
          y: (N, ...) with a total of D_y elements in ...
          x: (N, ...) with a total of D_x elements in ...
        Returns:
          The minibatch Jacobian matrix of shape (N, D_y, D_x)
        """
        assert y.shape[0] == x.shape[0]
        y = y.view(y.shape[0], -1)
        # Compute Jacobian row by row.
        jac = []
        for j in range(y.shape[1]):
            dy_j_dx = torch.autograd.grad(
                y[:, j],
                x,
                torch.ones_like(y[:, j], device=y.get_device()),
                retain_graph=True,
                create_graph=True,
            )[0].view(x.shape[0], -1)

            jac.append(torch.unsqueeze(dy_j_dx, 1))
        jac = torch.cat(jac, 1)
        return jac

    def compute(self, xyzt, xyzt_encoded, sigma, vel, fn):
        self.total_iters += 1
        if self.total_iters % self.skip_iters != 0 and self.total_iters < self.warmup_iters:
            return

        split_nse_wei = 0.001

        jac = torch.vmap(torch.func.jacrev(fn))(xyzt_encoded)
        jac = jac.contiguous()
        jac_x = self.get_minibatch_jacobian(xyzt_encoded, xyzt)
        jac_x = jac_x.contiguous()
        jac = jac @ jac_x

        _d_x, _d_y, _d_z, _d_t = [torch.squeeze(_, -1) for _ in jac.split(1, dim=-1)]

        _u_x, _u_y, _u_z, _u_t = None, None, None, None
        _u, _v, _w = vel.split(1, dim=-1)
        split_nse = _d_t + (_u * _d_x + _v * _d_y + _w * _d_z)
        nse_errors = torch.mean(torch.square(split_nse))

        viz_dens_mask = sigma.detach() > 0.1
        vel_norm = vel.norm(dim=-1, keepdim=True)
        min_vel_mask = vel_norm.detach() < 0.2 * sigma.detach()
        vel_reg_mask = min_vel_mask & viz_dens_mask
        min_vel_reg_map = (0.2 * sigma - vel_norm) * vel_reg_mask.float()
        min_vel_reg = min_vel_reg_map.pow(2).mean()

        zero_dens_mask = sigma.detach() < 1e-3
        keep_zero_map = vel_norm * zero_dens_mask.float()
        proj_loss = split_nse_wei * keep_zero_map.pow(2).mean()

        self.velocity_loss += nse_errors + 10 * min_vel_reg + proj_loss


class VelocityLoss(PluginLoss):
    def __init__(self, name: str = "velocity_loss"):
        super().__init__(name=name)
        self.velocity_loss = None
        self.total_iters = 0

    @property
    def loss(self):
        return self.velocity_loss

    def reset_plugin(self, dtype, device):
        self.velocity_loss = torch.tensor(0.0, dtype=dtype, device=device)

    def compute(self):
        pass

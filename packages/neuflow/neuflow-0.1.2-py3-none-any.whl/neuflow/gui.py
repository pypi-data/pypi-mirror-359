import math

import dearpygui.dearpygui as dpg
import torch


class BasicGUI:
    def __init__(self):
        self.render_buffer = None

    def init_gui(self, render_buffer):
        W, H = render_buffer.shape[-2], render_buffer.shape[-3]
        self.render_buffer = render_buffer
        dpg.create_context()
        with dpg.texture_registry(show=False):
            dpg.add_raw_texture(W, H, self.render_buffer, format=dpg.mvFormat_Float_rgb, tag="_texture")
        with dpg.window(tag="_primary_window", width=W + 20, height=H + 70, no_scrollbar=True, no_title_bar=True):
            dpg.add_image("_texture", width=W, height=H)
        dpg.set_primary_window("_primary_window", True)
        dpg.create_viewport(title='Visualizer', width=W + 20, height=H + 70, resizable=True)
        dpg.setup_dearpygui()
        dpg.show_viewport()

    def update_gui(self, render_buffer):
        if self.render_buffer is None:
            self.init_gui(render_buffer)
        else:
            if render_buffer is not None:
                self.render_buffer = render_buffer
                dpg.set_value("_texture", self.render_buffer)
            else:
                dpg.render_dearpygui_frame()


class OrbitCamera:
    def __init__(self, width: int, height: int, radius: float, fovy_deg: float):
        self.width = width
        self.height = height
        self.radius = radius
        self.fovy = math.radians(fovy_deg)
        self.center = torch.tensor([0.0, 0.0, 0.0])

        # 初始旋转（绕y轴 azimuth，绕x轴 elevation）
        self.azimuth = 0.0  # 水平角度（绕y轴）
        self.elevation = 0.0  # 垂直角度（绕x轴）

    def pose(self):
        # 计算相机位置（spherical coordinates）
        x = self.radius * math.cos(self.elevation) * math.sin(self.azimuth)
        y = self.radius * math.sin(self.elevation)
        z = self.radius * math.cos(self.elevation) * math.cos(self.azimuth)
        eye = torch.tensor([x, y, z])

        # Look at center
        forward = (self.center - eye)
        forward = forward / forward.norm()
        up = torch.tensor([0.0, 1.0, 0.0])
        right = torch.linalg.cross(up, forward)
        right = right / right.norm()
        true_up = torch.linalg.cross(forward, right)

        # 构造旋转矩阵（列向量为 right, up, forward）
        R = torch.stack([right, true_up, -forward], dim=1)
        t = eye.view(3, 1)

        # [R | t] -> [4x4]
        pose = torch.eye(4)
        pose[:3, :3] = R
        pose[:3, 3] = t[:, 0]

        return pose

    def orbit(self, dx: float, dy: float):
        """绕物体旋转 dx, dy 为弧度偏移"""
        self.azimuth += dx
        self.elevation += dy

        # clamp elevation 避免翻转（不能超过 ±89°）
        self.elevation = max(-math.pi / 2 + 1e-4, min(math.pi / 2 - 1e-4, self.elevation))


class OrbitCameraGUI(BasicGUI):
    def __init__(self, width=400, height=400, radius=5.0, fovy_deg=45.0):
        super().__init__()
        self.camera = OrbitCamera(width=width, height=height, radius=radius, fovy_deg=fovy_deg)

    def get_camera_intrinsics(self, dtype: torch.dtype, device: torch.device):
        self.camera.azimuth += 0.1
        pose = self.camera.pose().to(dtype=dtype).to(device=device)
        return pose, self.camera.width, self.camera.height

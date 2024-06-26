from ultralytics import YOLO
import torch
from torch import nn


class Yolov8Model(nn.Module):
    def __init__(self, num_classes):
        super().__init__()
        # yolov8n-seg.torchscript
        self.model = YOLO("yolov8n-seg.pt")

    def forward(self, x):
        out = self.model(x)

        return torch.tensor(out, dtype=torch.float32)

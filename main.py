# From the dataset, create a train and test set
import torch
from torch.utils.data import DataLoader
import pytorch_lightning as pl

from unified_focal_loss import AsymmetricUnifiedFocalLoss

from torch.optim.lr_scheduler import ReduceLROnPlateau

from models.base import BaseModel
from models.architectures import (
    DeepLabModel,
    FCNResNetModel,
    MaskRCNNModel,
    Yolov8Model,
)

from dataloaders.solar_dk_dataset import SolarDKDataset
import torchvision.transforms.v2 as transforms

train_folder = "data/solardk_dataset_neurips_v2/gentofte_trainval/train"
validation_folder = "data/solardk_dataset_neurips_v2/gentofte_trainval/val"
test_folder = "data/solardk_dataset_neurips_v2/herlev_test/test"

train_transform = transforms.Compose(
    [
        transforms.ToDtype(torch.uint8),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomVerticalFlip(p=0.5),
    ]
)

test_transform = transforms.Compose(
    [
        transforms.ToDtype(torch.uint8),
    ]
)

# Apply the transformations to the dataset
train_dataset = SolarDKDataset(train_folder, transform=train_transform)
validation_dataset = SolarDKDataset(validation_folder, transform=test_transform)
test_dataset = SolarDKDataset(test_folder, transform=test_transform)

train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True, num_workers=4)
validation_loader = DataLoader(
    validation_dataset, batch_size=16, shuffle=False, num_workers=4
)
test_loader = DataLoader(test_dataset, batch_size=4, shuffle=False, num_workers=4)

model = DeepLabModel(num_classes=1, backbone="resnet50")
# model = FCNResNetModel(num_classes=1, backbone="resnet50")
# model = MaskRCNNModel(num_classes=1)
# model = Yolov8Model(num_classes=1)

treshold = 0.5
loss_fn = AsymmetricUnifiedFocalLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)
scheduler = ReduceLROnPlateau(optimizer, mode="min", factor=0.1, patience=10)

base_model = BaseModel(model, loss_fn, optimizer, scheduler, treshold)
trainer = pl.Trainer(
    strategy="ddp_find_unused_parameters_true",
    max_epochs=150,
    min_epochs=10,
    enable_checkpointing=True,
)

trainer.fit(
    base_model,
    train_loader,
    validation_loader,
)

trainer.test(base_model, test_loader)

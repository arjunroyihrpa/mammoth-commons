from torchvision.models import resnet
import torch

model = resnet.resnet18()
model.fc = torch.nn.Linear(model.fc.in_features, 2)

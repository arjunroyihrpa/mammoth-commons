import torch.nn as nn
import torch.nn.functional as F


class Cnn32_Small(nn.Module):
    def __init__(self, num_classes, input_channels):
        super(Cnn32_Small, self).__init__()
        self.conv1 = nn.Conv2d(input_channels, 8, kernel_size=3)
        self.conv1_bn = nn.BatchNorm2d(8)
        self.conv2 = nn.Conv2d(8, 16, kernel_size=3)
        self.conv2_bn = nn.BatchNorm2d(16)
        self.conv3 = nn.Conv2d(16, 32, kernel_size=3)
        self.conv3_bn = nn.BatchNorm2d(32)
        self.fc1 = nn.Linear(in_features=32 * 4, out_features=64)
        self.fc2 = nn.Linear(in_features=64, out_features=num_classes)

    def forward(self, x):
        out = F.relu(self.conv1_bn(self.conv1(x)))
        out = F.max_pool2d(out, 2)
        out = F.relu(self.conv2_bn(self.conv2(out)))
        out = F.max_pool2d(out, 2)
        out = F.relu(self.conv3_bn(self.conv3(out)))
        out = F.max_pool2d(out, 2)
        out = out.view(out.size(0), -1)
        out = F.relu(self.fc1(out))
        out = self.fc2(out)
        return out


model = Cnn32_Small(10, 3)

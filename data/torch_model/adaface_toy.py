import torch
import torch.nn as nn
import torch.nn.functional as F


class ToyCNN(nn.Module):
    def __init__(self):
        super(ToyCNN, self).__init__()

        # Define the layers of the CNN
        self.conv1 = nn.Conv2d(in_channels=3, out_channels=16, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(
            in_channels=16, out_channels=32, kernel_size=3, padding=1
        )
        self.conv3 = nn.Conv2d(
            in_channels=32, out_channels=64, kernel_size=3, padding=1
        )

        # Define a global average pooling layer to reduce spatial dimensions to 1x1
        self.global_avg_pool = nn.AdaptiveAvgPool2d(1)

    def forward(self, x):
        # Apply convolutional layers with ReLU activations and max pooling
        x = F.relu(self.conv1(x))
        x = F.max_pool2d(x, kernel_size=2)

        x = F.relu(self.conv2(x))
        x = F.max_pool2d(x, kernel_size=2)

        x = F.relu(self.conv3(x))
        x = F.max_pool2d(x, kernel_size=2)

        # Apply global average pooling (reduces spatial dimensions to 1x1)
        x = self.global_avg_pool(x)

        # Flatten the tensor for the fully connected layer
        x = torch.flatten(x, 1)  # Keep batch dimension

        return x


# Example usage
model = ToyCNN()

# # Create a dummy input (e.g., batch size 1, 3 channels, arbitrary image size)
# dummy_input = torch.randn(1, 3, 128, 128)  # Replace 128x128 with any size

# # Forward pass through the model
# output = model(dummy_input)
# torch.save(model.state_dict(), "toy_adaface.pth")
# print(f"Output shape: {output.shape}")

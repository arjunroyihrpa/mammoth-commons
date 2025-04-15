import torchvision.transforms as transforms
from PIL import Image as PILImage


# Function to convert RGB to BGR
def to_bgr(img):
    if img.ndimension() == 3:  # (C, H, W)
        return img[[2, 1, 0], :, :]
    elif img.ndimension() == 4:  # (B, C, H, W)
        return img[:, [2, 1, 0], :, :]
    else:
        raise ValueError(f"Unexpected image shape: {img.shape}")

def img_loader(img_path):
    if not isinstance(img_path, str):
        return img_path
    image = PILImage.open(img_path).convert("RGB")
    return image

# Important note: make sure that your transforms have resize and normalize!
# Transformation pipeline
transform = transforms.Compose(
    [
        transforms.Lambda(img_loader),
        transforms.Resize(
            (112, 112), interpolation=transforms.InterpolationMode.NEAREST
        ),  # Resize image to 112x112
        transforms.ToTensor(),  # Convert image to PyTorch tensor
        transforms.Lambda(to_bgr),  # Convert RGB to BGR
        transforms.Normalize(
            mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]
        ),  # Normalize with BGR values
    ]
)

import torchvision.transforms as transforms
from PIL import Image as PILImage


def img_loader(img_path):
    if not isinstance(img_path, str):
        return img_path
    image = PILImage.open(img_path).convert("RGB")
    return image


transform = transforms.Compose(
    [
        transforms.Lambda(img_loader),
        transforms.Resize(
            (256, 256), interpolation=transforms.InterpolationMode.NEAREST
        ),  # Resize image to 256x256
        transforms.ToTensor(),  # Convert image to PyTorch tensor
        transforms.Normalize(  # Normalize image with mean and standard deviation
            mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
        ),
    ]
)

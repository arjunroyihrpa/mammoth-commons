from io import BytesIO
import requests
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

def img_loader(img_path, url_str=""):
    """
    If img_path is already a URL or not a string, it returns img_path as is.

    Note: This function also includes logic to *load* the image from the
    generated URL using the 'requests' library, as PIL cannot directly
    open images from HTTP URLs.
    """
    # minio_url = f"http://localhost:9000/{img_path}"

    if not isinstance(img_path, str):
        return img_path
    elif url_str == "":
        image = PILImage.open(img_path).convert("RGB")
        return image
    else: 
        full_url = f"{url_str}/{img_path}"
        try:
            # Fetch the image content from the URL
            # Use stream=True and iter_content for large files if needed
            response = requests.get(full_url)
            response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)

            # Open the image using PIL from the fetched content
            image = PILImage.open(BytesIO(response.content)).convert("RGB")
            return image
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to load image from URL '{full_url}': {e}") from e


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

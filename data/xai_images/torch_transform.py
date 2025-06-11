from io import BytesIO
import requests
import torchvision.transforms as transforms
from PIL import Image as PILImage
import urllib.parse

def img_loader(img_path, base_url=""):
    """
    If img_path is already a URL or not a string, it returns img_path as is.

    Note: This function also includes logic to *load* the image from the
    generated URL using the 'requests' library, as PIL cannot directly
    open images from HTTP URLs.
    """
    # url examples: "http://localhost:5500", "http://minio-service:9000/"

    if not isinstance(img_path, str):
        return img_path
    elif base_url == "":
        image = PILImage.open(img_path).convert("RGB")
        return image
    else: 
        full_url = urllib.parse.urljoin(base_url, img_path)


        print(full_url)
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

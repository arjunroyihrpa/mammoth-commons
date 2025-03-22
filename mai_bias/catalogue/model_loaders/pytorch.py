import os
from mammoth_commons.models.pytorch import Pytorch
from mammoth_commons.integration import loader
from mammoth_commons.externals import safeexec
import torch


@loader(namespace="mammotheu", version="v0038", python="3.12")
def model_torch(
    state_path: str = "",
    model_path: str = "",
    model_name: str = "model",
    safe_libraries: str = "numpy, torch, torchvision",
    multiclass_threshold: float = 0,
) -> Pytorch:
    """Loads a pytorch model that comprises a Python code initializing the
    architecture and a file of trained parameters. For safety, the architecture's
    definition is allowed to directly import only specified libraries.

    Args:
        state_path: The path in which the architecture's state is stored.
        model_path: The path in which the architecture's initialization script resides. Alternatively, you may also just paste the initialization code in this field.
        model_name: The variable in the model path's script to which the architecture is assigned.
        safe_libraries: A comma-separated list of libraries that can be imported.
        multiclass_threshold: A decision threshold that treats outputs as separate classes. If this is set to zero (default), a softmax is applied to outputs. For binary classification, this is equivalent to setting the decision threshold at 0.5. Otherwise, each output is thresholded separately.
    """

    multiclass_threshold = float(multiclass_threshold)
    model = safeexec(
        model_path,
        out=model_name,
        whitelist=[lib.strip() for lib in safe_libraries.split(",")],
    )
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.load_state_dict(torch.load(state_path, map_location=device))
    return Pytorch(model, threshold=multiclass_threshold)

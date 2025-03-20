import io
import os
from mammoth.models.pytorch2onnx import ONNX
from mammoth.integration import loader
from mammoth.externals import safeexec
import torch
import tempfile


@loader(namespace="mammotheu", version="v0038", python="3.12")
def model_torch2onnx(
    state_path: str = "",
    model_path: str = "",
    model_name: str = "model",
    input_size: tuple[int, int] = (224, 224),
    safe_libraries: str = "numpy, torch, torchvision",
    multiclass_threshold: float = 0,
) -> ONNX:
    """Loads a ONNX model that comprises a Python code initializing the
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

    model.load_state_dict(torch.load(state_path, map_location="cpu"))
    model.eval()
    dummy_input = torch.randn(1, 3, *input_size)

    with tempfile.NamedTemporaryFile(suffix=".onnx", delete=False) as temp_file:
        onnx_model_path = temp_file.name
        torch.onnx.export(
            model,
            dummy_input,
            onnx_model_path,
            input_names=["input"],
            output_names=["output"],
            dynamic_axes={"input": {0: "batch_size"}, "output": {0: "batch_size"}},
        )

    onnx_model = ONNX(onnx_model_path, threshold=multiclass_threshold)
    os.remove(onnx_model_path)
    return onnx_model

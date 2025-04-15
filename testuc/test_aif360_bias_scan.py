from typing import Dict, List
from kfp import dsl, local
from mai_bias.catalogue.dataset_loaders.custom_csv import data_custom_csv
from mai_bias.catalogue.model_loaders.onnx import model_onnx
from mai_bias.catalogue.metrics.bias_scan import bias_scan


@dsl.pipeline(name="test_aif360_bias_scan")
def pipeline(
    model_onnx__params: Dict,
    data_custom_csv__params: Dict,
    sensitive: List,
    bias_scan__params: Dict,
):
    data_custom_csv_task = data_custom_csv(
        data_custom_csv__params=data_custom_csv__params
    )
    model_onnx_task = model_onnx(model_onnx__params=model_onnx__params)
    bias_scan_task = bias_scan(
        bias_scan__params=bias_scan__params,
        sensitive=sensitive,
        dataset=data_custom_csv_task.outputs["output"],
        model=model_onnx_task.outputs["output"],
    )


# IMPORTANT: Components need to be build to have the docker image before testing with this file
# Build components commands
# Run the following commands to build the relevant components

# kfp component build . --component-filepattern <module_path_to_py>

# Test pipeline execution
local.init(runner=local.DockerRunner())

numeric = ["age", "duration", "campaign", "pdays", "previous"]
categorical = [
    "job",
    "marital",
    "education",
    "default",
    "housing",
    "loan",
    "contact",
    "poutcome",
]
sensitive = ["poutcome"]
dataset_uri = (
    "https://archive.ics.uci.edu/static/public/222/bank+marketing.zip/bank/bank.csv"
)


pipeline(
    data_custom_csv__params={
        "path": dataset_uri,
        "categorical": categorical,
        "numeric": numeric,
        "label": "y",
        "delimiter": ";",
    },
    model_onnx__params={
        "path": "https://github.com/mammoth-eu/mammoth-commons/raw/refs/heads/dev/data/model.onnx",
    },
    sensitive=sensitive,
    bias_scan__params={
        "penalty": 0.5,
    },
)

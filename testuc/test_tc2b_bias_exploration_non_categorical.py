from typing import Dict, List
from kfp import dsl, local
from mai_bias.catalogue.dataset_loaders.custom_csv import data_custom_csv
from mai_bias.catalogue.model_loaders.onnx import model_onnx
from mai_bias.catalogue.metrics.interactive_report import interactive_report


@dsl.pipeline(name="test_tc2b_bias_exploration_non_categorical")
def pipeline(
    model_onnx__params: Dict,
    data_custom_csv__params: Dict,
    sensitive: List,
    interactive_report__params: Dict,
):
    data_custom_csv_task = data_custom_csv(
        data_custom_csv__params=data_custom_csv__params
    )
    model_onnx_task = model_onnx(model_onnx__params=model_onnx__params)
    interactive_report_task = interactive_report(
        interactive_report__params=interactive_report__params,
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
sensitive = ["marital", "age"]
dataset_uri = "https://archive.ics.uci.edu/static/public/222/bank+marketing.zip/bank/bank.csv"

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
    interactive_report__params={
        "compare_groups": "Pairwise",
    },
)


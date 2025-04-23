from typing import Dict, List
from kfp import dsl, local
from mai_bias.catalogue.dataset_loaders.custom_csv import data_custom_csv
from mai_bias.catalogue.model_loaders.onnx import model_onnx
from mai_bias.catalogue.metrics.model_card import model_card


@dsl.pipeline(name="test_tc2a_bias_exploration")
def pipeline(
    model_onnx__params: Dict,
    data_custom_csv__params: Dict,
    sensitive: List,
    model_card__params: Dict,
):
    data_custom_csv_task = data_custom_csv(
        data_custom_csv__params=data_custom_csv__params
    )
    model_onnx_task = model_onnx(model_onnx__params=model_onnx__params)
    model_card_task = model_card(
        model_card__params=model_card__params,
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
sensitive = ["marital"]
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
    model_card__params={
        "compare_groups": "Pairwise",
    },
)

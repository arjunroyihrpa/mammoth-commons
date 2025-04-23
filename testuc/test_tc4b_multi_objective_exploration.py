from typing import Dict, List
from kfp import dsl, local
from mai_bias.catalogue.model_loaders.onnx_ensemble import model_onnx_ensemble
from mai_bias.catalogue.dataset_loaders.uci_csv import data_uci
from mai_bias.catalogue.metrics.multi_objective_report import multi_objective_report


@dsl.pipeline(name="test_tc4b_multi_objective_exploration")
def pipeline(
    model_onnx_ensemble__params: Dict,
    data_uci__params: Dict,
    sensitive: List,
    multi_objective_report__params: Dict,
):
    data_uci_task = data_uci(
        data_uci__params=data_uci__params
    )
    model_onnx_ensemble_task = model_onnx_ensemble(model_onnx_ensemble__params=model_onnx_ensemble__params)
    multi_objective_report_task = multi_objective_report(
        multi_objective_report__params=multi_objective_report__params,
        sensitive=sensitive,
        dataset=model_onnx_ensemble_task.outputs["output"],
        model=data_uci_task.outputs["output"],
    )


# IMPORTANT: Components need to be build to have the docker image before testing with this file
# Build components commands
# Run the following commands to build the relevant components

# kfp component build . --component-filepattern <module_path_to_py>

# Test pipeline execution
local.init(runner=local.DockerRunner())


sensitive = ["X2", "X4", "X5"]

pipeline(
    data_uci__params={
        "dataset_name": "credit",
        "target": "Y",
    },
    model_onnx_ensemble__params={
        "path": "https://github.com/mammoth-eu/mammoth-commons/raw/refs/heads/dev/data/credit_mfppb.zip",
    },
    sensitive=sensitive,
    multi_objective_report__params={},
)



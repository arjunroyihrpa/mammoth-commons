from typing import Dict, List
from kfp import dsl, local
from mai_bias.catalogue.dataset_loaders.auto_csv import data_auto_csv
from mai_bias.catalogue.metrics.multi_objective_report import multi_objective_report
from mai_bias.catalogue.model_loaders.onnx_ensemble import model_onnx_ensemble


@dsl.pipeline(name="financial-model-exploration")
def pipeline(
    model_onnx_ensemble__params: Dict, data_auto_csv__params: Dict, sensitive: List
):
    data_auto_csv_task = data_auto_csv(data_auto_csv__params=data_auto_csv__params)
    onnx_model_task = model_onnx_ensemble(
        model_onnx_ensemble__params=model_onnx_ensemble__params
    )
    metric_task = multi_objective_report(
        sensitive=sensitive,
        dataset=data_auto_csv_task.outputs["output"],
        model=onnx_model_task.outputs["output"],
    )


# IMPORTANT: Components need to be build to have the docker image before testing with this file
# Build components commands
# Run the following commands to build the relevant components

# kfp component build . --component-filepattern mai_bias/catalogue/model_loaders/onnx_ensemble.py
# kfp component build . --component-filepattern mai_bias/catalogue/dataset_loaders/auto_csv.py
# kfp component build . --component-filepattern mai_bias/catalogue/metrics/multi_objective_report.py

# Test pipeline execution
local.init(runner=local.DockerRunner())

pipeline(
    model_onnx_ensemble__params={
        "path": "https://github.com/mammoth-eu/mammoth-commons/raw/refs/heads/dev/data/mfppb.zip"
    },
    data_auto_csv__params={
        "path": "https://raw.githubusercontent.com/mammoth-eu/mammoth-commons/refs/heads/dev/data/bank.csv"
    },
    sensitive=["age", "marital"],
)

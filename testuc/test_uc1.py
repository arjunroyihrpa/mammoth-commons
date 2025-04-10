from typing import Dict, List
from kfp import dsl, local
from mai_bias.catalogue.dataset_loaders.auto_csv import data_auto_csv
from mai_bias.catalogue.metrics.sklearn_audit import sklearn_audit
from mai_bias.catalogue.model_loaders.no_model import no_model



@dsl.pipeline(name="financial-data-exploration")
def pipeline(data_auto_csv__params: Dict, sensitive: List, sklearn_audit__params: Dict):
    data_auto_csv_task = data_auto_csv(data_auto_csv__params=data_auto_csv__params)
    no_model_task = no_model()
    sklearn_audit_task = sklearn_audit(
        sklearn_audit__params=sklearn_audit__params,
        sensitive=sensitive,
        dataset=data_auto_csv_task.outputs["output"],
        model=no_model_task.outputs["output"],
    )


# IMPORTANT: Components need to be build to have the docker image before testing with this file
# Build components commands
# Run the following commands to build the relevant components

# kfp component build . --component-filepattern mai_bias/catalogue/model_loaders/no_model.py
# kfp component build . --component-filepattern mai_bias/catalogue/dataset_loaders/auto_csv.py
# kfp component build . --component-filepattern mai_bias/catalogue/metrics/sklearn_audit.py

# Test pipeline execution
local.init(runner=local.DockerRunner())

pipeline(
    data_auto_csv__params={
        "path": "https://raw.githubusercontent.com/mammoth-eu/mammoth-commons/refs/heads/dev/data/bank.csv"
    },
    sensitive=["age", "marital"],
    sklearn_audit__params={
        "predictor": "Logistic regression",
        "intersectional": True,
        "compare_groups": "Pairwise",
        "problematic_deviation": 0.1,
        "show_non_problematic": False,
        "top_recommendations": 3,
    },
)
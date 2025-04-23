from typing import Dict, List
from kfp import dsl, local
from mai_bias.catalogue.dataset_loaders.graph import data_graph
from mai_bias.catalogue.model_loaders.fair_node_ranking import model_fair_node_ranking
from mai_bias.catalogue.metrics.model_card import model_card


@dsl.pipeline(name="test_tc4b_multi_objective_exploration")
def pipeline(
    data_graph__params: Dict,
    model_fair_node_ranking__params: Dict,
    sensitive: List,
    model_card__params: Dict,
):
    model_fair_node_ranking_task = model_fair_node_ranking(
        model_fair_node_ranking__params=model_fair_node_ranking__params
    )
    data_graph_task = data_graph(data_graph__params=data_graph__params)
    model_card_task = model_card(
        model_card__params=model_card__params,
        sensitive=sensitive,
        dataset=data_graph_task.outputs["output"],
        model=model_fair_node_ranking_task.outputs["output"],
    )


# IMPORTANT: Components need to be build to have the docker image before testing with this file
# Build components commands
# Run the following commands to build the relevant components

# kfp component build . --component-filepattern <module_path_to_py>

# Test pipeline execution
local.init(runner=local.DockerRunner())
sensitive = ["0"]


pipeline(
    model_fair_node_ranking__params={
        "diffusion": 0.9,
    },
    data_graph__params={
        "path": "citeseer",
    },
    sensitive=sensitive,
    model_card__params={        
        "compare_groups": "Pairwise"
    },
)




#######################

from mammoth_commons import testing
from mai_bias.catalogue.model_loaders.onnx_ensemble import model_onnx_ensemble
from mai_bias.catalogue.dataset_loaders.uci_csv import data_uci
from mai_bias.catalogue.metrics.multi_objective_report import multi_objective_report


def test_multiobjective_report():
    with testing.Env(model_onnx_ensemble, multi_objective_report, data_uci) as env:
        dataset_name = "credit"
        target = "Y"
        dataset = env.data_uci(dataset_name=dataset_name, target=target)
        model_path = "data/credit_mfppb.zip"
        model = env.model_onnx_ensemble(model_path)
        sensitive = ["X2", "X4", "X5"]
        html_result = env.multi_objective_report(dataset, model, sensitive=sensitive)
        html_result.show()


if __name__ == "__main__":
    test_multiobjective_report()

from typing import Dict, List
from kfp import dsl, local
from mai_bias.catalogue.dataset_loaders.graph import data_graph
from mai_bias.catalogue.model_loaders.fair_node_ranking import model_fair_node_ranking
from mai_bias.catalogue.metrics.model_card import model_card


@dsl.pipeline(name="test_tc3_fair_graph_filtering")
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

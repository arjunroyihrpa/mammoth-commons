# data loaders
from catalogue.dataset_loaders.data_csv_rankings import data_csv_rankings
from catalogue.dataset_loaders.data_researchers import data_researchers
from catalogue.dataset_loaders.custom_csv import data_custom_csv
from catalogue.dataset_loaders.auto_csv import data_auto_csv
from catalogue.dataset_loaders.graph import data_graph
from catalogue.dataset_loaders.images import data_images
from catalogue.dataset_loaders.image_pairs import data_image_pairs
from catalogue.dataset_loaders.uci_csv import data_uci

# model loaders
from catalogue.model_loaders.no_model import no_model
from catalogue.model_loaders.onnx import model_onnx
from catalogue.model_loaders.onnx_ensemble import model_onnx_ensemble
from catalogue.model_loaders.pytorch import model_torch
from catalogue.model_loaders.pytorch2onnx import model_torch2onnx
from catalogue.model_loaders.fair_node_ranking import model_fair_node_ranking
from catalogue.model_loaders.compute_researcher_ranking import model_mitigation_ranking

# metrics
from catalogue.metrics.model_card import model_card
from catalogue.metrics.interactive_report import interactive_report
from catalogue.metrics.sklearn_audit import sklearn_audit
from catalogue.metrics.image_bias_analysis import image_bias_analysis
from catalogue.metrics.xai_analysis import facex_regions
from catalogue.metrics.xai_analysis_embeddings import facex_embeddings
from catalogue.metrics.ranking_fairness import exposure_distance_comparison
from catalogue.metrics.multi_objective_report import multi_objective_report
from catalogue.metrics.optimal_transport import optimal_transport
from catalogue.metrics.bias_scan import bias_scan
from catalogue.metrics.augmentation_report import (
    augmentation_report,
)

from mai.backend.registry import Registry

registry = Registry()

registry.data(data_auto_csv)
registry.data(data_uci)
registry.data(data_custom_csv)
registry.data(data_csv_rankings)
registry.data(data_researchers)
registry.data(data_graph)
registry.data(data_images)
registry.data(data_image_pairs)

registry.model(
    no_model,
    compatible=[
        data_auto_csv,
        data_custom_csv,
        data_uci,
        data_images,
    ],
)
registry.model(model_onnx, compatible=[data_auto_csv, data_custom_csv, data_uci])
registry.model(
    model_onnx_ensemble,
    compatible=[data_auto_csv, data_custom_csv, data_uci],
)
registry.model(model_torch, compatible=[data_images, data_image_pairs])
registry.model(model_torch2onnx, compatible=[data_images, data_image_pairs])
registry.model(model_fair_node_ranking, compatible=[data_graph])
registry.model(model_mitigation_ranking, compatible=[data_researchers])

registry.analysis(model_card)
registry.analysis(interactive_report)
registry.analysis(sklearn_audit)
registry.analysis(optimal_transport)
registry.analysis(bias_scan)
registry.analysis(image_bias_analysis)
registry.analysis(facex_regions)
registry.analysis(facex_embeddings)
registry.analysis(multi_objective_report)
registry.analysis(
    exposure_distance_comparison,
    compatible=[model_mitigation_ranking],
)
registry.analysis(augmentation_report)

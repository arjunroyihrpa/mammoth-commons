echo "Building components"

pip install --upgrade -r requirements\[test\].txt
pip install -e .

kfp component build . --component-filepattern catalogue/dataset_loaders/auto_csv.py
docker system prune -a --force --volumes
kfp component build . --component-filepattern catalogue/dataset_loaders/custom_csv.py
docker system prune -a --force --volumes
kfp component build . --component-filepattern catalogue/dataset_loaders/data_csv_rankings.py
docker system prune -a --force --volumes
kfp component build . --component-filepattern catalogue/dataset_loaders/data_researchers.py
docker system prune -a --force --volumes
kfp component build . --component-filepattern catalogue/dataset_loaders/graph.py
docker system prune -a --force --volumes
kfp component build . --component-filepattern catalogue/dataset_loaders/image_pairs.py
docker system prune -a --force --volumes
kfp component build . --component-filepattern catalogue/dataset_loaders/images.py
docker system prune -a --force --volumes
kfp component build . --component-filepattern catalogue/dataset_loaders/uci_csv.py
docker system prune -a --force --volumes

kfp component build . --component-filepattern catalogue/model_loaders/compute_rankings.py
docker system prune -a --force --volumes
kfp component build . --component-filepattern catalogue/model_loaders/compute_researcher_ranking.py
docker system prune -a --force --volumes
kfp component build . --component-filepattern catalogue/model_loaders/fair_node_ranking.py
docker system prune -a --force --volumes
kfp component build . --component-filepattern catalogue/model_loaders/no_model.py
docker system prune -a --force --volumes
kfp component build . --component-filepattern catalogue/model_loaders/onnx_ensemble.py
docker system prune -a --force --volumes
kfp component build . --component-filepattern catalogue/model_loaders/onnx.py
docker system prune -a --force --volumes
kfp component build . --component-filepattern catalogue/model_loaders/pytorch.py
docker system prune -a --force --volumes
kfp component build . --component-filepattern catalogue/model_loaders/pytorch2onnx.py
docker system prune -a --force --volumes

kfp component build . --component-filepattern catalogue/metrics/bias_scan.py
docker system prune -a --force --volumes
kfp component build . --component-filepattern catalogue/metrics/image_bias_analysis.py
docker system prune -a --force --volumes
kfp component build . --component-filepattern catalogue/metrics/interactive_report.py
docker system prune -a --force --volumes
kfp component build . --component-filepattern catalogue/metrics/interactive_augmentation_report.py
docker system prune -a --force --volumes
kfp component build . --component-filepattern catalogue/metrics/interactive_sklearn_report.py
docker system prune -a --force --volumes
kfp component build . --component-filepattern catalogue/metrics/model_card.py
docker system prune -a --force --volumes
kfp component build . --component-filepattern catalogue/metrics/multi_objective_report.py
docker system prune -a --force --volumes
kfp component build . --component-filepattern catalogue/metrics/optimal_transport.py
docker system prune -a --force --volumes
kfp component build . --component-filepattern catalogue/metrics/ranking_fairness.py
docker system prune -a --force --volumes
kfp component build . --component-filepattern catalogue/metrics/xai_analysis_embeddings.py
docker system prune -a --force --volumes
kfp component build . --component-filepattern catalogue/metrics/xai_analysis.py
docker system prune -a --force --volumes

mkdir yamls
mkdir yamls/data
mkdir yamls/meta

cp catalogue/dataset_loaders/component_metadata/* yamls/meta/
cp catalogue/model_loaders/component_metadata/* yamls/meta/
cp catalogue/metrics/component_metadata/* yamls/meta/
cp component_metadata/* yamls/data/

echo "Completed building components"


import os
from mammoth import testing

from catalogue.dataset_loaders.custom_csv import data_custom_csv
from catalogue.model_loaders.onnx import model_onnx
from catalogue.metrics.optimal_transport import optimal_transport


def test_optimal_transport():
    with testing.Env(data_custom_csv, model_onnx, optimal_transport) as env:
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
        dataset_uri = "https://archive.ics.uci.edu/static/public/222/bank+marketing.zip/bank/bank.csv"
        dataset = env.data_custom_csv(
            dataset_uri,
            categorical=categorical,
            numeric=numeric,
            label="y",
            delimiter=";",
        )

        model_path = "file://localhost//" + os.path.abspath("./data/model.onnx")
        model = env.model_onnx(model_path)

        markdown_result = env.optimal_transport(dataset, model, sensitive)
        markdown_result.show()


if __name__ == "__main__":
    test_optimal_transport()

from mammoth_commons.datasets import CSV
from mammoth_commons.integration import loader, Options

# from collections import OrderedDict
# import os
from mmm_fair.data_process import data_uci


@loader(
    namespace="mammotheu",
    version="v0042",
    python="3.12",
    packages=("pandas", "ucimlrepo", "mmm-fair"),
)
def data_uci_(
    dataset_name: str = "Credit",
    target=None,
) -> CSV:
    """Loads a dataset from the UCI Machine Learning Repository (<a href="https://archive.ics.uci.edu/ml/index.php" target="_blank">www.uci.org</a>) containing numeric, categorical, and predictive data columns. The dataset is automatically downloaded from the repository, and basic preprocessing is applied to identify the column types. The specified target column is treated as the predictive label.
        To customize the loading process (e.g., use a different target column, load a subset of features, or handle missing data differently), additional parameters or a custom loader can be used.

    Args:
        dataset_name: The name of the dataset.
        target: The name of the predictive label.
    """
    try:
        csv_dataset = data_uci(dataset_name)

        return csv_dataset
    except Exception as e:
        print(f"Failed to load the dataset for error: {e}")

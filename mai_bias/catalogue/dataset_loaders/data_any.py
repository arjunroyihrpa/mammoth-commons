from mammoth_commons.datasets import CSV
from mammoth_commons.integration import loader, Options
import pandas as pd


@loader(
    namespace="mammotheu",
    version="v0042",
    python="3.13",
    packages=("pandas", "onnxruntime", "mmm-fair", "skl2onnx"),
)
def data_read_any(
    raw_data: pd.DataFrame=None,
    dataset_name: str=None,
    target=None,
) -> CSV:
    """
    Loads a dataset for analysis from either a pre-loaded pandas DataFrame or a file in one of the supported formats:
    `.csv`, `.xls`, `.xlsx`, `.xlsm`, `.xlsb`, `.odf`, `.ods`, `.json`, `.html`, or `.htm`.

    The module accepts either a raw DataFrame or a file path (local or URL). If a file path is provided, the data is
    automatically loaded using the appropriate pandas function based on the file extension. Basic preprocessing is applied
    to infer column types, and the specified target column is treated as the predictive label.

    To customize the loading process (e.g., load a subset of columns, handle missing values, or change column type inference),
    additional parameters or a custom loader function may be provided.

    The Data loader module is recommended to load and process local data also while training models which are intented to be tested
    using the ONNXEnsemble module.

    Args:
        raw_dataframe (pd.DataFrame, optional): A preloaded pandas DataFrame. If provided, it is used directly.
        dataset_path (str, optional): Path or URL to the dataset file. Must have one of the supported extensions.
        target (str): The name of the column to treat as the predictive label.
    """
    from mmm_fair.data_process import data_raw

    csv_dataset = data_raw(raw_data, dataset_name, target)
    # TODO: REMOVE first argument
    # TODO: add conversion to the actual mammoth CSV data type here. Something like the following but export the labels too
    # TODO: returns commons data structures only if you import the module, otherwise return a convertible
    # return CSV(df=csv_dataset.data,num=csv_dataset.numeric, cat=csv_dataset.categorical, labels="TODO")
    return csv_dataset

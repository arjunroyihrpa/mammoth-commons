from mammoth_commons.datasets import CSV
from mammoth_commons.integration import loader
from mammoth_commons.externals import pd_read_csv


@loader(
    namespace="mammotheu",
    version="v0038",
    python="3.12",
    packages=("pandas",),
)
def data_auto_csv(path: str = "", max_discrete: int = 10) -> CSV:
    """Loads a CSV file that contains numeric, categorical, and predictive data columns.
    This automatically detects the characteristics of the dataset being loaded,
    namely the delimiter that separates the columns, and whether each column contains
    numeric or categorical data. A <a href="https://pandas.pydata.org/">pandas</a>
    CSV reader is employed internally.
    The last categorical column is used as the dataset label. To load the file using
    different options (e.g., a subset of columns, a different label column) use the
    custom csv loader instead.

    Args:
        path: The local file path or a web URL of the file.
        max_discrete: If a numeric column has a number of discrete entries than is less than this number (e.g., if it contains binary numeric values) then it is considered to hold categorical instead of numeric data. Minimum accepted value is 2.
    """
    if not path.endswith(".csv"):
        raise Exception("A file or url with .csv extension is needed.")
    max_discrete = int(max_discrete)
    if max_discrete < 2:
        raise Exception(
            "The number of numeric levels (the value of max discrete) should be at least 2"
        )
    raw_data = pd_read_csv(
        path,
        on_bad_lines="skip",
    )
    import pandas as pd

    numeric = [
        col for col in raw_data if pd.api.types.is_any_real_numeric_dtype(raw_data[col])
    ]
    numeric = [col for col in numeric if len(set(raw_data[col])) > max_discrete]
    numeric_set = set(numeric)
    categorical = [col for col in raw_data if col not in numeric_set]
    if len(categorical) < 1:
        raise Exception("At least two categorical columns are required.")
    label = categorical[-1]
    categorical = categorical[:-1]

    csv_dataset = CSV(
        raw_data,
        numeric=numeric,
        categorical=categorical,
        labels=label,
    )
    return csv_dataset

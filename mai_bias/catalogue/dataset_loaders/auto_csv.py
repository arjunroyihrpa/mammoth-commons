import importlib
from mammoth_commons.datasets import CSV
from mammoth_commons.integration import loader
from mammoth_commons.externals import pd_read_csv


@loader(
    namespace="mammotheu",
    version="v0042",
    python="3.13",
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
    max_discrete = int(max_discrete)
    assert path.endswith(".csv"), "A file or url with the .csv extension is expected."
    assert max_discrete >= 2, "Numeric levels (max discrete) should be at least 2"
    pd = importlib.import_module("pandas")
    df = pd_read_csv(path, on_bad_lines="skip")
    num = [col for col in df if pd.api.types.is_any_real_numeric_dtype(df[col])]
    num = [col for col in num if len(set(df[col])) > max_discrete]
    num_set = set(num)
    cat = [col for col in df if col not in num_set]
    assert len(cat) >= 1, "At least one categorical column is required."
    csv_dataset = CSV(df, num=num, cat=cat[:-1], labels=cat[-1])
    return csv_dataset

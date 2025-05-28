from typing import Iterable
import importlib
import numpy as np
from mammoth_commons.datasets.dataset import Dataset, Labels


def pd_features(df, num: list[str], cat: list[str], sens: list[str] | None = None):
    sens = set() if sens is None else set(sens)
    pd = importlib.import_module("pandas")
    dfs = [df[col] for col in num if col not in sens]
    dfs += [pd.get_dummies(df[col]) for col in cat if col not in sens]
    return pd.concat(dfs, axis=1).values


class CSV(Dataset):
    def __init__(
        self,
        df,
        num: list[str],
        cat: list[str],
        labels: str | dict | Iterable | None,
        sens: list[str] | None = None,
    ):
        pd = importlib.import_module("pandas")
        super().__init__(Labels(dict()))
        self.df = df
        self.num = num
        self.cat = cat
        self.cols = num + cat
        sens = set() if sens is None else set(sens)
        self.feats = [col for col in self.cols if col not in sens]
        self.labels = Labels(
            pd.get_dummies(df[labels]).to_dict(orient="list")
            if isinstance(labels, str)
            else labels if isinstance(labels, dict) else {"1": labels, "0": 1 - labels}
        )

    def to_numpy(self, sensitive: list[str]):
        return pd_features(self.df, self.num, self.cat).astype(np.float64)

    def to_input(self, sensitive: list[str]):
        return pd_features(self.df, self.num, self.cat, sensitive).astype(np.float64)

    def to_csv(self, sensitive: list[str]):
        return self

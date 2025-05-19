from mammoth_commons.models import EmptyModel
from mammoth_commons.integration import loader


@loader(namespace="mammotheu", version="v0042", python="3.13")
def no_model() -> EmptyModel:
    """Signifies that the analysis should focus solely on the fairness of the dataset."""

    return EmptyModel()

from mammoth_commons.models import EmptyModel
from mammoth_commons.integration import loader


@loader(namespace="mammotheu", version="v0038", python="3.12")
def no_model() -> EmptyModel:
    """Signifies that the analysis should focus solely on the fairness of the dataset."""

    return EmptyModel()

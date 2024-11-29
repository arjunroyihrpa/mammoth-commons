import numpy as np

from mammoth.datasets import CSV
from mammoth.models import EmptyModel
from mammoth.exports import HTML
from typing import Dict, List
from mammoth.integration import metric, Options
import fairbench as fb
import sklearn
import numpy as np


@fb.core.Transform
def categories(iterable):
    # print(iterable)
    is_numeric = True
    values = list()
    for value in iterable:
        try:
            values.append(float(value))
        except Exception:
            is_numeric = False
            break
    if is_numeric:
        values = np.array(values)
        mx = values.max()
        mn = values.min()
        if mx == mn:
            raise Exception(
                "Numerical sensitive attribute has the same value everywhere"
            )
        values = (values - mn) / (mx - mn)
        return {f"fuzzy min ({mn:.3f})": 1 - values, f"fuzzy max ({mx:.3f})": values}
    return fb.categories @ iterable


@metric(
    namespace="maniospas",
    version="v002",
    python="3.11",
    packages=(
        "fairbench",
        "scikit-learn",
    ),
)
def interactive_sklearn_report(
    dataset: CSV,
    model: EmptyModel,
    sensitive: List[str],
    predictor: Options("Logistic regression", "Gaussian naive Bayes") = None,
    intersectional: bool = False,
    compare_groups: Options("Pairwise", "To the total population") = None,
) -> HTML:
    """Creates an interactive report using the FairBench library, after running an internal training-test split
    on a basic sklearn model. The report creates traceable evaluations that you can shift through to find sources
    of unfairness on a common task.

    Args:
        predictor: Which sklearn predictor should be used.
        intersectional: Whether to consider all non-empty group intersections during analysis. This does nothing if there is only one sensitive attribute.
        compare_groups: Whether to compare groups pairwise, or each group to the whole population.
    """
    X = dataset.to_features(sensitive)
    y = dataset.labels
    if isinstance(y, dict):
        y = y[list(y.keys())[0]]
    else:
        assert (
            y.shape[1] <= 2
        ), "Cannot create a logistic regression interactive report for non-binary predictions"
        y = y[y.columns[-1]]
    from sklearn import model_selection

    (
        X_train,
        X_test,
        y_train,
        y_test,
        _,
        idx_test,
    ) = model_selection.train_test_split(
        X, y, np.arange(0, y.shape[0], dtype=np.int64), test_size=0.2
    )
    if predictor == "Logistic regression":
        from sklearn.linear_model import LogisticRegression

        model = LogisticRegression(max_iter=1000)
    elif predictor == "Gaussian naive Bayes":
        from sklearn.naive_bayes import GaussianNB

        model = GaussianNB()
    else:
        raise Exception(
            "Available predictors for interactive sklearn reports are only `Logistic regression` and `Gaussian naive Bayes`"
        )
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    scores = model.predict_proba(X_test)[:, 1]

    # declare sensitive attributes
    sensitive = fb.Fork(
        {attr + " ": (categories @ dataset.data[attr][idx_test]) for attr in sensitive}
    )

    # change behavior based on arguments
    if intersectional:
        sensitive = sensitive.intersectional()
    report_type = fb.multireport if compare_groups == "Pairwise" else fb.unireport

    report = report_type(
        predictions=predictions,
        labels=y_test.to_numpy(),
        scores=scores,
        sensitive=sensitive,
    )
    return HTML(fb.interactive_html(report, show=False, name=predictor))

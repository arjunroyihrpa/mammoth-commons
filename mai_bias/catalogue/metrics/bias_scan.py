import pandas as pd

import mammoth_commons.integration
from mammoth_commons.datasets import CSV
from mammoth_commons.models import Predictor
from mammoth_commons.exports import HTML
from typing import List
from mammoth_commons.integration import metric
from aif360.sklearn.detectors import bias_scan as aif360bias_scan


@metric(
    namespace="mammotheu",
    version="v0038",
    python="3.12",
    packages=(
        "aif360",
        "pandas",
        "onnxruntime",
        "ucimlrepo",
        "pygrank",
    ),
)
def bias_scan(
    dataset: CSV,
    model: Predictor,
    sensitive: List[str],
    penalty: float = 0.5,
    scoring: mammoth_commons.integration.Options(
        "Bernoulli", "Gaussian", "Poisson", "BerkJones"
    ) = "Bernoulli",
) -> HTML:
    """<p>Performs a scan for the most biased attribute intersection in the dataset.
    Any sensitive attributes that are already known will be <b>excluded</b> from the scan. That is, you can
    condition the scan to discover more attributes other than those declared as sensitive (these may not be
    actually sensitive, but set so because you are trying to find more subtle biases).
    To start a scan for the first time, do not set any sensitive attributes.
    A paper describing how this approach is implemented to estimate the intersection
    in linear rather than exponential time is available <a href="https://arxiv.org/pdf/1611.08292">here</a>.</p>

    Args:
        penalty: The higher the penalty, the less complex the highest scoring subset that gets returned is.
        scoring: The distribution used to computer p-values.
    """

    penalty = float(penalty)
    text = ""
    predictions = pd.Series(model.predict(dataset, sensitive))

    counts = 0
    for label in dataset.labels:
        labels = pd.Series(dataset.labels[label])
        cats = [cat for cat in dataset.categorical if cat not in sensitive]
        assert (
            len(cats) != 0
        ), "All categorical attributes are already considered sensitive"
        X = dataset.data[cats]
        ret = aif360bias_scan(
            X=X,
            y_true=labels,
            y_pred=predictions,
            overpredicted=False,
            scoring=scoring,
            penalty=penalty,
        )
        ret = ret[0]
        text += f'<h2 class="text-secondary">Prediction label: {label}</h2>'
        text += '<div class="table-responsive"><table class="table table-striped table-bordered table-hover mt-3">'
        text += '<thead class="thead-dark"><tr><th>Attribute</th><th>Value</th></tr></thead><tbody>'
        for key, values in ret.items():
            for value in values:
                text += f"<tr><td>{key}</td><td>{value}</td></tr>"
        text += "</tbody></table></div>"
        if len(ret) == 0:
            text += "<p>No attribute intersection</p>"
        counts = max(counts, len(ret))

    text = f"""
        <div class="container mt-4">
            {'<h1 class="text-success">No concern</h1>' if counts==0 else '<h1 class="text-danger">Biased intersections of up to '+str(counts)+' attributes</h1>'}
            {"" if len(dataset.numeric) == 0 else "<p><b>Numeric attributes have been ignored; the scan can work with only categorical ones.</b></p>"}
            <p>After scanning for imbalances, the following attribute combinations out of those that were
            <i>not</i> already marked as sensitive were found to be underestimated. There may be more attribute
            combinations that could be underestimated, but only the top one is presented here.
            Not all found attributes should necessarily be protected, and you should account only for the discovered
            intersection.</p>
            {text}
        </div>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">",
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>"
        """

    return HTML(text)

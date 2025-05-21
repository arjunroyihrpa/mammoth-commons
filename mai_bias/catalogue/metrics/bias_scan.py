import mammoth_commons.integration
from mammoth_commons.datasets import CSV
from mammoth_commons.models import Predictor
from mammoth_commons.exports import HTML
from typing import List
from mammoth_commons.integration import metric


@metric(
    namespace="mammotheu",
    version="v0042",
    python="3.13",
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
    discovery: bool = True
) -> HTML:
    """<p>Performs a scan for the most biased attribute intersection in the dataset.
    Any sensitive attributes that are already known will be <b>excluded</b> from the scan. That is, you can
    condition the scan to discover more attributes other than those declared as sensitive. These may not be
    actually sensitive, but set so because you are trying to find more subtle biases.
    A paper describing how this approach is implemented to estimate the intersection
    in linear rather than exponential time is available <a href="https://arxiv.org/pdf/1611.08292">here</a>.</p>

    <p>To start a scan for the first time, do not set any sensitive attributes. As a typical use case, you can
    rerun the analysis by adding problematic attributes from the previous run to those already known to be biased.
    This process will let you discover more potential issues, though now of lesser importance. To help with this
    process, this module can partially automate it by enabling the discovery mode. This removes all problematic
    attributes in the intersection and retries, Discovery
    is less informed than a human investigator that knows when to exclude intersections from the dataset</p>

    Args:
        penalty: The higher the penalty, the less complex the highest scoring subset that gets returned is.
        scoring: The distribution used to compute p-values. Can be Bernoulli, Gaussian, Poisson, or BerkJones.
        discovery: Whether the scan should attempt to create a list of problematic attribute combinations in decreasing order of importance. That list will contain only non-overlapping attribute intersections.
    """
    import pandas as pd
    from aif360.sklearn.detectors import bias_scan as aif360bias_scan

    penalty = float(penalty)
    text = ""
    predictions = pd.Series(model.predict(dataset, sensitive))

    counts = 0
    starting_sensitive = sensitive
    for label in dataset.labels:
        sensitive = starting_sensitive
        text += f'<h2 class="text-secondary">Prediction label: {label}</h2>'
        while True:
            labels = pd.Series(dataset.labels[label])
            cats = [cat for cat in dataset.categorical if cat not in sensitive]
            if len(cats) == 0 and text:
                text += f"<i>All categorical attributes are already considered sensitive</i>"
                break
            assert (
                len(cats) != 0
            ), "All categorical attributes are already considered sensitive"
            if sensitive:
                text += f"<i>Already known sensitive attributes to be ignored: {', '.join(sensitive)}</i>"
            else:
                text += f"<i>No attributes to be ignored (scanning everything)</i>"
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
            stext = ""
            for key, values in ret.items():
                for value in values:
                    stext += f"<tr><td>{key}</td><td>{value}</td></tr>"
                sensitive = sensitive + [key]
            if len(ret) == 0:
                text += "<p>No suspicious attribute intersection</p>"
                break
            text += '<div class="table-responsive"><table class="table table-striped table-bordered table-hover mt-3">'
            text += '<thead class="thead-dark"><tr><th>Attribute</th><th>Value</th></tr></thead><tbody>'
            text += stext
            text += "</tbody></table></div>"
            counts = max(counts, len(ret))
            if not discovery:
                break
            else:
                text += f'<h4 class="text-warning">Rerunning for new sensitive attributes</h4>'

    text = f"""
        <div class="container mt-4">
            {'<h1 class="text-success">No concern</h1>' if counts==0 else '<h1 class="text-danger">Biased intersections of up to '+str(counts)+' attributes</h1>'}
            {"" if len(dataset.numeric) == 0 else "<p><b>Numeric attributes have been ignored; the scan can work with only categorical ones.</b></p>"}
            <p>After scanning for imbalances, the following attribute combinations out of those that were
            <i>not</i> already marked as sensitive were found to be underestimated. {'The scan was run in discovery mode, so the process added all indicated sensitive attributes to sensitive ones and retrying the analysis. This was repeated until no more suspicions were shed on data.' if discovery else 'There may be more attribute combinations that could be underestimated, but only the top one is presented here.'}
            Not all found attributes should necessarily be protected, and you should account only for the discovered
            intersection.</p>
            {text}
        </div>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">",
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>"
        """

    return HTML(text)

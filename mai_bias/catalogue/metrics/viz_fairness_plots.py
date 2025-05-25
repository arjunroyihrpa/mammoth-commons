# Author: Swati Swati (swati17293@gmail.com, swati.swati@unibw.de)
"""
Fairness Visualization Report Generator
This module generates a detailed fairness plots using the Fairlearn library, providing both group-wise and scalar fairness metrics across sensitive attributes such as sex or race.
"""

from mammoth_commons.datasets import CSV
from mammoth_commons.exports import HTML
from mammoth_commons.models import Predictor
from mammoth_commons.integration import metric

from typing import List


@metric(
    namespace="mammotheu",
    version="v0001",
    python="3.13",
    packages=("fairlearn", "plotly", "pandas", "onnxruntime", "mmm-fair", "skl2onnx"),
)
def viz_fairness_plots(
    dataset: CSV,
    model: Predictor,
    sensitive: List[str],
) -> HTML:
    """
    <p>
    This module visualizes fairness metrics using the <a href="https://fairlearn.org/" target="_blank">Fairlearn</a> library and interactive Plotly charts.
    It provides visual insights into how a model performs across different groups defined by sensitive features such as gender, race, or age.
    </p>
    <p>
        The module produces two sets of visual outputs:
    </p>
    <ul>
        <li><strong>Group-wise metrics</strong>: Shown as grouped bar charts, these display performance metrics (e.g., false positive rate) across subgroups.</li>
        <li><strong>Scalar metrics</strong>: Displayed as horizontal bar charts, these summarize disparities (e.g., equal opportunity difference) in a compact, interpretable format.</li>
    </ul>
    <p>
        Interactive charts allow users to hover for precise values, compare metrics between groups, and quickly identify fairness gaps.
        An explanation panel is included to define each metric and guide interpretation.
    </p>
    <p>
        This module is well suited for exploratory analysis, presentations, and fairness monitoring.
        It makes group disparities visible and intuitive, helping identify where further scrutiny or mitigation may be needed.
    </p>
    """

    # Import the existing function from mmm-fair
    from mmm_fair.fairlearn_report import generate_reports_from_fairlearn

    # Extract predictions and ground truth
    if hasattr(model, "mmm"):
        model = model.mmm
    y_true = list(dataset.labels.values())[-1]
    y_pred = model.predict(dataset, sensitive)

    # Convert sensitive attributes into the expected numpy array format
    import numpy as np

    sa_df = dataset.data[sensitive].copy()
    sa_matrix = sa_df.to_numpy()

    # Force the first group in each sensitive column to be privileged (0), rest as 1
    for col_idx, attr in enumerate(sensitive):
        col = sa_matrix[:, col_idx]
        first_group = col[0]  # Treat first seen value as privileged
        sa_matrix[:, col_idx] = np.where(col == first_group, 0, 1)

    sa_matrix = sa_matrix.astype(int)

    # Call the original report function from mmm-fair (already supports console/table/html)
    html_string = generate_reports_from_fairlearn(
        report_type="html",  # one could also use "table" if preferred
        sensitives=sensitive,
        mmm_classifier=model,
        saIndex_test=sa_matrix,
        y_pred=y_pred,
        y_test=y_true,
        launch_browser=False,  # suppresses opening in a new browser
    )

    return HTML(html_string)

import pandas as pd

from mammoth_commons.datasets import Dataset
from mammoth_commons.models import Predictor
from mammoth_commons.exports import HTML
from typing import Dict, List
from mammoth_commons.integration import metric, Options
from mammoth_commons.externals import fb_categories, align_predictions_labels
import fairbench as fb


@metric(
    namespace="mammotheu",
    version="v0038",
    python="3.12",
    packages=("fairbench", "pandas", "onnxruntime", "ucimlrepo", "pygrank"),
)
def model_card(
    dataset: Dataset,
    model: Predictor,
    sensitive: List[str],
    intersectional: bool = False,
    compare_groups: Options("Pairwise", "To the total population") = None,
    minimum_shown_deviation: float = 0.1,
) -> HTML:
    """
    <p>Generates a fairness and bias report using the <a href="https://github.com/mever-team/FairBench">FairBench</a>
    library. This explores many kinds of bias to paint a broad picture and help you decide on what is problematic
    and what is acceptable behavior.
    The generated report can be viewed in three different formats, where the model card contains a subset of
    results but attaches to these socio-technical concerns to be taken into account:</p>
    <ol>
        <li>A summary table of results.</li>
        <li>A simplified model card that includes concerns.</li>
        <li>The full report, including details.</li>
    </ol>

    <p>The module's report summarizes how a model behaves on a provided dataset across different population groups.
    These groups are based on sensitive attributes like gender, age, and race. Each attribute can have multiple values,
    such as several genders or races. Numeric attributes, like age, are normalized to the range [0,1] and treated
    as fuzzy values, where 0 indicates membership to a fuzzy group of "small" values, and 1 indicates membership to
    a fuzzy group of "large" values. A separate set of fairness metrics is calculated for each prediction label.</p>

    <p>If intersectional subgroup analysis is enabled, separate subgroups are created for each combination of sensitive
    attribute values. However, if there are too many attributes, some groups will be small or empty. Empty groups are
    ignored in the analysis. The report may also include information about built-in datasets.</p>

    Args:
        intersectional: Whether to consider all non-empty group intersections during analysis. This does nothing if there is only one sensitive attribute. It could be computationally intensive if too many group intersections are selected.
        compare_groups: Whether to compare groups pairwise, or each group to the behavior of the whole population.
        minimum_shown_deviation: Show only results where the deviation from ideal values exceeds the given threshold. If nothing is shown, fairness is not necessarily achieved, but this is a good way to identify the most prominent biases. If value of 0 is set, all report values are shown, including those that have no set ideal value.
    """

    assert len(sensitive) != 0, "At least one sensitive attribute should be selected"
    predictions = model.predict(dataset, sensitive)
    labels = dataset.labels
    sensitive = fb.Dimensions(
        {attr: fb_categories(dataset.data[attr]) for attr in sensitive}
    )

    if intersectional:
        sensitive = sensitive.intersectional()
    report_type = (
        fb.reports.pairwise if compare_groups == "Pairwise" else fb.reports.vsall
    )

    predictions, labels = align_predictions_labels(predictions, labels)
    report = report_type(predictions=predictions, labels=labels, sensitive=sensitive)
    minimum_shown_deviation = float(minimum_shown_deviation)
    assert (
        0 <= minimum_shown_deviation <= 1
    ), "Minimum shown deviation should be in the range [0,1]"
    if minimum_shown_deviation != 0:
        report = report.filter(fb.investigate.DeviationsOver(minimum_shown_deviation))

    views = {
        "Summary": report.show(env=fb.export.HtmlTable(view=False, filename=None)),
        "Stamps": report.filter(fb.investigate.Stamps).show(
            env=fb.export.Html(view=False, filename=None),
            depth=2 if isinstance(predictions, dict) else 1,
        ),
        "Full report": report.show(
            env=fb.export.Html(view=False, filename=None),
            depth=3 if isinstance(predictions, dict) else 2,
        ),
    }
    tab_headers = "".join(
        f'<button class="tablinks" data-tab="{key}">{key}</button>' for key in views
    )
    tab_contents = "".join(
        f'<div id="{key}" class="tabcontent">{value}</div>'
        for key, value in views.items()
    )

    dataset_desc = dataset.format_description()

    html_content = f"""
       <style>
           .tablinks {{
               background-color: #ddd;
               padding: 10px;
               cursor: pointer;
               border: none;
               border-radius: 5px;
               margin: 5px;
           }}
           .tablinks:hover {{ background-color: #bbb; }}
           .tablinks.active {{ background-color: #aaa; }}

           .tabcontent {{
               display: none;
               padding: 10px;
               border: 1px solid #ccc;
           }}
           .tabcontent.active {{ display: block; }}
       </style>
       <script>
           document.addEventListener("DOMContentLoaded", function() {{
               const tabContainer = document.querySelector("div");
               tabContainer.addEventListener("click", function(event) {{
                   if (event.target.classList.contains("tablinks")) {{
                       let tabName = event.target.getAttribute("data-tab");
                       document.querySelectorAll(".tablinks").forEach(tab => tab.classList.remove("active"));
                       document.querySelectorAll(".tabcontent").forEach(content => content.classList.remove("active"));
                       event.target.classList.add("active");
                       document.getElementById(tabName).classList.add("active");
                   }}
               }});

               // Show the first tab by default
               let firstTab = document.querySelector(".tablinks");
               if (firstTab) {{
                   firstTab.classList.add("active");
                   document.getElementById(firstTab.getAttribute("data-tab")).classList.add("active");
               }}
           }});
       </script>
       <h1>{f'Report over {len(sensitive.branches())} groups' if minimum_shown_deviation == 0 else f'Report over {len(sensitive.branches())} groups for {minimum_shown_deviation:.3f} deviations'}</h1>
       <p>A report was computed over several prospective biases. 
       The following {len(sensitive.branches())} protected groups were analysed: <i>{', '.join(sensitive.branches().keys())}</i>.
       </p><p>Several values are computed to paint a broad picture
       {'; set a minimum shown deviation parameter for this analysis to simplify what is shown.' if minimum_shown_deviation == 0 else f', but for simplicity only those that differ at least {minimum_shown_deviation:.3f} from their ideal values are shown; this is the minimum shown deviation parameter of the analysis.'}
       Results may not give the full picture, and not all biases may be harmful to the social context. Switch between different views.</p>
       <div>{tab_headers}</div>
       <div>{tab_contents}</div>
       <div style="clear: both;">{dataset_desc}</div>
       """

    return HTML(html_content)

from mammoth.datasets import CSV
from mammoth.models import EmptyModel
from mammoth.exports import HTML
from typing import Dict, List
from mammoth.integration import metric, Options
import fairbench as fb
import numpy as np
from mammoth.integration_callback import notify_progress, notify_end
from mammoth.externals import fb_categories


@metric(
    namespace="mammotheu",
    version="v0038",
    python="3.12",
    packages=(
        "fairbench",
        "scikit-learn",
        "pandas",
        "onnxruntime",
        "ucimlrepo",
        "pygrank",
    ),
)
def sklearn_audit(
    dataset: CSV,
    model: EmptyModel,
    sensitive: List[str],
    predictor: Options("Logistic regression", "Gaussian naive Bayes") = None,
    intersectional: bool = False,
    compare_groups: Options("Pairwise", "To the total population") = None,
    minimum_shown_deviation: float = 0.1,
) -> HTML:
    """
    <p>One way to evaluate the fairness of a dataset is by testing for biases using simple models with limited
    degrees of freedom. This module audits datasets by training such models provided by the
    <a href="https://scikit-learn.org/stable/index.html">scikit-learn</a> library on half of the dataset.
    The second half is then used as test data to assess predictive performance and detect classification
    or scoring biases.</p>

    <p>Test data are used to generate a fairness and bias report using the
    <a href="https://fairbench.readthedocs.io/">FairBench</a> library. If strong biases appear in the simple models
    that are explored, they may also persist in more complex models trained on the same data. To focus on the most
    significant biases, adjust the minimum shown deviation parameter.
    The report provides multiple types of fairness and bias assessments and can be viewed in three different formats,
    where the model card contains a subset of results but attaches to these socio-technical concerns to be taken into
    account:</p>
    <ol>
        <li>A summary table of results.</li>
        <li>A simplified model card with key fairness concerns.</li>
        <li>A full detailed report.</li>
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
        predictor: Which simple model should be used.
        intersectional: Whether to consider all non-empty group intersections during analysis. This does nothing if there is only one sensitive attribute. It could be computationally intensive if too many group intersections are selected.
        compare_groups: Whether to compare groups pairwise, or each group to the behavior of the whole population.
        minimum_shown_deviation: Show only results where the deviation from ideal values exceeds the given threshold. If nothing is shown, fairness is not necessarily achieved, but this is a good way to identify the most prominent biases. If value of 0 is set, all report values are shown, including those that have no set ideal value.
    """
    assert len(sensitive) != 0, "Set at least one sensitive attribute"
    X = dataset.to_features(sensitive)
    y = dataset.labels
    if isinstance(y, dict):
        y = y[list(y.keys())[0]]
    else:
        assert (
            y.shape[1] <= 2
        ), "Cannot create an sklearn report for non-binary predictions"
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
        from sklearn.exceptions import ConvergenceWarning
        import warnings

        warnings.simplefilter("ignore", ConvergenceWarning)
        model = LogisticRegression(max_iter=1, warm_start=True)
        for i in range(1000):
            model.fit(X, y)
            notify_progress(
                (i + 1) / 1000,
                f"Training a logistic regression classifier for {i+1}/{1000} epochs",
            )
    else:
        from sklearn.naive_bayes import GaussianNB

        model = GaussianNB()
        batch_size = 100
        unique_classes = np.unique(y)
        for i in range(0, len(y), batch_size):
            X_batch = X[i : i + batch_size]
            y_batch = y[i : i + batch_size]
            model.partial_fit(X_batch, y_batch, classes=unique_classes)
            notify_progress(
                min(1.0, (i + batch_size) / len(X)),
                f"Fitting a Gaussian naive Bayes classifier on {i}/{len(y)} data points",
            )

    notify_end()
    predictions = model.predict(X_test)
    scores = model.predict_proba(X_test)[:, 1]
    sensitive = fb.Dimensions(
        {attr + " ": fb_categories(dataset.data[attr][idx_test]) for attr in sensitive}
    )

    if intersectional:
        sensitive = sensitive.intersectional()
    report_type = (
        fb.reports.pairwise if compare_groups == "Pairwise" else fb.reports.vsall
    )

    report = report_type(
        predictions=predictions,
        labels=y_test.to_numpy(),
        scores=scores,
        sensitive=sensitive,
    )
    minimum_shown_deviation = float(minimum_shown_deviation)
    assert (
        0 <= minimum_shown_deviation <= 1
    ), "Minimum shown deviation should be in the range [0,1]"
    if minimum_shown_deviation != 0:
        report = report.filter(fb.investigate.DeviationsOver(minimum_shown_deviation))

    views = {
        "Summary": report.show(env=fb.export.HtmlTable(view=False, filename=None)),
        "Stamps": report.filter(fb.investigate.Stamps).show(
            env=fb.export.Html(view=False, filename=None), depth=1
        ),
        "Full report": report.show(
            env=fb.export.Html(view=False, filename=None), depth=2
        ),
    }
    # Generate tabbed HTML content
    tab_headers = "".join(
        f'<button class="tablinks" data-tab="{key}">{key}</button>' for key in views
    )
    tab_contents = "".join(
        f'<div id="{key}" class="tabcontent">{value}</div>'
        for key, value in views.items()
    )

    dataset_desc = ""
    if hasattr(dataset, "description"):
        dataset_desc += "<h1>Dataset</h1>"
        if isinstance(dataset.description, str):
            dataset_desc += dataset.description + "<br>"
        elif isinstance(dataset.description, dict):
            for key, value in dataset.description.items():
                dataset_desc += f"<h3>{key}</h3>" + value.replace("\n", "<br>") + "<br>"
        else:
            raise Exception("Dataset description must be a string or a dictionary.")

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

                       // Remove "active" from all tabs and contents
                       document.querySelectorAll(".tablinks").forEach(tab => tab.classList.remove("active"));
                       document.querySelectorAll(".tabcontent").forEach(content => content.classList.remove("active"));

                       // Activate the selected tab and content
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
       <h1>{f'Audit of {len(sensitive.branches())} groups' if minimum_shown_deviation==0 else f'Audit of {len(sensitive.branches())} groups for {minimum_shown_deviation:.3f} deviations'}</h1>
       <p>A report was computed over several prospective biases
       when a {predictor} model is trained. 
       The following {len(sensitive.branches())} protected groups were analysed: <i>{', '.join(sensitive.branches().keys())}</i>.
       </p><p>Several values are computed to paint a broad picture
       {'; set a minimum shown deviation parameter for this analysis to simplify what is shown.' if minimum_shown_deviation==0 else f', but for simplicity only those that differ at least {minimum_shown_deviation:.3f} from their ideal values are shown; this is the minimum shown deviation parameter of the analysis.'}
       Results may not give the full picture, and not all biases may be harmful to the social context. Switch between different views.</p>
       <div>{tab_headers}</div>
       {tab_contents}
       {dataset_desc}
       """
    return HTML(html_content)

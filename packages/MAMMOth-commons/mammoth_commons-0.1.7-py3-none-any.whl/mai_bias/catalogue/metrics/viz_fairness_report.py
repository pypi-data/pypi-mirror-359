# Author: Swati Swati (swati17293@gmail.com, swati.swati@unibw.de)
"""
Fairness Visualization Report Generator
This module generates a detailed fairness report using the Fairlearn library, providing both group-wise and scalar fairness metrics across sensitive attributes such as sex or race.
"""

from mammoth_commons.datasets import Dataset
from mammoth_commons.exports import HTML
from mammoth_commons.models import Predictor
from mammoth_commons.integration import metric

from typing import List


@metric(
    namespace="mammotheu",
    version="v0001",
    python="3.13",
    packages=(
        "fairlearn",
        "plotly",
        "pandas",
        "onnxruntime",
        "mmm-fair-cli",
        "skl2onnx",
    ),
)
def viz_fairness_report(
    dataset: Dataset,
    model: Predictor,
    sensitive: List[str],
) -> HTML:
    """
    <p>
        This module generates a structured fairness report using the <a href="https://fairlearn.org/" target="_blank">Fairlearn</a> library.
        It assesses whether a machine learning model behaves similarly across different population groups, as defined by sensitive attributes such as gender, race, or age.
    </p>
    <p>
        The report includes two types of fairness metrics:
    </p>
    <ul>
        <li><strong>Group-wise metrics</strong>: These show how the model performs for each group separately (e.g., true positive rates for Group A vs. Group B).</li>
        <li><strong>Scalar metrics</strong>: These summarize disparities across groups into single numeric values. Small differences and ratios close to 1 indicate balanced treatment.</li>
    </ul>
    <p>
        Results are presented in aligned tables with clear formatting, allowing users to compare outcomes across groups at a glance.
        Each metric is briefly explained to help interpret whether the model exhibits performance or outcome disparities for different groups.
    </p>
    <p>
        This module is particularly useful in evaluation pipelines, audit reports, and model reviews where transparency and fairness are essential.
        It helps teams assess group-level equity in model behavior using interpretable, tabular summaries.
    </p>
    """
    from mmm_fair_cli.fairlearn_report import generate_reports_from_fairlearn
    import numpy as np

    if hasattr(model, "mmm"):
        model = model.mmm
    y_pred = model.predict(dataset, sensitive)
    dataset = dataset.to_csv(sensitive)
    y_true = list(dataset.labels.columns.values())[-1]

    sa_df = dataset.df[sensitive].copy()
    sa_matrix = sa_df.to_numpy()

    # Force the first group in each sensitive column to be privileged (0), rest as 1
    for col_idx, attr in enumerate(sensitive):
        col = sa_matrix[:, col_idx]
        first_group = col[0]  # Treat first seen value as privileged
        sa_matrix[:, col_idx] = np.where(col == first_group, 0, 1)

    sa_matrix = sa_matrix.astype(int)

    # Call the original report function from mmm-fair (already supports console/table/html)
    html_string = generate_reports_from_fairlearn(
        report_type="table",  # one could also use "table" if preferred
        sensitives=sensitive,
        mmm_classifier=model,
        saIndex_test=sa_matrix,
        y_pred=y_pred,
        y_test=y_true,
        launch_browser=False,  # suppresses opening in a new browser
    )

    return HTML(html_string)

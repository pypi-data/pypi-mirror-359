# ml-drift-detection 📈🔍

**Streamlit dashboard for rapid visual monitoring of data drift and model-performance metrics**

![PyPI Version](https://img.shields.io/pypi/v/ml-drift-detection?color=blue)
![PyPI Downloads](https://img.shields.io/pypi/dm/ml-drift-detection)
![Python Versions](https://img.shields.io/pypi/pyversions/ml-drift-detection)
![License](https://img.shields.io/github/license/knowusuboaky/ml-drift-detection)

---

## Why use it?

* **One command → full dashboard** – point at two files (baseline & new batch) and instantly see  
  * Feature-level drift (numeric & categorical)  
  * Label drift & concept drift  
  * Metric deltas with colour-coded gauges
* Zero vendor lock-in: pure Streamlit + Plotly; runs anywhere Python runs.
* Works as **both** a command-line tool **and** an importable library.

---

## Default visual settings

| Setting | Default value |
|---------|---------------|
| **Background** | `"white"` (pass `--background-color="#0E1117"` for dark mode) |
| **Gauge colour bands** | *Relative delta bands for each metric*<br>`[-1.0 – -0.10] → firebrick`<br>`[-0.10 – -0.05] → orange`<br>`[-0.05 –  0.05] → green`<br>`[ 0.05 –  1.00] → #2ca02c` |

You can override the bands per metric with `--metric-one-threshold-steps`,  
`--metric-two-threshold-steps`, etc. Any argument left empty (`[]`) falls back to these defaults.

---

## Installation

```bash
pip install ml-drift-detection
# optional dev / test extras
pip install -e ".[dev,test]"
```

Requires **Python ≥ 3.9**. See `pyproject.toml` for full dependency list.

---

## Quick-start (CLI)

```bash
streamlit run -m ml_drift_detection.cli -- \
  --prod-data=prod_df.csv \
  --new-data=new_df.csv \
  --numeric-cols=age,income,loan_amount \
  --categorical-cols=gender,region,plan \
  --target-variable=subscription_type \
  --target-type=categorical \
  --prod-metrics=accuracy=0.91,f1=0.88 \
  --new-metrics=accuracy=0.83,f1=0.79 \
  --background-color="#0E1117" \
  --metric-one-threshold-steps="[{'range':[-1,-0.1],'color':'red'},{'range':[-0.1,0.05],'color':'orange'},{'range':[0.05,1],'color':'green'}]"
```

<details>
<summary><b>Windows PowerShell multi-line example</b></summary>

```powershell
streamlit run "C:\Python\Lib\site-packages\ml_drift_detection\cli.py" -- `
  --prod-data="C:\data\prod_df.csv" `
  --new-data="C:\data\new_df.csv" `
  --numeric-cols="age,income,loan_amount" `
  --categorical-cols="gender,region,plan" `
  --target-variable="subscription_type" `
  --target-type="categorical" `
  --prod-metrics="accuracy=0.91,f1=0.88" `
  --new-metrics="accuracy=0.83,f1=0.79"
```

</details>

---

## Programmatic use

```python
from ml_drift_detection import dashboard_main
import pandas as pd

prod_df = pd.read_csv("prod_df.csv")
new_df  = pd.read_csv("new_df.csv")

dashboard_main(
    prod_df=prod_df,
    new_df=new_df,
    numeric_cols=["age", "income", "loan_amount"],
    categorical_cols=["gender", "region", "plan"],
    target_variable="subscription_type",
    target_type="categorical",
    prod_metrics={"accuracy": 0.91, "f1": 0.88},
    new_metrics={"accuracy": 0.83, "f1": 0.79},
)
```

---

## Public API (mini)

| Symbol                                                      | Purpose                                        |
| ----------------------------------------------------------- | ---------------------------------------------- |
| `ml_drift_detection.cli_main`                               | CLI entry-point (invoked by the command above) |
| `ml_drift_detection.dashboard_main`                         | Programmatic dashboard launcher                |
| `check_numeric_stats / check_categorical_stats`             | Produce pandas summaries of drift metrics      |
| `get_plotly_dist / get_plotly_barplot / get_plotly_boxplot` | Stand-alone Plotly figure builders             |

---

## Contributing 🤝

```bash
git clone https://github.com/knowusuboaky/ml-drift-detection
cd ml-drift-detection
pip install -e ".[dev,test]"
pre-commit install
pytest
```

Bug reports & feature requests welcome – open an issue first for large changes.

---

## License

MIT © Kwadwo Daddy Nyame Owusu-Boakye

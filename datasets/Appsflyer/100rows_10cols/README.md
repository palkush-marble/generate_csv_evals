# Appsflyer Dataset - 100 Rows

Generated on: 2025-10-16T13:50:38.485799

## Structure

```
datasets/Appsflyer/
├── appsflyer_sample.csv              # Original sample file
└── 100/
    ├── appsflyer_synthetic_100rows_10cols.csv       # Synthetic data (100 rows)
    ├── eval_dataset_all.json            # All evaluation cases
    ├── eval_dataset_aggregation.json    # Data aggregation tests
    ├── eval_dataset_time_comparison.json # Time comparison tests
    └── eval_dataset_custom_metrics.json  # Custom metrics tests
```

## Synthetic Data

- **File**: `appsflyer_synthetic_100rows_10cols.csv`
- **Rows**: 100
- **Columns**: 10
- **File Size**: 0.01 MB

### Column Summary
- Numeric columns: 4
- Categorical columns: 6
- Date columns: Date

### Date Range
- Start: 2024-01-10
- End: 2025-12-28

## Evaluation Datasets

Total test cases: **50**

### Data Aggregation
- Test cases: **25**
- Description: Test cases for grouping and aggregating data with sum, avg, min, max

### Time Period Comparison
- Test cases: **20**
- Description: Test cases for comparing metrics between different time periods

### Custom Metrics
- Test cases: **5**
- Description: Test cases for calculating and aggregating custom business metrics

## Files Generated

| File | Size | Description |
|------|------|-------------|
| `appsflyer_synthetic_100rows_10cols.csv` | 0.01 MB | Synthetic data |
| `eval_dataset_all.json` | 46.5 KB | Combined |\n| `eval_dataset_aggregation.json` | 21.1 KB | Aggregation |\n| `eval_dataset_time_comparison.json` | 17.4 KB | Time Comparison |\n| `eval_dataset_custom_metrics.json` | 2.9 KB | Custom Metrics |\n
## Usage

### Load Synthetic Data
```python
import pandas as pd

df = pd.read_csv('appsflyer_synthetic_100rows_10cols.csv')
print(df.head())
```

### Load Evaluation Cases
```python
import json

with open('eval_dataset_all.json', 'r') as f:
    eval_data = json.load(f)

# Access specific category
for case in eval_data['categories']['data_aggregation']['cases']:
    print(case['question'])
    print(case['expected_result'])
```

### Test Your AI Agent
```python
# See ../../../example_eval_usage.py for complete example
from example_eval_usage import run_evaluation

run_evaluation('eval_dataset_all.json', 'appsflyer_synthetic_100rows_10cols.csv')
```

## Next Steps

1. Use the synthetic data to test your AI agent
2. Validate against the evaluation datasets
3. Track accuracy across different categories
4. Generate more data with different row counts if needed

---
Generated with `main.py`

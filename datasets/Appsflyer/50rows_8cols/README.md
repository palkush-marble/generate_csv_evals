# Appsflyer Dataset - 50 Rows

Generated on: 2025-10-16T14:13:21.244920

## Structure

```
datasets/Appsflyer/
├── appsflyer_sample.csv              # Original sample file
└── 50/
    ├── appsflyer_synthetic_50rows_8cols.csv       # Synthetic data (50 rows)
    ├── eval_dataset_all.json            # All evaluation cases
    ├── eval_dataset_aggregation.json    # Data aggregation tests
    ├── eval_dataset_time_comparison.json # Time comparison tests
    └── eval_dataset_custom_metrics.json  # Custom metrics tests
```

## Synthetic Data

- **File**: `appsflyer_synthetic_50rows_8cols.csv`
- **Rows**: 50
- **Columns**: 8
- **File Size**: 0.00 MB

### Column Summary
- Numeric columns: 2
- Categorical columns: 6
- Date columns: Date

### Date Range
- Start: 2024-01-13
- End: 2025-12-25

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
| `appsflyer_synthetic_50rows_8cols.csv` | 0.00 MB | Synthetic data |
| `eval_dataset_all.json` | 47.4 KB | Combined |\n| `eval_dataset_aggregation.json` | 19.3 KB | Aggregation |\n| `eval_dataset_time_comparison.json` | 19.2 KB | Time Comparison |\n| `eval_dataset_custom_metrics.json` | 3.3 KB | Custom Metrics |\n
## Usage

### Load Synthetic Data
```python
import pandas as pd

df = pd.read_csv('appsflyer_synthetic_50rows_8cols.csv')
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

run_evaluation('eval_dataset_all.json', 'appsflyer_synthetic_50rows_8cols.csv')
```

## Next Steps

1. Use the synthetic data to test your AI agent
2. Validate against the evaluation datasets
3. Track accuracy across different categories
4. Generate more data with different row counts if needed

---
Generated with `main.py`

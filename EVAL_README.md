# Evaluation Dataset Generator

This script generates comprehensive evaluation datasets for testing AI agents on marketing data analysis tasks.

## Overview

The evaluation datasets cover three main categories:

1. **Data Aggregation** - Group by operations with sum, average, min, max, count
2. **Time Period Comparison** - Comparing metrics between different time ranges
3. **Custom Metrics** - Calculating and aggregating custom business formulas

## Generated Files

- `eval_dataset_all.json` - Combined dataset with all eval cases
- `eval_dataset_aggregation.json` - Data aggregation test cases only
- `eval_dataset_time_comparison.json` - Time period comparison test cases only
- `eval_dataset_custom_metrics.json` - Custom metrics test cases only

## Usage

### Generate Eval Datasets

```bash
python3 generate_eval_datasets.py my_data.csv --output-dir .
```

### Options

```bash
python3 generate_eval_datasets.py --help

Arguments:
  data_csv              Path to synthetic data CSV file
  
Options:
  --output-dir, -o      Output directory for eval files (default: .)
  --agg-cases          Number of aggregation eval cases (default: 20)
  --time-cases         Number of time comparison eval cases (default: 15)
  --custom-cases       Number of custom metrics eval cases (default: 15)
```

### Custom Generation

```bash
# Generate more eval cases
python3 generate_eval_datasets.py my_data.csv --agg-cases 50 --time-cases 30 --custom-cases 30

# Save to different directory
python3 generate_eval_datasets.py my_data.csv --output-dir ./evals
```

## Eval Case Format

Each evaluation case includes:

- `id` - Unique identifier
- `category` - Category of the eval case
- `question` - Natural language question
- `operation` - Expected operation/query description
- `expected_result` - Ground truth answer
- `difficulty` - Difficulty level (medium/hard)

### Example: Data Aggregation

```json
{
  "id": "agg_1",
  "category": "data_aggregation",
  "question": "What is the min of overlay_permission_not_given (Event counter) by Conversion Type?",
  "operation": "GROUP BY Conversion Type, MIN(overlay_permission_not_given (Event counter))",
  "group_by_column": "Conversion Type",
  "metric_column": "overlay_permission_not_given (Event counter)",
  "aggregation_function": "min",
  "expected_result": {
    "new install": 0.0,
    "other": 0.0,
    "re-attribution": 0.0
  },
  "difficulty": "medium"
}
```

### Example: Time Period Comparison

```json
{
  "id": "time_comp_1",
  "category": "time_period_comparison",
  "question": "Compare the total booking_done_6_fos (Sales in INR) between 2024-10-15 to 2025-04-14 and 2025-04-15 to 2025-10-15. What is the difference?",
  "metric_column": "booking_done_6_fos (Sales in INR)",
  "time_period_1": {
    "start": "2024-10-15",
    "end": "2025-04-14",
    "value": 7752.15
  },
  "time_period_2": {
    "start": "2025-04-15",
    "end": "2025-10-15",
    "value": 7611.02
  },
  "expected_result": {
    "period_1_value": 7752.15,
    "period_2_value": 7611.02,
    "absolute_difference": -141.13,
    "percent_change": -1.82
  },
  "difficulty": "medium"
}
```

### Example: Custom Metrics

```json
{
  "id": "custom_metric_1",
  "category": "custom_metrics",
  "question": "Calculate the median Revenue Per Session across all records. Formula: Total Revenue / Sessions",
  "metric_name": "Revenue Per Session",
  "metric_formula": "Total Revenue / Sessions",
  "metric_description": "Average revenue per session",
  "aggregation_function": "median",
  "required_columns": ["Total Revenue", "Sessions"],
  "expected_result": 0.2,
  "difficulty": "medium"
}
```

## Evaluation Categories

### 1. Data Aggregation

Tests the AI agent's ability to:
- Group data by single or multiple columns
- Apply aggregation functions (sum, average, min, max, count)
- Handle NULL values appropriately
- Return results in correct format

**Difficulty Levels:**
- Medium: Single group by column
- Hard: Multiple group by columns

### 2. Time Period Comparison

Tests the AI agent's ability to:
- Filter data by date ranges
- Compare metrics between two time periods
- Calculate absolute and percentage differences
- Handle grouped time comparisons

**Difficulty Levels:**
- Medium: Simple time period comparison
- Hard: Time period comparison with grouping

### 3. Custom Metrics

Tests the AI agent's ability to:
- Calculate custom business metrics using formulas
- Handle division by zero cases
- Aggregate custom metrics
- Group custom metrics by dimensions

**Built-in Custom Metrics:**
- ROI: `(Total Revenue - Total Cost) / Total Cost * 100`
- Conversion Rate: `Conversions / Clicks * 100`
- Cost Per Conversion: `Total Cost / Conversions`
- Revenue Per Session: `Total Revenue / Sessions`
- Profit Margin: `(Total Revenue - Total Cost) / Total Revenue * 100`

**Difficulty Levels:**
- Medium: Simple custom metric calculation
- Hard: Custom metric with grouping

## Using Evals for Testing

### Python Example

```python
import json
import pandas as pd

# Load eval dataset
with open('eval_dataset_all.json') as f:
    eval_data = json.load(f)

# Load your data
df = pd.read_csv('my_data.csv')

# Test your AI agent
for category, info in eval_data['categories'].items():
    for case in info['cases']:
        # 1. Send question to your AI agent
        agent_answer = your_ai_agent.answer(case['question'], df)
        
        # 2. Compare with expected result
        expected = case['expected_result']
        
        # 3. Calculate accuracy
        is_correct = compare_results(agent_answer, expected)
        
        print(f"Case {case['id']}: {'✅' if is_correct else '❌'}")
```

### Evaluation Metrics

You can measure:
- **Accuracy**: Percentage of correct answers
- **Category Performance**: Accuracy per category
- **Difficulty Performance**: Accuracy by difficulty level
- **Error Analysis**: Common failure patterns

## Data Requirements

The generator works with any CSV containing:
- At least one date column named `Date`
- Numeric columns for metrics
- Categorical columns for grouping

For best results:
- Include at least 1000 rows
- Have a date range spanning multiple months
- Include relevant business metrics

## Tips

1. **Validate Results**: The expected results are calculated from your synthetic data
2. **Tolerance**: Consider using tolerance for floating-point comparisons (e.g., ±0.01)
3. **NULL Handling**: Some cases may have NULL values - ensure your agent handles them
4. **Date Formats**: Dates are in YYYY-MM-DD format
5. **Custom Evals**: Modify the script to add your own custom metrics

## Troubleshooting

**Issue**: Not enough time comparison cases generated
- **Solution**: Ensure your data has a date range spanning at least 30 days

**Issue**: Custom metric calculations return NULL
- **Solution**: Check that required columns exist and have non-zero values

**Issue**: Expected results don't match actual calculations
- **Solution**: Verify the data preprocessing (handling of NaN, zeros, etc.)

## Extending the Generator

Add your own custom metrics in the `generate_custom_metrics_evals` method:

```python
custom_metrics = [
    {
        "name": "Your Metric",
        "formula": "Column1 / Column2 * 100",
        "columns": ["Column1", "Column2"],
        "description": "Description of your metric"
    },
    # ... add more
]
```

## License

MIT


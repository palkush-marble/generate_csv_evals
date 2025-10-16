# Synthetic Data & Evaluation Generator

AI-powered tool to generate synthetic data and comprehensive evaluation datasets for testing AI agents. Uses Google's Gemini AI to create realistic data matching your patterns.

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set API key in .env file (already done if you have one)
echo "GEMINI_API_KEY=your_key_here" > .env

# 3. Generate everything with one command!
python3 main.py appsflyer.csv --rows 5000 --columns 20
```

**That's it!** Creates organized folder with synthetic data + evaluation datasets.

---

## 📁 What You Get

```
datasets/
└── Appsflyer/
    ├── appsflyer_sample.csv
    └── 5000rows_20cols/
        ├── appsflyer_synthetic_5000rows_20cols.csv    # Your data
        ├── eval_dataset_all.json                      # 65+ test cases
        ├── eval_dataset_aggregation.json              # 25 cases
        ├── eval_dataset_time_comparison.json          # 20 cases
        ├── eval_dataset_custom_metrics.json           # 20 cases
        └── README.md                                   # Dataset docs
```

---

## 📖 Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Command Options](#command-options)
- [Examples](#examples)
- [Evaluation Datasets](#evaluation-datasets)
- [Features](#features)
- [Folder Structure](#folder-structure)
- [Troubleshooting](#troubleshooting)

---

## Installation

### Requirements
- Python 3.8+
- Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

### Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set API key (choose one method)

# Method 1: .env file (recommended)
echo "GEMINI_API_KEY=your_api_key_here" > .env

# Method 2: Environment variable
export GEMINI_API_KEY=your_api_key_here

# Method 3: Pass as argument
python3 main.py data.csv --rows 5000 --api-key YOUR_KEY
```

---

## Usage

### Basic Usage

```bash
# Generate with all columns
python3 main.py appsflyer.csv --rows 5000

# Generate with specific number of columns
python3 main.py appsflyer.csv --rows 5000 --columns 20

# Quick test (100 rows, 10 columns)
python3 main.py appsflyer.csv --rows 100 --columns 10
```

### What Happens

1. **Analyzes** your sample CSV
2. **Uses Gemini AI** to generate row creation function
3. **Creates synthetic data** matching your patterns
4. **Generates evaluation datasets** (65+ test cases)
5. **Auto-generates documentation**

---

## Command Options

```bash
python3 main.py INPUT_FILE --rows ROWS [OPTIONS]
```

### Required Arguments

| Argument | Description |
|----------|-------------|
| `INPUT_FILE` | Path to your CSV file |
| `--rows, -r` | Number of rows to generate |

### Optional Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--columns, -c` | Number of columns to use | All columns |
| `--base-dir, -b` | Output directory | `datasets` |
| `--api-key, -k` | Gemini API key | From `.env` or env var |
| `--help, -h` | Show help message | - |

---

## Examples

### Basic Examples

```bash
# All columns, 5000 rows
python3 main.py appsflyer.csv --rows 5000

# First 20 columns, 5000 rows  
python3 main.py appsflyer.csv --rows 5000 --columns 20

# Quick test with 100 rows and 10 columns
python3 main.py appsflyer.csv --rows 100 --columns 10
```

### Multiple Sizes

```bash
# Generate different sizes for testing
python3 main.py appsflyer.csv --rows 100 --columns 10    # Quick test
python3 main.py appsflyer.csv --rows 1000 --columns 20   # Development
python3 main.py appsflyer.csv --rows 5000 --columns 30   # Testing
python3 main.py appsflyer.csv --rows 10000               # Production
```

### Multiple Datasets

```bash
# Generate different datasets
python3 main.py sales_data.csv --rows 5000
python3 main.py user_events.csv --rows 10000
python3 main.py marketing_metrics.csv --rows 3000
```

---

## Evaluation Datasets

Generated evaluation datasets include 65+ test cases across 3 categories:

### 1. Data Aggregation (25 cases)

Tests grouping and aggregation with sum, avg, min, max, count.

**Example:**
```json
{
  "question": "What is the sum of Total Revenue by Country?",
  "operation": "GROUP BY Country, SUM(Total Revenue)",
  "expected_result": {"US": 12345.67, "IN": 8901.23}
}
```

### 2. Time Period Comparison (20 cases)

Tests comparing metrics between different time ranges.

**Example:**
```json
{
  "question": "Compare total Conversions between Q1 and Q2",
  "expected_result": {
    "period_1_value": 1250,
    "period_2_value": 1380,
    "percent_change": 10.4
  }
}
```

### 3. Custom Metrics (20 cases)

Tests calculating custom business metrics like ROI, conversion rate, etc.

**Example:**
```json
{
  "question": "Calculate average ROI by Campaign",
  "metric_formula": "(Revenue - Cost) / Cost * 100",
  "expected_result": {"Campaign A": 45.2, "Campaign B": 38.7}
}
```

### Using Eval Datasets

```python
import json
import pandas as pd

# Load eval dataset
with open('datasets/Appsflyer/5000rows_20cols/eval_dataset_all.json') as f:
    evals = json.load(f)

# Load synthetic data
df = pd.read_csv('datasets/Appsflyer/5000rows_20cols/appsflyer_synthetic_5000rows_20cols.csv')

# Test your AI agent
for category, info in evals['categories'].items():
    for case in info['cases']:
        # Send question to your AI agent
        agent_answer = your_ai_agent.answer(case['question'], df)
        
        # Compare with expected result
        is_correct = (agent_answer == case['expected_result'])
        print(f"{case['id']}: {'✅' if is_correct else '❌'}")
```

---

## Features

### 🤖 AI-Powered Generation
- Uses Gemini AI to understand your data patterns
- Generates realistic synthetic data automatically
- Creates custom row generation function per dataset

### 📊 Flexible Configuration
- Specify number of rows (required)
- Specify number of columns (optional)
- Works with any CSV structure

### 🎯 Pattern Recognition
- Analyzes data types and formats
- Maintains realistic patterns
- Handles dates, numbers, categories

### 📝 Comprehensive Evaluations
- 65+ test cases automatically generated
- Covers aggregation, time comparison, custom metrics
- Includes ground truth answers

### 💾 Organized Output
- Clean folder structure: `datasets/DatasetName/RowsXColsY/`
- Self-documenting names
- Auto-generated documentation per dataset

### 🔄 Backward Compatible
- Works without `--columns` flag
- Existing workflows unchanged
- Progressive enhancement

---

## Folder Structure

### Automated Structure

When you run:
```bash
python3 main.py appsflyer.csv --rows 5000 --columns 20
```

You get:
```
datasets/
└── Appsflyer/                              # Auto-named from input
    ├── appsflyer_sample.csv               # Your original sample
    └── 5000rows_20cols/                   # Auto-named folder
        ├── appsflyer_synthetic_5000rows_20cols.csv
        ├── eval_dataset_all.json
        ├── eval_dataset_aggregation.json
        ├── eval_dataset_time_comparison.json
        ├── eval_dataset_custom_metrics.json
        └── README.md
```

### Multiple Configurations

You can generate multiple versions:
```
datasets/
└── Appsflyer/
    ├── appsflyer_sample.csv
    ├── 100rows_10cols/     # Quick test
    ├── 1000rows_20cols/    # Development
    ├── 5000rows_30cols/    # Testing
    └── 10000/              # Production (all columns)
```

### Dataset Name Extraction

Input files are automatically named:

| Input File | Dataset Name |
|------------|--------------|
| `appsflyer.csv` | `Appsflyer` |
| `marketing_data.csv` | `MarketingData` |
| `sales_report.csv` | `SalesReport` |
| `user_events_sample.csv` | `UserEventsSample` |

---

## Troubleshooting

### Error: GEMINI_API_KEY must be set

**Solution:**
```bash
# Add to .env file
echo "GEMINI_API_KEY=your_key_here" > .env

# Or export environment variable
export GEMINI_API_KEY=your_key_here

# Or pass as argument
python3 main.py data.csv --rows 5000 --api-key YOUR_KEY
```

### Error: File not found

**Solution:**
- Check file path is correct
- Use absolute or relative path
- Ensure file exists

### Error: Cannot choose from empty sequence

**Solution:**
- Use more columns (at least 10-15 recommended)
- Ensure sample has numeric columns
- Some columns needed for evaluations

### Slow generation?

**Normal behavior:**
- 100 rows: ~30 seconds
- 1000 rows: ~1-2 minutes
- 5000 rows: ~3-5 minutes
- AI function generation is slowest part (one-time per dataset)

**Speed it up:**
- Use fewer columns with `--columns`
- Start with smaller row counts
- Wide CSVs (100+ cols) benefit most from `--columns`

### Generated data doesn't look realistic

**Solutions:**
- Provide more sample rows (at least 5-10)
- Ensure sample data is representative
- Try running again (AI may generate better code)
- Check if sample has clear patterns

---

## Performance Guide

### Row Count Recommendations

| Rows | Use Case | Generation Time |
|------|----------|----------------|
| 50-100 | Quick tests | ~30 sec |
| 1,000 | Development | ~1-2 min |
| 5,000 | Standard testing | ~3-5 min |
| 10,000 | Load testing | ~5-10 min |
| 50,000+ | Production-like | ~20-30 min |

### Column Count Impact

For a CSV with 131 columns:

| Columns | Generation Time | CSV Size | JSON Size |
|---------|----------------|----------|-----------|
| All (131) | ~5 min | 2.2 MB | 290 KB |
| 50 | ~3 min | ~1 MB | ~150 KB |
| 20 | ~2 min | ~500 KB | ~80 KB |
| 10 | ~1 min | ~300 KB | ~40 KB |

**💡 Tip:** Use `--columns` with wide CSVs to speed up generation significantly.

---

## Python API

You can also use the tool programmatically:

```python
from main import DatasetPipeline

# Create pipeline
pipeline = DatasetPipeline(
    input_file='appsflyer.csv',
    row_count=5000,
    column_count=20,
    base_dir='datasets',
    api_key='your_key'  # Optional if in .env
)

# Run complete pipeline
pipeline.run()

# Or run individual steps
pipeline.create_folder_structure()
synthetic_path = pipeline.generate_synthetic_data()
eval_files = pipeline.generate_eval_datasets(synthetic_path)
```

---

## Best Practices

### 1. Start Small, Scale Up

```bash
# Phase 1: Validate (quick)
python3 main.py data.csv --rows 100 --columns 10

# Phase 2: Develop
python3 main.py data.csv --rows 1000 --columns 20

# Phase 3: Test
python3 main.py data.csv --rows 5000 --columns 30

# Phase 4: Production
python3 main.py data.csv --rows 10000
```

### 2. Use Version Control

Add to `.gitignore`:
```
# Generated data
datasets/*/[0-9]*
*.csv
!*_sample.csv

# Environment
.env
```

### 3. Organize by Purpose

```
datasets/
├── Appsflyer/
│   ├── 100rows_10cols/      # Quick testing
│   ├── 1000rows_20cols/     # Development
│   ├── 5000rows_30cols/     # Standard testing
│   └── 10000/               # Load testing
```

### 4. Document Your Experiments

Each generated folder includes `README.md` with:
- Dataset statistics
- Column summary
- Date ranges
- File sizes
- Usage examples

---

## Requirements

**Python Packages** (in `requirements.txt`):
```
google-genai>=1.0.0
pandas>=2.0.0
python-dotenv>=1.0.0
faker>=20.0.0
```

**System Requirements:**
- Python 3.8 or higher
- Internet connection (for Gemini API)
- Sufficient disk space for generated files

---

## How It Works

### 1. Analysis Phase
- Reads your sample CSV
- Extracts column names and types
- Analyzes data patterns from sample rows

### 2. AI Generation Phase
- Sends pattern analysis to Gemini AI
- AI generates custom Python function
- Function creates realistic data matching patterns

### 3. Execution Phase
- Runs generated function N times (N = rows)
- Creates DataFrame with synthetic data
- Saves to CSV file

### 4. Evaluation Phase
- Generates 65+ test cases automatically
- Creates aggregation tests (25)
- Creates time comparison tests (20)
- Creates custom metrics tests (20)

### 5. Documentation Phase
- Generates README for dataset
- Includes statistics and usage examples
- Documents all generated files

---

## FAQ

**Q: How much does it cost?**
A: Uses Gemini API. Free tier usually sufficient for typical usage. Cost depends on data complexity and size.

**Q: Can I use my own API?**
A: Currently uses Gemini. Could be extended to other AI providers.

**Q: What CSV formats are supported?**
A: Any CSV with headers. Works best with clear patterns in data.

**Q: Can I customize the generated data?**
A: Yes! The AI-generated function is shown during generation. You can modify the script to customize.

**Q: How realistic is the data?**
A: Depends on sample quality. More samples = better patterns = more realistic data.

**Q: Can I generate specific date ranges?**
A: Currently generates dates spanning ~1 year. Can be customized in the generator script.

**Q: What about data privacy?**
A: Sample data is sent to Gemini API for function generation. Don't use sensitive production data as samples.

**Q: Can I use this in CI/CD?**
A: Yes! Works well in automated pipelines. Just ensure API key is available.

---

## Contributing

Improvements welcome! This is a utility tool for testing AI agents. Feel free to:
- Add new evaluation categories
- Improve AI prompts for better data generation
- Add support for more data types
- Enhance documentation

---

## License

MIT

---

## Support

For issues or questions:
1. Check this README
2. Review generated `README.md` in dataset folders
3. Check the displayed function code during generation
4. Ensure API key is valid and has quota

---

## Quick Reference

```bash
# Basic
python3 main.py data.csv --rows 5000

# With columns
python3 main.py data.csv --rows 5000 --columns 20

# Quick test
python3 main.py data.csv --rows 100 --columns 10

# Help
python3 main.py --help
```

**Generated structure:**
```
datasets/DatasetName/RowsXColsY/
├── dataset_synthetic_XrowsYcols.csv
├── eval_dataset_all.json
├── eval_dataset_aggregation.json
├── eval_dataset_time_comparison.json
├── eval_dataset_custom_metrics.json
└── README.md
```

---

**Built with ❤️ using Gemini AI**

# Synthetic Marketing Data Generator

An AI-powered tool that generates synthetic marketing data for testing and development. It uses Google's Gemini AI to intelligently create a row generation function based on your sample data, then generates realistic synthetic rows.

## Features

- 🤖 **AI-Powered Generation**: Uses Gemini AI to understand your data patterns and generate realistic synthetic data
- 📊 **Flexible Configuration**: Specify number of rows and columns to generate
- 🎯 **Pattern Recognition**: Analyzes sample CSV to match data types, formats, and patterns
- 📝 **Transparent Process**: Shows the generated function code for review
- 💾 **Easy Export**: Outputs to CSV format for immediate use

## Installation

1. **Clone or download this repository**

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up Gemini API Key**:

Create a `.env` file in the project directory:
```
GEMINI_API_KEY=your_api_key_here
```

Or export it in your shell:
```bash
export GEMINI_API_KEY=your_api_key_here
```

Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

## Usage

### Command Line Interface

Basic usage:
```bash
python synthetic_data_generator.py sample_marketing_data.csv --rows 100
```

Specify number of columns:
```bash
python synthetic_data_generator.py sample_marketing_data.csv --rows 100 --columns 5
```

Custom output path:
```bash
python synthetic_data_generator.py sample_marketing_data.csv --rows 500 --output my_data.csv
```

Pass API key directly:
```bash
python synthetic_data_generator.py sample_marketing_data.csv --rows 100 --api-key YOUR_API_KEY
```

### Python API

```python
from synthetic_data_generator import SyntheticDataGenerator

# Initialize generator
generator = SyntheticDataGenerator(api_key='your_api_key')

# Generate synthetic data
df = generator.generate_synthetic_data(
    sample_csv_path='sample_marketing_data.csv',
    num_rows=1000,
    num_columns=None,  # Use all columns
    output_path='output.csv'
)

# Use the dataframe
print(df.head())
```

## How It Works

1. **Analysis Phase**: Reads and analyzes the sample CSV file
   - Extracts column names and data types
   - Examines sample rows to understand patterns

2. **AI Generation Phase**: Uses Gemini AI to generate a Python function
   - Creates a `generate_row()` function tailored to your data
   - Includes appropriate randomization and realistic patterns

3. **Execution Phase**: Runs the generated function
   - Creates the specified number of synthetic rows
   - Returns a pandas DataFrame with the results

4. **Export Phase**: Saves to CSV (optional)

## Example

Using the provided `sample_marketing_data.csv`:

```bash
python synthetic_data_generator.py sample_marketing_data.csv --rows 50 --output test_data.csv
```

Output:
```
📊 Analyzing sample CSV: sample_marketing_data.csv
📝 Columns to generate: 10
🤖 Generating row creation function using Gemini...

============================================================
Generated Function Code:
============================================================
[Generated Python function will be displayed here]
============================================================

⚙️  Executing function to generate 50 rows...
✅ Saved synthetic data to: test_data.csv
✅ Generated 50 rows with 10 columns

📊 Preview of generated data:
[First 5 rows will be displayed here]

📈 Data shape: (50, 10)
```

## Sample Data Format

The included `sample_marketing_data.csv` contains marketing campaign data with columns:
- campaign_id
- campaign_name
- channel
- impressions
- clicks
- conversions
- spend
- revenue
- date
- target_audience

You can use your own CSV files with any structure!

## Requirements

- Python 3.8+
- google-genai
- pandas
- python-dotenv

## Notes

- The AI-generated function code is displayed for transparency and debugging
- Generated data maintains realistic patterns based on your samples
- The tool works with any CSV structure, not just marketing data
- Column count can be limited if you only need a subset of columns

## Troubleshooting

**Error: GEMINI_API_KEY must be set**
- Make sure you've set the API key in `.env` file or as an environment variable

**Error: Generated code doesn't contain 'generate_row' function**
- The AI might have generated invalid code. Try running again or adjust your sample data

**Data doesn't look realistic**
- Provide more sample rows (at least 5-10) for better pattern recognition
- Ensure your sample data is representative of the patterns you want

## Evaluation Dataset Generator

This project also includes an evaluation dataset generator for testing AI agents!

### Generate Eval Datasets

```bash
python3 generate_eval_datasets.py my_data.csv --output-dir .
```

This will generate test cases for:
1. **Data Aggregation** - Group by with sum, avg, min, max
2. **Time Period Comparison** - Compare metrics between date ranges
3. **Custom Metrics** - Calculate ROI, conversion rates, etc.

See `EVAL_README.md` for detailed documentation.

### Generated Files

- `eval_dataset_all.json` - All eval cases combined
- `eval_dataset_aggregation.json` - Aggregation tests
- `eval_dataset_time_comparison.json` - Time comparison tests
- `eval_dataset_custom_metrics.json` - Custom metrics tests

Each eval case includes:
- Natural language question
- Expected operation
- Ground truth answer with exact values
- Difficulty level

## License

MIT


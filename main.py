#!/usr/bin/env python3
"""
Main script to automate the entire synthetic data and evaluation generation workflow.

Usage:
    python3 main.py input_file.csv --rows 5000
    python3 main.py datasets/MyDataset/sample.csv --rows 10000
"""

import os
import sys
import argparse
import shutil
from pathlib import Path
from dotenv import load_dotenv
from synthetic_data_generator import SyntheticDataGenerator
from generate_eval_datasets import EvalDatasetGenerator

# Load environment variables from .env file
load_dotenv()


class DatasetPipeline:
    def __init__(self, input_file: str, row_count: int, column_count: int = None, base_dir: str = "datasets", api_key: str = None):
        """
        Initialize the dataset generation pipeline.
        
        Args:
            input_file: Path to input CSV file
            row_count: Number of rows to generate
            column_count: Number of columns to use (optional, uses all by default)
            base_dir: Base directory for datasets (default: "datasets")
            api_key: Gemini API key (optional, can use env var)
        """
        self.input_file = Path(input_file)
        self.row_count = row_count
        self.column_count = column_count
        self.base_dir = Path(base_dir)
        self.api_key = api_key
        
        if not self.input_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        self.dataset_name = self._extract_dataset_name()
        self.dataset_dir = self.base_dir / self.dataset_name
        
        # Include column count in folder name if specified
        if self.column_count:
            folder_name = f"{row_count}rows_{column_count}cols"
        else:
            folder_name = str(row_count)
        
        self.output_dir = self.dataset_dir / folder_name
        self.sample_file = self.dataset_dir / f"{self.dataset_name.lower()}_sample.csv"
        
    def _extract_dataset_name(self) -> str:
        """Extract dataset name from input file."""
        filename = self.input_file.stem
        
        if filename.endswith('_sample'):
            return filename.replace('_sample', '').title()
        
        return filename.replace('_', ' ').title().replace(' ', '')
    
    def create_folder_structure(self):
        """Create the required folder structure."""
        print(f"\n📁 Creating folder structure...")
        
        self.dataset_dir.mkdir(parents=True, exist_ok=True)
        print(f"   ✅ Created: {self.dataset_dir}")
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        print(f"   ✅ Created: {self.output_dir}")
        
        if not self.sample_file.exists():
            shutil.copy2(self.input_file, self.sample_file)
            print(f"   ✅ Copied sample file: {self.sample_file}")
        else:
            print(f"   ℹ️  Sample file already exists: {self.sample_file}")
    
    def generate_synthetic_data(self) -> Path:
        """Generate synthetic data using Gemini AI."""
        print(f"\n🤖 Generating synthetic data...")
        print(f"   Input: {self.sample_file}")
        print(f"   Rows: {self.row_count}")
        if self.column_count:
            print(f"   Columns: {self.column_count}")
        else:
            print(f"   Columns: All")
        
        # Include column count in filename if specified
        if self.column_count:
            output_filename = f"{self.dataset_name.lower()}_synthetic_{self.row_count}rows_{self.column_count}cols.csv"
        else:
            output_filename = f"{self.dataset_name.lower()}_synthetic_{self.row_count}.csv"
        output_path = self.output_dir / output_filename
        
        generator = SyntheticDataGenerator(api_key=self.api_key)
        
        df = generator.generate_synthetic_data(
            sample_csv_path=str(self.sample_file),
            num_rows=self.row_count,
            num_columns=self.column_count,
            output_path=str(output_path)
        )
        
        print(f"   ✅ Generated: {output_path}")
        print(f"   📊 Shape: {df.shape}")
        
        return output_path
    
    def generate_eval_datasets(self, synthetic_data_path: Path):
        """Generate evaluation datasets."""
        print(f"\n📝 Generating evaluation datasets...")
        
        eval_generator = EvalDatasetGenerator(str(synthetic_data_path))
        
        print(f"   📈 Dataset info: {len(eval_generator.df)} rows, {len(eval_generator.df.columns)} columns")
        print(f"   📅 Date range: {eval_generator.df['Date'].min()} to {eval_generator.df['Date'].max()}")
        
        output_files = eval_generator.generate_all_evals(output_dir=str(self.output_dir))
        
        return output_files
    
    def generate_summary(self, synthetic_data_path: Path, eval_files: dict):
        """Generate a summary file with all details."""
        summary_path = self.output_dir / "README.md"
        
        import pandas as pd
        import json
        
        df = pd.read_csv(synthetic_data_path)
        
        with open(eval_files['combined'], 'r') as f:
            eval_data = json.load(f)
        
        summary = f"""# {self.dataset_name} Dataset - {self.row_count} Rows

Generated on: {eval_data['metadata']['generated_at']}

## Structure

```
{self.dataset_dir}/
├── {self.sample_file.name}              # Original sample file
└── {self.row_count}/
    ├── {synthetic_data_path.name}       # Synthetic data ({self.row_count} rows)
    ├── eval_dataset_all.json            # All evaluation cases
    ├── eval_dataset_aggregation.json    # Data aggregation tests
    ├── eval_dataset_time_comparison.json # Time comparison tests
    └── eval_dataset_custom_metrics.json  # Custom metrics tests
```

## Synthetic Data

- **File**: `{synthetic_data_path.name}`
- **Rows**: {len(df):,}
- **Columns**: {len(df.columns)}
- **File Size**: {synthetic_data_path.stat().st_size / 1024 / 1024:.2f} MB

### Column Summary
- Numeric columns: {len(df.select_dtypes(include=['float64', 'int64']).columns)}
- Categorical columns: {len(df.select_dtypes(include=['object']).columns)}
- Date columns: {'Date' if 'Date' in df.columns else 'None'}

### Date Range
- Start: {df['Date'].min()}
- End: {df['Date'].max()}

## Evaluation Datasets

Total test cases: **{eval_data['metadata']['total_cases']}**

"""
        
        for category, info in eval_data['categories'].items():
            summary += f"### {category.replace('_', ' ').title()}\n"
            summary += f"- Test cases: **{info['count']}**\n"
            summary += f"- Description: {info['description']}\n\n"
        
        summary += f"""## Files Generated

| File | Size | Description |
|------|------|-------------|
| `{synthetic_data_path.name}` | {synthetic_data_path.stat().st_size / 1024 / 1024:.2f} MB | Synthetic data |
"""
        
        for name, path in eval_files.items():
            file_path = Path(path)
            size_kb = file_path.stat().st_size / 1024
            summary += f"| `{file_path.name}` | {size_kb:.1f} KB | {name.replace('_', ' ').title()} |\\n"
        
        summary += """
## Usage

### Load Synthetic Data
```python
import pandas as pd

df = pd.read_csv('{synthetic_data_name}')
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

run_evaluation('eval_dataset_all.json', '{synthetic_data_name}')
```

## Next Steps

1. Use the synthetic data to test your AI agent
2. Validate against the evaluation datasets
3. Track accuracy across different categories
4. Generate more data with different row counts if needed

---
Generated with `main.py`
""".format(synthetic_data_name=synthetic_data_path.name)
        
        with open(summary_path, 'w') as f:
            f.write(summary)
        
        print(f"\n📄 Generated summary: {summary_path}")
    
    def run(self):
        """Run the complete pipeline."""
        print("="*70)
        print(f"🚀 Starting Dataset Generation Pipeline")
        print("="*70)
        print(f"Dataset: {self.dataset_name}")
        print(f"Rows: {self.row_count:,}")
        print(f"Columns: {self.column_count if self.column_count else 'All'}")
        print(f"Output: {self.output_dir}")
        print("="*70)
        
        try:
            self.create_folder_structure()
            
            synthetic_data_path = self.generate_synthetic_data()
            
            eval_files = self.generate_eval_datasets(synthetic_data_path)
            
            self.generate_summary(synthetic_data_path, eval_files)
            
            print("\n" + "="*70)
            print("✅ Pipeline completed successfully!")
            print("="*70)
            print(f"\n📁 Output directory: {self.output_dir}")
            print(f"\n📊 Files generated:")
            print(f"   - {synthetic_data_path.name}")
            for name, path in eval_files.items():
                print(f"   - {Path(path).name}")
            print(f"   - README.md")
            print("\n" + "="*70)
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Generate synthetic data and evaluation datasets with automated folder structure',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate from a new input file
  python3 main.py appsflyer.csv --rows 5000
  
  # Generate with specific number of columns
  python3 main.py appsflyer.csv --rows 5000 --columns 20
  
  # Generate from existing sample file
  python3 main.py datasets/Appsflyer/appsflyer_sample.csv --rows 10000
  
  # Custom base directory
  python3 main.py mydata.csv --rows 1000 --base-dir my_datasets
        """
    )
    
    parser.add_argument('input_file', help='Path to input CSV file')
    parser.add_argument('--rows', '-r', type=int, required=True, help='Number of rows to generate')
    parser.add_argument('--columns', '-c', type=int, help='Number of columns to use (optional, uses all by default)')
    parser.add_argument('--base-dir', '-b', default='datasets', help='Base directory for datasets (default: datasets)')
    parser.add_argument('--api-key', '-k', help='Gemini API key (or set GEMINI_API_KEY env var)')
    
    args = parser.parse_args()
    
    if args.rows <= 0:
        print("❌ Error: Number of rows must be positive")
        sys.exit(1)
    
    if args.columns is not None and args.columns <= 0:
        print("❌ Error: Number of columns must be positive")
        sys.exit(1)
    
    pipeline = DatasetPipeline(
        input_file=args.input_file,
        row_count=args.rows,
        column_count=args.columns,
        base_dir=args.base_dir,
        api_key=args.api_key
    )
    
    pipeline.run()


if __name__ == '__main__':
    main()


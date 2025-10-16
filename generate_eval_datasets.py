import pandas as pd
import json
import argparse
from datetime import datetime, timedelta
from typing import List, Dict, Any
import random


class EvalDatasetGenerator:
    def __init__(self, data_csv_path: str):
        """Initialize with the synthetic data CSV."""
        self.df = pd.read_csv(data_csv_path)
        self.df['Date'] = pd.to_datetime(self.df['Date'])
        self.numeric_columns = self.df.select_dtypes(include=['float64', 'int64']).columns.tolist()
        self.categorical_columns = self.df.select_dtypes(include=['object']).columns.tolist()
        if 'Date' in self.categorical_columns:
            self.categorical_columns.remove('Date')
        
    def generate_aggregation_evals(self, num_cases: int = 20) -> List[Dict[str, Any]]:
        """Generate eval cases for data aggregation with group by."""
        eval_cases = []
        
        agg_functions = {
            'sum': ('sum', 'total'),
            'mean': ('average', 'avg'),
            'min': ('minimum', 'min'),
            'max': ('maximum', 'max'),
            'count': ('count', 'number of')
        }
        
        for i in range(num_cases):
            group_col = random.choice([col for col in self.categorical_columns if col != 'Date'])
            metric_col = random.choice(self.numeric_columns)
            agg_func = random.choice(list(agg_functions.keys()))
            agg_label, agg_desc = agg_functions[agg_func]
            
            result = self.df.groupby(group_col)[metric_col].agg(agg_func).to_dict()
            
            question = f"What is the {agg_desc} of {metric_col} by {group_col}?"
            
            operation = f"GROUP BY {group_col}, {agg_func.upper()}({metric_col})"
            
            eval_case = {
                "id": f"agg_{i+1}",
                "category": "data_aggregation",
                "question": question,
                "operation": operation,
                "group_by_column": group_col,
                "metric_column": metric_col,
                "aggregation_function": agg_func,
                "expected_result": {str(k): float(v) if pd.notna(v) else None for k, v in result.items()},
                "difficulty": "medium"
            }
            eval_cases.append(eval_case)
        
        for i in range(5):
            group_cols = random.sample([col for col in self.categorical_columns if col != 'Date'], 2)
            metric_col = random.choice(self.numeric_columns)
            agg_func = random.choice(['sum', 'mean', 'count'])
            agg_label, agg_desc = agg_functions[agg_func]
            
            result = self.df.groupby(group_cols)[metric_col].agg(agg_func)
            result_dict = {}
            for idx, val in result.items():
                key = f"{idx[0]}_{idx[1]}"
                result_dict[key] = float(val) if pd.notna(val) else None
            
            question = f"What is the {agg_desc} of {metric_col} grouped by {group_cols[0]} and {group_cols[1]}?"
            operation = f"GROUP BY {group_cols[0]}, {group_cols[1]}, {agg_func.upper()}({metric_col})"
            
            eval_case = {
                "id": f"agg_multi_{i+1}",
                "category": "data_aggregation_multi_group",
                "question": question,
                "operation": operation,
                "group_by_columns": group_cols,
                "metric_column": metric_col,
                "aggregation_function": agg_func,
                "expected_result": result_dict,
                "difficulty": "hard"
            }
            eval_cases.append(eval_case)
        
        return eval_cases
    
    def generate_time_comparison_evals(self, num_cases: int = 15) -> List[Dict[str, Any]]:
        """Generate eval cases for metric comparison between time periods."""
        eval_cases = []
        
        self.df = self.df.sort_values('Date')
        date_range = (self.df['Date'].max() - self.df['Date'].min()).days
        
        if date_range < 30:
            print("Warning: Date range is less than 30 days. Time comparison evals may be limited.")
        
        for i in range(num_cases):
            metric_col = random.choice(self.numeric_columns)
            
            split_point = self.df['Date'].min() + timedelta(days=date_range // 2)
            
            period1_df = self.df[self.df['Date'] < split_point]
            period2_df = self.df[self.df['Date'] >= split_point]
            
            period1_value = period1_df[metric_col].sum()
            period2_value = period2_df[metric_col].sum()
            difference = period2_value - period1_value
            percent_change = ((period2_value - period1_value) / period1_value * 100) if period1_value != 0 else None
            
            period1_str = f"{period1_df['Date'].min().strftime('%Y-%m-%d')} to {period1_df['Date'].max().strftime('%Y-%m-%d')}"
            period2_str = f"{period2_df['Date'].min().strftime('%Y-%m-%d')} to {period2_df['Date'].max().strftime('%Y-%m-%d')}"
            
            question = f"Compare the total {metric_col} between {period1_str} and {period2_str}. What is the difference?"
            
            eval_case = {
                "id": f"time_comp_{i+1}",
                "category": "time_period_comparison",
                "question": question,
                "metric_column": metric_col,
                "time_period_1": {
                    "start": period1_df['Date'].min().strftime('%Y-%m-%d'),
                    "end": period1_df['Date'].max().strftime('%Y-%m-%d'),
                    "value": float(period1_value) if pd.notna(period1_value) else None
                },
                "time_period_2": {
                    "start": period2_df['Date'].min().strftime('%Y-%m-%d'),
                    "end": period2_df['Date'].max().strftime('%Y-%m-%d'),
                    "value": float(period2_value) if pd.notna(period2_value) else None
                },
                "expected_result": {
                    "period_1_value": float(period1_value) if pd.notna(period1_value) else None,
                    "period_2_value": float(period2_value) if pd.notna(period2_value) else None,
                    "absolute_difference": float(difference) if pd.notna(difference) else None,
                    "percent_change": float(round(percent_change, 2)) if percent_change is not None and pd.notna(percent_change) else None
                },
                "difficulty": "medium"
            }
            eval_cases.append(eval_case)
        
        for i in range(5):
            metric_col = random.choice(self.numeric_columns)
            group_col = random.choice([col for col in self.categorical_columns if col != 'Date'])
            
            split_point = self.df['Date'].min() + timedelta(days=date_range // 2)
            
            period1_df = self.df[self.df['Date'] < split_point]
            period2_df = self.df[self.df['Date'] >= split_point]
            
            period1_grouped = period1_df.groupby(group_col)[metric_col].sum().to_dict()
            period2_grouped = period2_df.groupby(group_col)[metric_col].sum().to_dict()
            
            all_groups = set(list(period1_grouped.keys()) + list(period2_grouped.keys()))
            comparison_result = {}
            for group in all_groups:
                val1 = period1_grouped.get(group, 0)
                val2 = period2_grouped.get(group, 0)
                diff = val2 - val1
                pct_change = ((val2 - val1) / val1 * 100) if val1 != 0 else None
                comparison_result[str(group)] = {
                    "period_1": float(val1) if pd.notna(val1) else None,
                    "period_2": float(val2) if pd.notna(val2) else None,
                    "difference": float(diff) if pd.notna(diff) else None,
                    "percent_change": float(round(pct_change, 2)) if pct_change is not None and pd.notna(pct_change) else None
                }
            
            period1_str = f"{period1_df['Date'].min().strftime('%Y-%m-%d')} to {period1_df['Date'].max().strftime('%Y-%m-%d')}"
            period2_str = f"{period2_df['Date'].min().strftime('%Y-%m-%d')} to {period2_df['Date'].max().strftime('%Y-%m-%d')}"
            
            question = f"Compare the total {metric_col} by {group_col} between {period1_str} and {period2_str}."
            
            eval_case = {
                "id": f"time_comp_grouped_{i+1}",
                "category": "time_period_comparison_grouped",
                "question": question,
                "metric_column": metric_col,
                "group_by_column": group_col,
                "time_period_1": period1_str,
                "time_period_2": period2_str,
                "expected_result": comparison_result,
                "difficulty": "hard"
            }
            eval_cases.append(eval_case)
        
        return eval_cases
    
    def generate_custom_metrics_evals(self, num_cases: int = 15) -> List[Dict[str, Any]]:
        """Generate eval cases for custom metrics and their aggregation."""
        eval_cases = []
        
        custom_metrics = [
            {
                "name": "ROI",
                "formula": "(Total Revenue - Total Cost) / Total Cost * 100",
                "columns": ["Total Revenue", "Total Cost"],
                "description": "Return on Investment percentage"
            },
            {
                "name": "Conversion Rate",
                "formula": "Conversions / Clicks * 100",
                "columns": ["Conversions", "Clicks"],
                "description": "Conversion rate percentage"
            },
            {
                "name": "Cost Per Conversion",
                "formula": "Total Cost / Conversions",
                "columns": ["Total Cost", "Conversions"],
                "description": "Average cost per conversion"
            },
            {
                "name": "Revenue Per Session",
                "formula": "Total Revenue / Sessions",
                "columns": ["Total Revenue", "Sessions"],
                "description": "Average revenue per session"
            },
            {
                "name": "Profit Margin",
                "formula": "(Total Revenue - Total Cost) / Total Revenue * 100",
                "columns": ["Total Revenue", "Total Cost"],
                "description": "Profit margin percentage"
            }
        ]
        
        for i in range(num_cases):
            metric = random.choice(custom_metrics)
            
            required_cols = metric["columns"]
            if not all(col in self.df.columns for col in required_cols):
                continue
            
            df_clean = self.df.dropna(subset=required_cols)
            
            if metric["name"] == "ROI":
                df_clean = df_clean[df_clean["Total Cost"] != 0]
                df_clean['custom_metric'] = (df_clean["Total Revenue"] - df_clean["Total Cost"]) / df_clean["Total Cost"] * 100
            elif metric["name"] == "Conversion Rate":
                df_clean = df_clean[df_clean["Clicks"] != 0]
                df_clean['custom_metric'] = df_clean["Conversions"] / df_clean["Clicks"] * 100
            elif metric["name"] == "Cost Per Conversion":
                df_clean = df_clean[df_clean["Conversions"] != 0]
                df_clean['custom_metric'] = df_clean["Total Cost"] / df_clean["Conversions"]
            elif metric["name"] == "Revenue Per Session":
                df_clean = df_clean[df_clean["Sessions"] != 0]
                df_clean['custom_metric'] = df_clean["Total Revenue"] / df_clean["Sessions"]
            elif metric["name"] == "Profit Margin":
                df_clean = df_clean[df_clean["Total Revenue"] != 0]
                df_clean['custom_metric'] = (df_clean["Total Revenue"] - df_clean["Total Cost"]) / df_clean["Total Revenue"] * 100
            
            if len(df_clean) == 0:
                continue
            
            agg_func = random.choice(['mean', 'sum', 'median'])
            
            if agg_func == 'mean':
                result = df_clean['custom_metric'].mean()
                agg_desc = "average"
            elif agg_func == 'sum':
                result = df_clean['custom_metric'].sum()
                agg_desc = "total"
            else:
                result = df_clean['custom_metric'].median()
                agg_desc = "median"
            
            question = f"Calculate the {agg_desc} {metric['name']} across all records. Formula: {metric['formula']}"
            
            eval_case = {
                "id": f"custom_metric_{i+1}",
                "category": "custom_metrics",
                "question": question,
                "metric_name": metric["name"],
                "metric_formula": metric["formula"],
                "metric_description": metric["description"],
                "aggregation_function": agg_func,
                "required_columns": required_cols,
                "expected_result": float(round(result, 2)) if pd.notna(result) else None,
                "difficulty": "medium"
            }
            eval_cases.append(eval_case)
        
        for i in range(5):
            metric = random.choice(custom_metrics)
            group_col = random.choice([col for col in self.categorical_columns if col != 'Date'])
            
            required_cols = metric["columns"]
            if not all(col in self.df.columns for col in required_cols):
                continue
            
            df_clean = self.df.dropna(subset=required_cols)
            
            if metric["name"] == "ROI":
                df_clean = df_clean[df_clean["Total Cost"] != 0]
                df_clean['custom_metric'] = (df_clean["Total Revenue"] - df_clean["Total Cost"]) / df_clean["Total Cost"] * 100
            elif metric["name"] == "Conversion Rate":
                df_clean = df_clean[df_clean["Clicks"] != 0]
                df_clean['custom_metric'] = df_clean["Conversions"] / df_clean["Clicks"] * 100
            elif metric["name"] == "Cost Per Conversion":
                df_clean = df_clean[df_clean["Conversions"] != 0]
                df_clean['custom_metric'] = df_clean["Total Cost"] / df_clean["Conversions"]
            elif metric["name"] == "Revenue Per Session":
                df_clean = df_clean[df_clean["Sessions"] != 0]
                df_clean['custom_metric'] = df_clean["Total Revenue"] / df_clean["Sessions"]
            elif metric["name"] == "Profit Margin":
                df_clean = df_clean[df_clean["Total Revenue"] != 0]
                df_clean['custom_metric'] = (df_clean["Total Revenue"] - df_clean["Total Cost"]) / df_clean["Total Revenue"] * 100
            
            if len(df_clean) == 0:
                continue
            
            result = df_clean.groupby(group_col)['custom_metric'].mean().to_dict()
            
            question = f"Calculate the average {metric['name']} by {group_col}. Formula: {metric['formula']}"
            
            eval_case = {
                "id": f"custom_metric_grouped_{i+1}",
                "category": "custom_metrics_grouped",
                "question": question,
                "metric_name": metric["name"],
                "metric_formula": metric["formula"],
                "metric_description": metric["description"],
                "group_by_column": group_col,
                "aggregation_function": "mean",
                "required_columns": required_cols,
                "expected_result": {str(k): float(round(v, 2)) if pd.notna(v) else None for k, v in result.items()},
                "difficulty": "hard"
            }
            eval_cases.append(eval_case)
        
        return eval_cases
    
    def generate_all_evals(self, output_dir: str = ".") -> Dict[str, str]:
        """Generate all eval datasets and save them."""
        print("🔄 Generating evaluation datasets...")
        
        agg_evals = self.generate_aggregation_evals()
        print(f"✅ Generated {len(agg_evals)} data aggregation eval cases")
        
        time_evals = self.generate_time_comparison_evals()
        print(f"✅ Generated {len(time_evals)} time comparison eval cases")
        
        custom_evals = self.generate_custom_metrics_evals()
        print(f"✅ Generated {len(custom_evals)} custom metrics eval cases")
        
        all_evals = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "source_data": "synthetic marketing data",
                "total_cases": len(agg_evals) + len(time_evals) + len(custom_evals)
            },
            "categories": {
                "data_aggregation": {
                    "description": "Test cases for grouping and aggregating data with sum, avg, min, max",
                    "count": len(agg_evals),
                    "cases": agg_evals
                },
                "time_period_comparison": {
                    "description": "Test cases for comparing metrics between different time periods",
                    "count": len(time_evals),
                    "cases": time_evals
                },
                "custom_metrics": {
                    "description": "Test cases for calculating and aggregating custom business metrics",
                    "count": len(custom_evals),
                    "cases": custom_evals
                }
            }
        }
        
        output_files = {}
        
        combined_path = f"{output_dir}/eval_dataset_all.json"
        with open(combined_path, 'w') as f:
            json.dump(all_evals, f, indent=2)
        output_files['combined'] = combined_path
        print(f"📄 Saved combined eval dataset: {combined_path}")
        
        agg_path = f"{output_dir}/eval_dataset_aggregation.json"
        with open(agg_path, 'w') as f:
            json.dump({"metadata": all_evals["metadata"], "cases": agg_evals}, f, indent=2)
        output_files['aggregation'] = agg_path
        print(f"📄 Saved aggregation eval dataset: {agg_path}")
        
        time_path = f"{output_dir}/eval_dataset_time_comparison.json"
        with open(time_path, 'w') as f:
            json.dump({"metadata": all_evals["metadata"], "cases": time_evals}, f, indent=2)
        output_files['time_comparison'] = time_path
        print(f"📄 Saved time comparison eval dataset: {time_path}")
        
        custom_path = f"{output_dir}/eval_dataset_custom_metrics.json"
        with open(custom_path, 'w') as f:
            json.dump({"metadata": all_evals["metadata"], "cases": custom_evals}, f, indent=2)
        output_files['custom_metrics'] = custom_path
        print(f"📄 Saved custom metrics eval dataset: {custom_path}")
        
        return output_files


def main():
    parser = argparse.ArgumentParser(description='Generate evaluation datasets for AI agent testing')
    parser.add_argument('data_csv', help='Path to synthetic data CSV file')
    parser.add_argument('--output-dir', '-o', default='.', help='Output directory for eval files')
    parser.add_argument('--agg-cases', type=int, default=20, help='Number of aggregation eval cases')
    parser.add_argument('--time-cases', type=int, default=15, help='Number of time comparison eval cases')
    parser.add_argument('--custom-cases', type=int, default=15, help='Number of custom metrics eval cases')
    
    args = parser.parse_args()
    
    print(f"📊 Loading data from: {args.data_csv}")
    generator = EvalDatasetGenerator(args.data_csv)
    
    print(f"📈 Dataset info: {len(generator.df)} rows, {len(generator.df.columns)} columns")
    print(f"📅 Date range: {generator.df['Date'].min()} to {generator.df['Date'].max()}")
    
    output_files = generator.generate_all_evals(output_dir=args.output_dir)
    
    print(f"\n✅ Successfully generated evaluation datasets!")
    print(f"📁 Output files:")
    for category, path in output_files.items():
        print(f"   - {category}: {path}")


if __name__ == '__main__':
    main()


"""
Example script showing how to use the evaluation datasets to test an AI agent.
"""

import json
import pandas as pd
from typing import Dict, Any


def load_eval_dataset(eval_file: str) -> Dict[str, Any]:
    """Load an evaluation dataset from JSON."""
    with open(eval_file, 'r') as f:
        return json.load(f)


def compare_results(actual: Any, expected: Any, tolerance: float = 0.01) -> bool:
    """Compare actual and expected results with tolerance for floats."""
    if isinstance(expected, dict) and isinstance(actual, dict):
        if set(expected.keys()) != set(actual.keys()):
            return False
        return all(compare_results(actual[k], expected[k], tolerance) for k in expected.keys())
    
    elif isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
        if expected is None or actual is None:
            return expected == actual
        return abs(actual - expected) <= tolerance
    
    else:
        return actual == expected


def test_aggregation_case(case: Dict[str, Any], df: pd.DataFrame) -> bool:
    """
    Test a data aggregation case.
    This is a mock implementation - replace with your AI agent.
    """
    group_col = case.get('group_by_column') or case.get('group_by_columns')
    metric_col = case['metric_column']
    agg_func = case['aggregation_function']
    
    if isinstance(group_col, list):
        result = df.groupby(group_col)[metric_col].agg(agg_func)
        result_dict = {}
        for idx, val in result.items():
            key = "_".join(str(i) for i in idx)
            result_dict[key] = float(val) if pd.notna(val) else None
    else:
        result = df.groupby(group_col)[metric_col].agg(agg_func).to_dict()
        result_dict = {str(k): float(v) if pd.notna(v) else None for k, v in result.items()}
    
    expected = case['expected_result']
    return compare_results(result_dict, expected)


def test_time_comparison_case(case: Dict[str, Any], df: pd.DataFrame) -> bool:
    """
    Test a time period comparison case.
    This is a mock implementation - replace with your AI agent.
    """
    df['Date'] = pd.to_datetime(df['Date'])
    metric_col = case['metric_column']
    
    if 'time_period_1' in case and isinstance(case['time_period_1'], dict):
        period1 = case['time_period_1']
        period2 = case['time_period_2']
        
        p1_start = pd.to_datetime(period1['start'])
        p1_end = pd.to_datetime(period1['end'])
        p2_start = pd.to_datetime(period2['start'])
        p2_end = pd.to_datetime(period2['end'])
        
        p1_val = df[(df['Date'] >= p1_start) & (df['Date'] <= p1_end)][metric_col].sum()
        p2_val = df[(df['Date'] >= p2_start) & (df['Date'] <= p2_end)][metric_col].sum()
        
        actual = {
            'period_1_value': float(p1_val) if pd.notna(p1_val) else None,
            'period_2_value': float(p2_val) if pd.notna(p2_val) else None,
            'absolute_difference': float(p2_val - p1_val) if pd.notna(p2_val) and pd.notna(p1_val) else None,
            'percent_change': float(round((p2_val - p1_val) / p1_val * 100, 2)) if p1_val != 0 and pd.notna(p1_val) else None
        }
        
        expected = case['expected_result']
        return compare_results(actual, expected, tolerance=0.1)
    
    return False


def test_custom_metrics_case(case: Dict[str, Any], df: pd.DataFrame) -> bool:
    """
    Test a custom metrics case.
    This is a mock implementation - replace with your AI agent.
    """
    metric_name = case['metric_name']
    required_cols = case['required_columns']
    agg_func = case['aggregation_function']
    
    df_clean = df.dropna(subset=required_cols)
    
    if metric_name == "ROI":
        df_clean = df_clean[df_clean["Total Cost"] != 0]
        df_clean['custom_metric'] = (df_clean["Total Revenue"] - df_clean["Total Cost"]) / df_clean["Total Cost"] * 100
    elif metric_name == "Conversion Rate":
        df_clean = df_clean[df_clean["Clicks"] != 0]
        df_clean['custom_metric'] = df_clean["Conversions"] / df_clean["Clicks"] * 100
    elif metric_name == "Cost Per Conversion":
        df_clean = df_clean[df_clean["Conversions"] != 0]
        df_clean['custom_metric'] = df_clean["Total Cost"] / df_clean["Conversions"]
    elif metric_name == "Revenue Per Session":
        df_clean = df_clean[df_clean["Sessions"] != 0]
        df_clean['custom_metric'] = df_clean["Total Revenue"] / df_clean["Sessions"]
    elif metric_name == "Profit Margin":
        df_clean = df_clean[df_clean["Total Revenue"] != 0]
        df_clean['custom_metric'] = (df_clean["Total Revenue"] - df_clean["Total Cost"]) / df_clean["Total Revenue"] * 100
    
    if 'group_by_column' in case:
        result = df_clean.groupby(case['group_by_column'])['custom_metric'].mean().to_dict()
        actual = {str(k): float(round(v, 2)) if pd.notna(v) else None for k, v in result.items()}
    else:
        if agg_func == 'mean':
            actual = float(round(df_clean['custom_metric'].mean(), 2))
        elif agg_func == 'sum':
            actual = float(round(df_clean['custom_metric'].sum(), 2))
        elif agg_func == 'median':
            actual = float(round(df_clean['custom_metric'].median(), 2))
    
    expected = case['expected_result']
    return compare_results(actual, expected, tolerance=0.1)


def run_evaluation(eval_file: str, data_file: str):
    """Run evaluation on all cases in an eval dataset."""
    print(f"\n{'='*70}")
    print(f"Running evaluation: {eval_file}")
    print(f"{'='*70}\n")
    
    eval_data = load_eval_dataset(eval_file)
    df = pd.read_csv(data_file)
    
    if 'categories' in eval_data:
        for category, info in eval_data['categories'].items():
            print(f"\n📁 Category: {category}")
            print(f"   {info['description']}")
            print(f"   Total cases: {info['count']}\n")
            
            passed = 0
            failed = 0
            
            for case in info['cases']:
                try:
                    if 'data_aggregation' in category:
                        result = test_aggregation_case(case, df)
                    elif 'time_period_comparison' in category:
                        result = test_time_comparison_case(case, df)
                    elif 'custom_metrics' in category:
                        result = test_custom_metrics_case(case, df)
                    else:
                        result = False
                    
                    if result:
                        passed += 1
                        print(f"   ✅ {case['id']}: PASSED")
                    else:
                        failed += 1
                        print(f"   ❌ {case['id']}: FAILED")
                        print(f"      Question: {case['question']}")
                
                except Exception as e:
                    failed += 1
                    print(f"   ❌ {case['id']}: ERROR - {str(e)}")
            
            accuracy = (passed / (passed + failed) * 100) if (passed + failed) > 0 else 0
            print(f"\n   📊 Results: {passed} passed, {failed} failed")
            print(f"   🎯 Accuracy: {accuracy:.1f}%")
    
    else:
        cases = eval_data.get('cases', [])
        print(f"Total cases: {len(cases)}\n")
        
        passed = 0
        failed = 0
        
        for case in cases:
            try:
                category = case['category']
                
                if 'aggregation' in category:
                    result = test_aggregation_case(case, df)
                elif 'time' in category or 'comparison' in category:
                    result = test_time_comparison_case(case, df)
                elif 'custom' in category or 'metric' in category:
                    result = test_custom_metrics_case(case, df)
                else:
                    result = False
                
                if result:
                    passed += 1
                    print(f"✅ {case['id']}: PASSED")
                else:
                    failed += 1
                    print(f"❌ {case['id']}: FAILED - {case['question']}")
            
            except Exception as e:
                failed += 1
                print(f"❌ {case['id']}: ERROR - {str(e)}")
        
        accuracy = (passed / (passed + failed) * 100) if (passed + failed) > 0 else 0
        print(f"\n📊 Overall Results: {passed} passed, {failed} failed")
        print(f"🎯 Overall Accuracy: {accuracy:.1f}%")


def main():
    """Run evaluation on all eval datasets."""
    data_file = 'my_data.csv'
    
    eval_files = [
        'eval_dataset_all.json',
        # 'eval_dataset_aggregation.json',
        # 'eval_dataset_time_comparison.json',
        # 'eval_dataset_custom_metrics.json',
    ]
    
    for eval_file in eval_files:
        try:
            run_evaluation(eval_file, data_file)
        except FileNotFoundError:
            print(f"⚠️  File not found: {eval_file}")
        except Exception as e:
            print(f"❌ Error running evaluation: {e}")
    
    print(f"\n{'='*70}")
    print("Evaluation complete!")
    print(f"{'='*70}\n")


if __name__ == '__main__':
    main()


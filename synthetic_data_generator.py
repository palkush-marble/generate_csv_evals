import os
import pandas as pd
from google import genai
from google.genai import types
import json
import re
from typing import Optional


class SyntheticDataGenerator:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the generator with Gemini API key."""
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY must be set in environment or passed as argument")
        self.client = genai.Client(api_key=self.api_key)

    def analyze_sample_csv(self, sample_csv_path: str) -> tuple[pd.DataFrame, dict]:
        """Read and analyze the sample CSV file."""
        df = pd.read_csv(sample_csv_path)
        
        analysis = {
            'columns': list(df.columns),
            'column_count': len(df.columns),
            'sample_rows': df.head(5).to_dict('records'),
            'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()}
        }
        
        return df, analysis

    def generate_row_function(self, analysis: dict, num_columns: Optional[int] = None) -> str:
        """Use Gemini to generate a Python function for creating synthetic rows."""
        columns = analysis['columns']
        
        if num_columns and num_columns != len(columns):
            columns = columns[:num_columns]
        
        prompt = f"""You are a Python code generator. Generate a Python function that creates synthetic marketing data rows.

Column names: {columns}
Sample data for reference: {json.dumps(analysis['sample_rows'][:3], indent=2)}

Requirements:
1. Create a function named 'generate_row' that returns a dictionary with keys: {columns}
2. The function should use Python's random module and faker library if needed
3. Generate realistic marketing data that matches the pattern in the samples
4. Use proper data types (strings, numbers, dates, etc.) based on the samples
5. Add variety to the data while maintaining realistic patterns
6. The function should be standalone and include all necessary imports at the top

Return ONLY the Python code for the function, no explanations. Make sure the code is complete and ready to execute.
"""
        
        response = self.client.models.generate_content(
            model='gemini-2.0-flash-001',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=2000,
            )
        )
        
        code = self._extract_code(response.text)
        return code

    def _extract_code(self, response_text: str) -> str:
        """Extract Python code from markdown code blocks."""
        pattern = r'```python\n(.*?)\n```'
        matches = re.findall(pattern, response_text, re.DOTALL)
        
        if matches:
            return matches[0]
        
        pattern = r'```\n(.*?)\n```'
        matches = re.findall(pattern, response_text, re.DOTALL)
        
        if matches:
            return matches[0]
        
        return response_text.strip()

    def execute_generation(self, function_code: str, num_rows: int) -> pd.DataFrame:
        """Execute the generated function to create synthetic data."""
        namespace = {}
        exec(function_code, namespace)
        
        if 'generate_row' not in namespace:
            raise ValueError("Generated code doesn't contain 'generate_row' function")
        
        generate_row = namespace['generate_row']
        
        rows = []
        for _ in range(num_rows):
            row = generate_row()
            rows.append(row)
        
        df = pd.DataFrame(rows)
        return df

    def generate_synthetic_data(
        self, 
        sample_csv_path: str, 
        num_rows: int,
        num_columns: Optional[int] = None,
        output_path: Optional[str] = None
    ) -> pd.DataFrame:
        """Generate synthetic data based on sample CSV."""
        print(f"📊 Analyzing sample CSV: {sample_csv_path}")
        df_sample, analysis = self.analyze_sample_csv(sample_csv_path)
        
        if num_columns and num_columns > len(analysis['columns']):
            num_columns = len(analysis['columns'])
            print(f"⚠️  Requested columns ({num_columns}) exceeds sample columns. Using {len(analysis['columns'])} columns.")
        
        print(f"📝 Columns to generate: {num_columns or analysis['column_count']}")
        print(f"🤖 Generating row creation function using Gemini...")
        
        function_code = self.generate_row_function(analysis, num_columns)
        
        print(f"\n{'='*60}")
        print("Generated Function Code:")
        print(f"{'='*60}")
        print(function_code)
        print(f"{'='*60}\n")
        
        print(f"⚙️  Executing function to generate {num_rows} rows...")
        df_synthetic = self.execute_generation(function_code, num_rows)
        
        if output_path:
            df_synthetic.to_csv(output_path, index=False)
            print(f"✅ Saved synthetic data to: {output_path}")
        
        print(f"✅ Generated {len(df_synthetic)} rows with {len(df_synthetic.columns)} columns")
        return df_synthetic


def main():
    """CLI interface for the synthetic data generator."""
    import argparse
    from dotenv import load_dotenv
    
    load_dotenv()
    
    parser = argparse.ArgumentParser(description='Generate synthetic marketing data using AI')
    parser.add_argument('sample_csv', help='Path to sample CSV file')
    parser.add_argument('--rows', type=int, required=True, help='Number of rows to generate')
    parser.add_argument('--columns', type=int, help='Number of columns to use (optional, uses all by default)')
    parser.add_argument('--output', '-o', help='Output CSV path (optional)')
    parser.add_argument('--api-key', help='Gemini API key (or set GEMINI_API_KEY env var)')
    
    args = parser.parse_args()
    
    generator = SyntheticDataGenerator(api_key=args.api_key)
    
    output_path = args.output or f'synthetic_data_{args.rows}_rows.csv'
    
    df = generator.generate_synthetic_data(
        sample_csv_path=args.sample_csv,
        num_rows=args.rows,
        num_columns=args.columns,
        output_path=output_path
    )
    
    print("\n📊 Preview of generated data:")
    print(df.head())
    print(f"\n📈 Data shape: {df.shape}")


if __name__ == '__main__':
    main()


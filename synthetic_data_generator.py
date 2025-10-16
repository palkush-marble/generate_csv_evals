import os
import pandas as pd
from google import genai
from google.genai import types
import json
import re
import time
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
        
        prompt = f"""Generate a Python function that creates synthetic marketing data rows.

Columns: {columns}
Sample data: {json.dumps(analysis['sample_rows'][:2], indent=1)}

Create function 'generate_row()' that returns dict with keys: {columns}
Use random, faker, datetime, numpy. Keep it concise but realistic.
Return ONLY the complete Python code, no explanations.
"""
        
        # Retry logic for API calls
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"   🔄 Attempt {attempt + 1}/{max_retries}...")
                
                # Try different models in order of preference (best to fallback)
                models_to_try = [
                    'gemini-2.5-pro',           # Best quality
                    'gemini-2.5-flash',         # Good balance
                    'gemini-2.0-flash-001',     # Stable fallback
                    'gemini-flash-latest'       # Latest stable
                ]
                response = None
                
                for model in models_to_try:
                    try:
                        print(f"   🤖 Trying model: {model}")
                        response = self.client.models.generate_content(
                            model=model,
                            contents=prompt,
                            config=types.GenerateContentConfig(
                                temperature=0.7,
                                max_output_tokens=4000,
                            )
                        )
                        if response and hasattr(response, 'text') and response.text:
                            print(f"   ✅ Model {model} responded successfully")
                            break
                        else:
                            print(f"   ⚠️  Model {model} returned empty response")
                    except Exception as model_error:
                        print(f"   ⚠️  Model {model} failed: {str(model_error)}")
                        continue
                
                if not response or not hasattr(response, 'text'):
                    raise ValueError("Gemini API returned invalid response structure.")
                
                if response.text is None or response.text.strip() == "":
                    raise ValueError("Gemini API returned empty response.")
                
                code = self._extract_code(response.text)
                if code and len(code.strip()) > 50:  # Basic validation
                    print(f"   ✅ Successfully generated function code")
                    return code
                else:
                    raise ValueError("Generated code is too short or invalid.")
                    
            except Exception as e:
                print(f"   ⚠️  Attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_retries - 1:
                    print(f"   ⏳ Retrying in 2 seconds...")
                    time.sleep(2)
                else:
                    print(f"   🔄 All attempts failed, using fallback generator...")
                    return self._generate_fallback_function(columns)
        
        raise ValueError("Unexpected error in retry loop.")

    def _extract_code(self, response_text: str) -> str:
        """Extract Python code from markdown code blocks."""
        if response_text is None:
            raise ValueError("Gemini API returned None response. Please try again.")
        
        # Try to extract from markdown code blocks
        patterns = [
            r'```python\n(.*?)\n```',  # ```python ... ```
            r'```\n(.*?)\n```',        # ``` ... ```
            r'```(.*?)```',            # ```...``` (single line)
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, response_text, re.DOTALL)
            if matches:
                code = matches[0].strip()
                if code and len(code) > 10:  # Basic validation
                    return code
        
        # If no code blocks found, try to find Python code without markdown
        lines = response_text.split('\n')
        code_lines = []
        in_code = False
        
        for line in lines:
            # Skip markdown formatting lines
            if line.strip().startswith('```'):
                in_code = not in_code
                continue
            
            # If we're in a code block or line looks like Python code
            if in_code or (line.strip() and not line.strip().startswith('#')):
                code_lines.append(line)
        
        if code_lines:
            code = '\n'.join(code_lines).strip()
            if code and len(code) > 10:
                return code
        
        # Last resort: return the text as-is if it looks like code
        cleaned_text = response_text.strip()
        if cleaned_text and len(cleaned_text) > 10 and not cleaned_text.startswith('```'):
            return cleaned_text
        
        raise ValueError("No valid Python code found in response.")

    def _generate_fallback_function(self, columns: list) -> str:
        """Generate a simple fallback function when API fails."""
        print(f"   🔧 Generating fallback function for {len(columns)} columns...")
        
        function_code = """import random
import string
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()

def generate_row():
    return {"""
        
        for i, col in enumerate(columns):
            if i > 0:
                function_code += ",\n        "
            else:
                function_code += "\n        "
            
            # Simple heuristics for column types
            col_lower = col.lower()
            if any(word in col_lower for word in ['id', 'key', 'index']):
                function_code += f'"{col}": random.randint(1, 10000)'
            elif any(word in col_lower for word in ['date', 'time', 'created', 'updated']):
                function_code += f'"{col}": fake.date_between(start_date="-1y", end_date="today").strftime("%Y-%m-%d")'
            elif any(word in col_lower for word in ['email', 'mail']):
                function_code += f'"{col}": fake.email()'
            elif any(word in col_lower for word in ['name', 'title']):
                function_code += f'"{col}": fake.name()'
            elif any(word in col_lower for word in ['amount', 'price', 'cost', 'revenue', 'value']):
                function_code += f'"{col}": round(random.uniform(10, 1000), 2)'
            elif any(word in col_lower for word in ['count', 'number', 'quantity']):
                function_code += f'"{col}": random.randint(1, 100)'
            elif any(word in col_lower for word in ['status', 'type', 'category']):
                function_code += f'"{col}": random.choice(["active", "inactive", "pending", "completed"])'
            else:
                function_code += f'"{col}": fake.word()'
        
        function_code += "\n    }"
        
        return function_code

    def list_available_models(self):
        """List all available models for debugging."""
        try:
            print("📋 Available models:")
            for model in self.client.models.list():
                print(f"   - {model.name}")
        except Exception as e:
            print(f"❌ Error listing models: {e}")

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


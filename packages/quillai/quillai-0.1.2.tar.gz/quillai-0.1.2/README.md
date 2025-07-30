# QuillAI Python Package

A Python package for interfacing with the Quill Express API, providing AI-powered financial data processing capabilities using SEC filings and earnings transcripts.

## Installation

```bash
pip install quillai
```

## Quick Start

### Simple Usage (Basic DataFrame)

```python
import pandas as pd
from quillai import fillDfModel

# Real example using BOK Financial Corporation (BOKF) data
# Historical quarterly data from 2021 Q3 to 2023 Q2
financial_data = {
    '3Q21': [191206, 1274, 38941, 2580],    # As of 9/30/21
    '4Q21': [186736, 1242, 44471, 2516],    # As of 12/31/21
    '1Q22': [178373, 1394, 40975, 2354],    # As of 3/31/22
    '2Q22': [204015, 1559, 22958, 3485],    # As of 6/30/22
    '3Q22': [264350, 1684, 22720, 9108],    # As of 9/30/22
    '4Q22': [329915, 1390, 28395, 9125],    # As of 12/31/22
    '1Q23': [367870, 979, 34009, 8928],     # As of 3/31/23
    '2Q23': [399182, 1092, 47821, 8586],    # As of 6/30/23
}

# Create DataFrame with line items as index
line_items = [
    'Loans',
    'Residential mortgage loans held for sale',
    'Trading securities',
    'Investment securities'
]

df = pd.DataFrame(financial_data, index=line_items)

# Get AI predictions for the next quarter
updated_df = fillDfModel(df, company="BOKF")
print(updated_df)

# Shows predictions for 3Q23:
# Loans: $447,114
# Residential mortgage loans held for sale: $1,348
# Trading securities: $74,801
# Investment securities: $7,564
```

### Detailed Usage (With Citations and Metadata)

```python
import pandas as pd
from quillai import fillDfModelDetailed

# Same data setup as above...
df = pd.DataFrame(financial_data, index=line_items)

# Get detailed predictions with citations and metadata
detailed_result = fillDfModelDetailed(df, company="BOKF")

# Access the DataFrame (same as fillDfModel output)
print(detailed_result.dataframe)

# Access detailed prediction metadata
print(f"Next Period: {detailed_result.next_period}")
print(f"API Version: {detailed_result.version}")

# Access individual predictions with citations
for i, prediction in enumerate(detailed_result.predictions):
    line_item = df.index[i]
    print(f"\n{line_item}:")
    print(f"  Predicted Value: ${prediction.value:,}")
    print(f"  Citation Link: {prediction.citation_href}")

# Example output:
# Loans:
#   Predicted Value: $447,114
#   Citation Link: http://localhost:5173/filing/0000875357/...
```

### Expected Output

The function returns an updated DataFrame with your original data plus AI predictions for the next period:

```
                                            3Q21    4Q21    1Q22    2Q22    3Q22    4Q22    1Q23    2Q23    3Q23
Loans                                     191206  186736  178373  204015  264350  329915  367870  399182  447114
Residential mortgage loans held for sale    1274    1242    1394    1559    1684    1390     979    1092    1348
Trading securities                         38941   44471   40975   22958   22720   28395   34009   47821   74801
Investment securities                       2580    2516    2354    3485    9108    9125    8928    8586    7564
```

## Example Script

For a complete working example, see the included test script:
```bash
python test_bokf.py
```

This demonstrates the full workflow with real BOK Financial Corporation data.

## Features

- **AI-Powered Predictions**: Uses machine learning to predict financial values based on SEC filings and earnings transcripts
- **Easy DataFrame Integration**: Works seamlessly with pandas DataFrames
- **Automatic Period Detection**: Handles quarterly and fiscal year periods automatically
- **Company-Specific Analysis**: Tailored predictions based on individual company data
- **Simple & Detailed Modes**: Choose between simple DataFrame output or detailed results with citations and metadata
- **Source Citations**: Get direct links to SEC filing sections that support each prediction
- **Transparent Results**: Access both predicted values and their supporting documentation

## Setup

Before using QuillAI, you'll need to set up your API key:

1. **Get your API key** from [Quill AI](https://quillai.com)
2. **Set environment variable**:
   ```bash
   export QUILL_API_KEY='your_api_key_here'
   ```
   Or add it to your `.env` file:
   ```
   QUILL_API_KEY=your_api_key_here
```

## Environment Variables

- `QUILL_API_KEY`: Your Quill API token (required)
- `QUILL_EXPRESS_BASE`: Base URL for the API (default: "express.quillai.com")

## License

MIT License

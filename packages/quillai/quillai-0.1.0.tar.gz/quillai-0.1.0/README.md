# QuillAI Python Package

A Python package for interfacing with the Quill Express API, providing AI-powered financial data processing capabilities using SEC filings and earnings transcripts.

## Installation

```bash
pip install quillai
```

## Quick Start

```python
import pandas as pd
from quillai import fillDfModel

# Create a DataFrame with financial data
data = {
    '1Q23': [1000, 500, 200],
    '2Q23': [1100, 550, 220], 
    '3Q23': [1200, 600, 240],
    '4Q23': [1300, 650, 260],
    '1Q24': [1400, 700, 280],
    '2Q24': [1500, 750, 300],
    '3Q24': [1600, 800, 320],
    '4Q24': [1700, 850, 340]
}
df = pd.DataFrame(data, index=['Revenue', 'Cost of Sales', 'Operating Expenses'])

# Fill the model for the next quarter with AI predictions
updated_df = fillDfModel(df, company="AAPL")
print(updated_df)  # Shows original data plus predictions for the next period
```

## Features

- **AI-Powered Predictions**: Uses machine learning to predict financial values based on SEC filings and earnings transcripts
- **Easy DataFrame Integration**: Works seamlessly with pandas DataFrames
- **Automatic Period Detection**: Handles quarterly and fiscal year periods automatically
- **Company-Specific Analysis**: Tailored predictions based on individual company data

## Environment Variables

- `QUILL_API_KEY`: Your Quill API token (required)
- `QUILL_EXPRESS_BASE`: Base URL for the API (default: "express.quillai.com")

## License

MIT License

"""
Main client module for Quill API interactions.
"""

import os
import re
from typing import Dict, List, Optional, Tuple, Union, Any
import pandas as pd
import requests


def fillDfModel(
    df: pd.DataFrame, 
    company: str,
    base_url: Optional[str] = None,
    token: Optional[str] = None
) -> pd.DataFrame:
    """
    Fill a financial model DataFrame using Quill's AI-powered data extraction.
    
    This function takes a pandas DataFrame containing historical financial data
    and uses Quill's API to predict values for the next period based on 
    SEC filings and earnings transcripts.
    
    Args:
        df: DataFrame with line items as index and periods as columns.
            Periods should be in format like '1Q23', '2Q24', 'FY23', etc.
            Example:
                        1Q23  2Q23  3Q23  4Q23
            Revenue     1000  1100  1200  1300
            Expenses     800   850   900   950
            
        company: Company ticker symbol or name (e.g., 'AAPL', 'Apple Inc.')
        
        base_url: Optional base URL for the API. If not provided, uses 
                 QUILL_EXPRESS_BASE environment variable or defaults to
                 'express.quillai.com'
                 
        token: Optional API token. If not provided, uses QUILL_API_KEY
               environment variable.
    
    Returns:
        Updated DataFrame containing the original data plus a new column with 
        predicted values for the next period.
        
    Raises:
        ValueError: If DataFrame format is invalid or required parameters missing
        requests.RequestException: If API request fails
        
    Example:
        >>> import pandas as pd
        >>> from quill import fillDfModel
        >>> 
        >>> data = {
        ...     '1Q23': [1000, 500],
        ...     '2Q23': [1100, 550], 
        ...     '3Q23': [1200, 600],
        ...     '4Q23': [1300, 650]
        ... }
        >>> df = pd.DataFrame(data, index=['Revenue', 'Cost of Sales'])
        >>> updated_df = fillDfModel(df, company="AAPL")
        >>> print(updated_df)  # Shows original data plus predicted 1Q24 column
    """
    
    # Validate inputs
    if df.empty:
        raise ValueError("DataFrame cannot be empty")
    
    if not company.strip():
        raise ValueError("Company parameter cannot be empty")
    
    # Get configuration
    api_token = token or os.getenv('QUILL_API_KEY')
    if not api_token:
        raise ValueError("API token required. Set QUILL_API_KEY environment variable or pass token parameter.")
    
    api_base = base_url or os.getenv('QUILL_EXPRESS_BASE', 'express.quillai.com')
    if not api_base.startswith(('http://', 'https://')):
        api_base = f"https://{api_base}"
    
    # Parse periods and validate format
    periods = _parse_periods(df.columns.tolist())
    if len(periods) < 2:
        raise ValueError("DataFrame must contain at least 2 periods")
    
    # Get the most recent period as lastPeriod
    last_period = periods[-1]
    
    # Build scrollback items (last 8 quarters)
    scrollback_items = _build_scrollback_items(df, periods)
    
    # Prepare API request
    request_data = {
        "token": api_token,
        "company": company.strip(),
        "newCol": "Z",  # Placeholder - not used in this context
        "lastPeriod": last_period,
        "lastCol": "Y",  # Placeholder - not used in this context  
        "convertToZeros": False,
        "newLineItems": False,
        "strict": False,
        "generateAiResponses": True,
        "labelsCol": "A",  # Placeholder - not used in this context
        "lastExcelRow": len(df),
        "scrollbackItems": scrollback_items,
        "selectedRowsString": "all rows",
        "labelsList": df.index.tolist()
    }
    
    # Make API request
    url = f"{api_base}/api/v1/quillUpdateCol"
    
    try:
        response = requests.post(
            url,
            json=request_data,
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'quill-python/0.1.0'
            },
            timeout=60
        )
        response.raise_for_status()
        api_response = response.json()
        
        # Parse the API response and create updated DataFrame
        return _create_updated_dataframe(df, api_response, periods)
        
    except requests.exceptions.RequestException as e:
        raise requests.RequestException(f"API request failed: {str(e)}")


def _parse_periods(columns: List[str]) -> List[str]:
    """
    Parse and validate period column names.
    
    Expected formats: 1Q23, 2Q24, FY23, etc.
    """
    period_pattern = re.compile(r'^(\d{1}Q\d{2}|FY\d{2})$')
    periods = []
    
    for col in columns:
        col_clean = str(col).strip().upper()
        if period_pattern.match(col_clean):
            periods.append(col_clean)
        else:
            # Try to extract period from more complex column names
            match = re.search(r'(\d{1}Q\d{2}|FY\d{2})', col_clean)
            if match:
                periods.append(match.group(1))
            else:
                raise ValueError(f"Invalid period format: {col}. Expected format like '1Q23', '2Q24', 'FY23'")
    
    # Sort periods chronologically
    periods.sort(key=_period_sort_key)
    return periods


def _period_sort_key(period: str) -> Tuple[int, int]:
    """Generate sort key for chronological period ordering."""
    if period.startswith('FY'):
        year = int('20' + period[2:])
        return (year, 5)  # FY comes after Q4
    else:
        quarter = int(period[0])
        year = int('20' + period[2:])
        return (year, quarter)


def _build_scrollback_items(df: pd.DataFrame, periods: List[str]) -> List[List[Union[str, List[str], List[int]]]]:
    """
    Build scrollback items for the last 8 quarters of data.
    
    Returns list of tuples: [period, col_letter, values, formulas, rows]
    """
    scrollback_items = []
    
    # Take last 8 periods (or all if less than 8)
    recent_periods = periods[-8:] if len(periods) >= 8 else periods
    
    for i, period in enumerate(recent_periods):
        if period not in df.columns:
            continue
            
        # Get values for this period
        values = []
        formulas = []
        rows = []
        
        for row_idx, (line_item, value) in enumerate(df[period].items()):
            # Convert value to string, handle NaN/None
            if pd.isna(value):
                str_value = ""
            else:
                str_value = str(value)
            
            values.append(str_value)
            
            # For formulas, use the value as-is (could be enhanced to detect actual Excel formulas)
            formulas.append(str_value if str_value else "")
            
            # Row numbers (1-indexed for Excel compatibility)
            rows.append(row_idx + 1)
        
        # Column letter (A, B, C, etc.)
        col_letter = chr(ord('A') + i)
        
        scrollback_items.append([
            period,
            col_letter, 
            values,
            formulas,
            rows
        ])
    
    return scrollback_items


def _create_updated_dataframe(df: pd.DataFrame, api_response: Dict[str, Any], periods: List[str]) -> pd.DataFrame:
    """
    Create an updated DataFrame with predicted values from the API response.
    
    Args:
        df: Original DataFrame
        api_response: API response containing predicted values
        periods: List of periods from the original DataFrame
    
    Returns:
        Updated DataFrame with new column containing predicted values
    """
    # Create a copy of the original DataFrame
    updated_df = df.copy()
    
    # Generate the next period name
    next_period = _get_next_period(periods[-1])
    
    # Extract predicted values from API response
    predicted_values = _extract_predicted_values(api_response, len(df))
    
    # Add new column with predicted values
    updated_df[next_period] = predicted_values
    
    return updated_df


def _get_next_period(last_period: str) -> str:
    """
    Generate the next period name based on the last period.
    
    Args:
        last_period: Last period in format like '2Q23', '4Q23', 'FY23'
    
    Returns:
        Next period name
    """
    if last_period.startswith('FY'):
        # For fiscal year, increment year
        year = int(last_period[2:])
        return f"FY{year + 1:02d}"
    else:
        # For quarters
        quarter = int(last_period[0])
        year = int(last_period[2:])
        
        if quarter == 4:
            # Q4 -> Q1 of next year
            return f"1Q{year + 1:02d}"
        else:
            # Q1/Q2/Q3 -> next quarter same year
            return f"{quarter + 1}Q{year:02d}"


def _extract_predicted_values(api_response: Dict[str, Any], num_rows: int) -> List[Union[int, float]]:
    """
    Extract predicted values from the API response.
    
    Args:
        api_response: API response containing results
        num_rows: Expected number of rows/values
    
    Returns:
        List of predicted values
    """
    predicted_values = []
    
    # Get results from API response
    results = api_response.get('results', [])
    
    for i in range(num_rows):
        if i < len(results):
            result = results[i]
            text = result.get('text', '')
            
            # Parse the formula to extract numeric value
            # Format is typically "=447114+QUILL_PH(0)" or similar
            value = _parse_formula_value(text)
            predicted_values.append(value)
        else:
            # If no result for this row, use None
            predicted_values.append(None)
    
    return predicted_values


def _parse_formula_value(formula: str) -> Union[int, float, None]:
    """
    Parse a formula string to extract the numeric value.
    
    Args:
        formula: Formula string like "=447114+QUILL_PH(0)"
    
    Returns:
        Numeric value or None if parsing fails
    """
    if not formula:
        return None
        
    # Remove leading equals sign if present
    formula = formula.lstrip('=')
    
    # Extract the first number from the formula
    # Look for patterns like "447114+QUILL_PH(0)" or just "447114"
    match = re.search(r'^(\d+(?:\.\d+)?)', formula)
    
    if match:
        value_str = match.group(1)
        try:
            # Try to convert to int first, then float
            if '.' in value_str:
                return float(value_str)
            else:
                return int(value_str)
        except ValueError:
            return None
    
    return None

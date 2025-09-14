# Brazilian Stock Fundamental Analysis Screener

A comprehensive tool for analyzing Brazilian stocks using fundamental indicators to find great investment opportunities. This screener uses company financial indicators such as P/L (Price/Earnings), profit margins, EV/EBITDA, and Debt/EBITDA ratios with sector-specific criteria.

## Features

- **Sector-Specific Analysis**: Different screening criteria for different sectors (Banking, Commodities, Technology, Industrial)
- **Comprehensive Metrics**: Analyzes P/L, ROE, profit margins, EV/EBITDA, debt ratios, and dividend yields
- **Brazilian Market Focus**: Designed specifically for Brazilian stocks using the fundamentus library
- **Flexible Screening**: Customizable criteria with command-line interface
- **Mock Data Support**: Includes sample data for testing and demonstration

## Supported Sectors

- **Financial Sector** (Financeiros): Banks and financial institutions
- **Commodity Sectors**: Mining (Mineração), Oil & Gas (Petróleo e Gás)
- **Technology Sector** (Software e Dados): Software and technology companies
- **Industrial Sectors**: Manufacturing, chemicals, construction, automotive, etc.

## Installation

1. Clone this repository:
```bash
git clone https://github.com/vitorwashiya/fundamental_analysis.git
cd fundamental_analysis
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Command Line Interface

#### Basic Usage

```bash
# Show top 5 investment opportunities (using mock data)
python main.py --mock --top 5

# Screen specific sectors
python main.py --mock --sectors FINANCEIROS,MINERACAO

# Analyze a specific stock
python main.py --mock --symbol ITUB4

# Screen all sectors with default criteria
python main.py --mock
```

#### Advanced Filtering

```bash
# Custom criteria: P/E <= 15, ROE >= 15%, Debt/EBITDA <= 2.0
python main.py --mock --max-pe 15 --min-roe 0.15 --max-debt-ebitda 2.0 --top 10

# Focus on dividend stocks
python main.py --mock --min-dividend-yield 0.05 --top 5

# Conservative screening
python main.py --mock --max-pe 12 --min-roe 0.12 --min-margin 0.08 --max-debt-ebitda 3.0
```

### Python API

```python
from src.fundamental_screener import FundamentalScreener, ScreeningCriteria, Sector

# Initialize screener (with mock data for demo)
screener = FundamentalScreener(use_mock_data=True)

# Get top opportunities across all sectors
top_stocks = screener.get_top_opportunities(max_results=5)

# Screen specific sector
bank_stocks = screener.screen_sector(Sector.FINANCEIROS)

# Analyze specific stock
result = screener.analyze_specific_stock("ITUB4")

# Custom screening criteria
criteria = ScreeningCriteria(
    pl_max=15.0,
    roe_min=0.15,
    divida_liquida_ebitda_max=2.0
)
results = screener.screen_all_sectors(criteria)
```

## Screening Criteria by Sector

### Banking/Financial Sector
- P/L: 3.0 - 12.0
- ROE: Minimum 12%
- Dividend Yield: Minimum 4%
- Debt/EBITDA: Maximum 3.0

### Commodity Sectors (Mining, Oil & Gas)
- P/L: 2.0 - 15.0
- EV/EBITDA: Maximum 8.0
- EBITDA Margin: Minimum 15%
- Debt/EBITDA: Maximum 3.0
- Dividend Yield: Minimum 5%

### Technology Sector
- P/L: Maximum 30.0 (growth premium)
- Net Margin: Minimum 10%
- ROE: Minimum 15%
- Debt/EBITDA: Maximum 2.0 (prefer low debt)

### Industrial Sectors
- P/L: 5.0 - 20.0
- EV/EBITDA: Maximum 12.0
- Net Margin: Minimum 8%
- ROE: Minimum 12%
- Debt/EBITDA: Maximum 3.5

## Key Financial Indicators

- **P/L (Price/Earnings)**: Valuation metric comparing price to earnings
- **ROE (Return on Equity)**: Measures company's profitability relative to equity
- **Net Margin**: Percentage of revenue that becomes profit
- **EV/EBITDA**: Enterprise value relative to earnings before interest, taxes, depreciation
- **Debt/EBITDA**: Debt level relative to cash generation ability
- **Dividend Yield**: Annual dividend payment relative to stock price

## Architecture

The screener follows a modular design with clear separation of concerns:

- `models.py`: Data structures for stocks, sectors, and criteria
- `data_provider.py`: Abstract interface with fundamentus and mock implementations
- `sector_screeners.py`: Sector-specific screening logic
- `screener.py`: Main coordination class
- `cli.py`: Command-line interface

## Examples with Mock Data

Since the repository includes mock data, you can immediately test the screener:

```bash
# See all available options
python main.py --help

# Quick demo - top 3 opportunities
python main.py --mock --top 3

# Banking sector analysis
python main.py --mock --sectors FINANCEIROS

# Conservative dividend-focused screening
python main.py --mock --min-dividend-yield 0.06 --max-pe 12 --min-roe 0.15
```

## Real Data Usage

To use real data from fundamentus.com.br instead of mock data, simply omit the `--mock` flag:

```bash
# Screen with real market data (requires internet connection)
python main.py --top 5
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for educational and research purposes only. It does not constitute financial advice. Always conduct your own research and consult with qualified financial advisors before making investment decisions.
# FinPull - Comprehensive Financial Data Scraper

A powerful, cross-platform financial data scraping tool that fetches comprehensive financial data from multiple sources with fallback mechanisms.

## Features

- **Multiple Data Sources**: Supports Finviz and Yahoo Finance with intelligent fallback
- **Cross-Platform**: Compatible with Python, WASM, and executable environments
- **Multiple Interfaces**: GUI (Tkinter), CLI, and programmatic API
- **Export Options**: JSON, CSV, and Excel formats
- **Data Persistence**: Automatic caching and storage
- **Error Handling**: Robust fallback mechanisms and rate limiting

## Installation

### From PyPI (Recommended)
```bash
# Install with full functionality
pip install finpull[full]

# Or install with specific features only
pip install finpull[scraping]  # For web scraping only
pip install finpull[yahoo]     # For Yahoo Finance only  
pip install finpull[excel]     # For Excel export only
```

### From Source
```bash
git clone https://github.com/Lavarite/FinPull
cd FinPull
pip install -e .[full]
```

### For Development
```bash
git clone https://github.com/Lavarite/FinPull
cd FinPull
pip install -e .[full]
pip install -r requirements.txt
```

## Quick Start

### GUI Mode (Default)
```bash
python -m finpull
```

### CLI Mode
```bash
python -m finpull --cli
```

### As a Library
```python
from finpull import FinancialDataScraper

scraper = FinancialDataScraper()
scraper.add_ticker("AAPL")
data = scraper.get_all_data()
```

## Dependencies

### Required
- Python 3.7+

### Optional (for full functionality)
- `requests` - Web scraping
- `beautifulsoup4` - HTML parsing
- `yfinance` - Yahoo Finance data
- `tkinter` - GUI interface (usually included with Python)
- `openpyxl` - Excel export

## Project Structure

```
FinPull/
├── src/finpull/           # Main package
│   ├── core/                 # Core functionality
│   ├── interfaces/           # User interfaces
│   └── utils/               # Utilities
└── docs/                    # Documentation
```

## Usage Examples

### Adding and Managing Tickers
```python
from finpull import FinancialDataScraper

scraper = FinancialDataScraper()

# Add tickers
scraper.add_ticker("AAPL")
scraper.add_ticker("GOOGL")

# Refresh data
scraper.refresh_data("AAPL")  # Single ticker
scraper.refresh_data()        # All tickers

# Export data
filename = scraper.export_data("xlsx")
print(f"Data exported to {filename}")
```

### Batch Processing
```python
from finpull.utils.batch import batch_fetch_tickers

tickers = ["AAPL", "GOOGL", "MSFT", "TSLA"]
results = batch_fetch_tickers(tickers)

for data in results:
    print(f"{data.ticker}: {data.price}")
```

## Command Line Interface

### Available Commands
- `add` - Add a new ticker
- `remove` - Remove a ticker
- `list` - List all tickers and basic info
- `refresh` - Refresh data for ticker(s)
- `export` - Export data to file
- `clear` - Clear all data
- `help` - Show help

### Example Session
```bash
$ python -m finpull --cli
Financial Data Scraper CLI
Commands: add, remove, list, refresh, export, clear, quit

Enter command: add
Enter ticker: AAPL
Added AAPL

Enter command: list
Ticker     Company                        Price      P/E      Market Cap     
--------------------------------------------------------------------------------
AAPL       Apple Inc.                     150.00     25.5     2.5T           

Enter command: export
Enter format (json/csv/xlsx): csv
Data exported to financial_export_20231215_143022.csv
```

## Web/WASM Environment

The scraper is compatible with Pyodide/WASM environments:

```javascript
// In a web environment with Pyodide
let result = pyodide_financial_scraper.add_ticker("AAPL");
let data = pyodide_financial_scraper.get_data();
```

## Configuration

### Environment Variables
- `FINPULL_STORAGE_FILE` - Custom storage file path
- `FINPULL_RATE_LIMIT` - Rate limit delay in seconds

### Data Sources Priority
1. Finviz (primary)
2. Yahoo Finance (fallback)
3. N/A values (when sources unavailable)

## Error Handling

The application includes comprehensive error handling:
- Network timeout and retry logic
- Rate limiting compliance
- Graceful fallback between data sources
- Data validation and sanitization

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and feature requests, please use the GitHub issue tracker.

## Changelog

### v1.0.0
- Initial release
- Multi-source financial data scraping
- GUI, CLI, and API interfaces
- Export to JSON, CSV, and Excel
- Cross-platform compatibility 
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
pip install finpull
```

**Windows Users**: If you encounter permission errors, use:
```bash
pip install finpull --user
```
Or run Command Prompt as Administrator.

### From Source
```bash
git clone https://github.com/Lavarite/FinPull
cd FinPull
pip install -e .
```

### For Development
```bash
git clone https://github.com/Lavarite/FinPull
cd FinPull
pip install -e .
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

### Required
- `requests` - Web scraping from Finviz
- `beautifulsoup4` - HTML parsing  
- `yfinance` - Yahoo Finance data
- `openpyxl` - Excel export functionality

### System Dependencies
- `tkinter` - GUI interface (included with most Python installations)

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

# Get data for a ticker (automatically adds if not present)
data = scraper.get_ticker_data("V")

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

### Command Line Examples
```bash
# Automatically fetch and display ticker data
finpull show AAPL GOOGL MSFT
# Output: 🔍 AAPL not found. Fetching data...
#         ✅ Added AAPL
#         [Displays detailed data for each ticker]

# Add multiple tickers
finpull add GOOGL TSLA NVDA

# Export with format flags and custom path
finpull export ~/Desktop/stocks.csv --csv
finpull export --json  # Uses file dialog
finpull export ~/data/portfolio.xlsx -x

# Interactive mode - same commands work
finpull -i
finpull> add V AAPL GOOG
finpull> export ~/Desktop/ --json
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

### v1.0.9
- **Enhanced Export**: Added format flags `--json/-j`, `--csv/-c`, `--xlsx/-x` for all modes
- **Smart Path Handling**: Export commands with paths skip location prompts (`~/Desktop/` now works)
- **GUI Improvements**: All export formats now use file dialogs for better UX
- **Multi-ticker Support**: All commands now support multiple tickers in both CLI and interactive modes

### v1.0.8
- **Fixed**: Multiple ticker arguments now work correctly (`finpull add V AAPL GOOG`)
- **Fixed**: Interactive mode command parsing with proper argument handling

### v1.0.7
- **New Feature**: No administrator rights required - uses user home directory for storage
- **Enhanced**: Permission errors are handled gracefully with user-friendly messages
- **GUI Access**: Multiple ways to launch GUI (`finpull`, `finpull -g`, `finpull --gui`)

### v1.0.3
- **New Feature**: `finpull show <ticker>` now automatically fetches and adds tickers if not present

### v1.0.2
- **Breaking Change**: Full dependencies now install by default with `pip install finpull`
- Removed mock data fallback - returns N/A values when sources unavailable

### v1.0.1
- Improved dependency management with optional extras
- Enhanced error handling and fallback mechanisms

### v1.0.0
- Initial release
- Multi-source financial data scraping
- GUI, CLI, and API interfaces
- Export to JSON, CSV, and Excel
- Cross-platform compatibility 
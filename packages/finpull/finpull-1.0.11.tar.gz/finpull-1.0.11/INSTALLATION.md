# FinPull Installation Guide

## Quick Start

### 1. Clone or Download
```bash
git clone <repository-url>
cd FinPull
```

### 2. Install Dependencies (Optional)
For full functionality, install the optional dependencies:
```bash
pip install -r requirements.txt
```

**Note**: FinPull works without external dependencies using mock data fallback.

### 3. Run the Application

#### GUI Mode (Default)
```bash
PYTHONPATH=src python3 -m finpull
```

#### CLI Mode
```bash
PYTHONPATH=src python3 -m finpull --cli
```

#### As a Python Library
```python
import sys
sys.path.insert(0, 'src')
from finpull import FinancialDataScraper

scraper = FinancialDataScraper()
scraper.add_ticker("AAPL")
data = scraper.get_all_data()
```

## Dependencies

### Required
- Python 3.7+

### Optional (for enhanced functionality)
- `requests` - Web scraping from Finviz
- `beautifulsoup4` - HTML parsing
- `yfinance` - Yahoo Finance data
- `openpyxl` - Excel export
- `tkinter` - GUI interface (usually included with Python)

## Installation Methods

### Method 1: Development Installation
```bash
pip install -e .
```

### Method 2: Standard Installation
```bash
pip install .
```

### Method 3: Direct Run (No Installation)
Use `PYTHONPATH=src` prefix as shown in the Quick Start.

## Troubleshooting

### Import Errors
If you get import errors, ensure you're using the correct Python path:
```bash
PYTHONPATH=src python3 your_script.py
```

### Missing GUI
If GUI doesn't work:
- On Ubuntu/Debian: `sudo apt-get install python3-tk`
- On macOS: tkinter is usually included with Python
- On Windows: tkinter is usually included with Python

### Missing Dependencies
Run the dependency check:
```bash
PYTHONPATH=src python3 -c "from finpull.utils.compatibility import print_dependency_status; print_dependency_status()"
```

## Platform Support

- ✅ Linux
- ✅ macOS  
- ✅ Windows
- ✅ WASM/Pyodide (web environments)

## Next Steps

1. Read the [README.md](README.md) for usage instructions
2. Run the demo: `python3 run_demo.py` 
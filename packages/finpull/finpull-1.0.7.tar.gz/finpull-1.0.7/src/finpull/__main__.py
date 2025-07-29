#!/usr/bin/env python3
"""
Main entry point for FinPull package
Handles command-line execution and interface selection
"""

import sys
import argparse
import logging
from .interfaces.cli import FinancialDataCLI
from .interfaces.api import FinancialDataAPI
from .utils.compatibility import HAS_TKINTER, get_available_features

# Setup logging
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_parser():
    """Create command-line argument parser"""
    parser = argparse.ArgumentParser(
        prog='finpull',
        description='FinPull - Professional Financial Data Scraper',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
        Examples:
        finpull show AAPL             # Auto-fetch and show Apple stock
        finpull add GOOGL             # Manually add Google stock  
        finpull show --summary        # Show all tickers summary
        finpull export --format json # Export data to JSON
        finpull refresh               # Refresh all data
        finpull --gui                 # Launch GUI interface
        finpull --interactive         # Interactive CLI mode
        """
    )
    
    # Interface mode arguments
    interface_group = parser.add_mutually_exclusive_group()
    interface_group.add_argument('--gui', '-g', action='store_true', help='Launch GUI interface')
    interface_group.add_argument('--interactive', '-i', action='store_true', help='Interactive CLI mode')
    interface_group.add_argument('--api', action='store_true', help='API mode for programmatic use')
    
    # Commands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add one or more tickers')
    add_parser.add_argument('tickers', nargs='+', help='One or more stock ticker symbols (e.g., AAPL TSLA)')
    
    # Remove command
    remove_parser = subparsers.add_parser('remove', help='Remove a ticker')
    remove_parser.add_argument('ticker', help='Stock ticker symbol to remove')
    
    # Show command
    show_parser = subparsers.add_parser('show', help='Show ticker data (auto-fetches if not present)')
    show_parser.add_argument('ticker', nargs='?', help='Ticker to show (will auto-add if not tracked)')
    show_parser.add_argument('--summary', action='store_true', help='Show summary for all tickers')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export data to file')
    export_parser.add_argument('--format', choices=['json', 'csv', 'xlsx'], default='json', help='Export format')
    export_parser.add_argument('--output', '-o', help='Output file path')
    
    # Refresh command
    refresh_parser = subparsers.add_parser('refresh', help='Refresh ticker data')
    refresh_parser.add_argument('ticker', nargs='?', help='Specific ticker to refresh (optional)')
    
    # Stats command
    subparsers.add_parser('stats', help='Show scraper statistics')
    
    # List command
    subparsers.add_parser('list', help='List all tracked tickers')
    
    # Clear command
    clear_parser = subparsers.add_parser('clear', help='Clear all data')
    clear_parser.add_argument('--force', action='store_true', help='Skip confirmation')
    
    return parser

def handle_command(args):
    """Handle command-line commands"""
    from . import FinancialDataScraper
    
    scraper = FinancialDataScraper()
    
    try:
        if args.command == 'add':
            added = 0
            for tk in args.tickers:
                try:
                    if scraper.add_ticker(tk):
                        print(f"✅ Added {tk.upper()}")
                        added += 1
                    else:
                        print(f"ℹ️  {tk.upper()} already exists")
                except Exception as e:
                    print(f"❌ Failed to add {tk.upper()}: {e}")
            if added:
                print(f"Added {added} new ticker(s)")
                
        elif args.command == 'remove':
            if scraper.has_ticker(args.ticker):
                scraper.remove_ticker(args.ticker)
                print(f"✅ Removed {args.ticker.upper()}")
            else:
                print(f"❌ {args.ticker.upper()} not found")
                
        elif args.command == 'show':
            if args.ticker:
                # Show specific ticker - automatically add if not present
                if not scraper.has_ticker(args.ticker):
                    print(f"🔍 {args.ticker.upper()} not found. Fetching data...")
                    try:
                        scraper.add_ticker(args.ticker)
                        print(f"✅ Added {args.ticker.upper()}")
                    except Exception as e:
                        print(f"❌ Failed to fetch {args.ticker.upper()}: {e}")
                        return 1
                
                data = scraper.get_ticker_data(args.ticker)
                cli = FinancialDataCLI()
                cli.scraper = scraper
                cli._display_detailed_table(data)
            else:
                # Show all tickers
                cli = FinancialDataCLI()
                cli.scraper = scraper
                if args.summary:
                    cli._show_all_tickers_summary()
                else:
                    # Show menu for user to choose
                    data_list = scraper.get_all_data()
                    if not data_list:
                        print("No tickers found. Use 'finpull add TICKER' to add some.")
                    else:
                        print("Available tickers:", ", ".join([d.ticker for d in data_list]))
                        print("Use 'finpull show TICKER' for detailed view")
                        print("Use 'finpull show --summary' for summary table")
                        
        elif args.command == 'export':
            try:
                filename = scraper.export_data(args.format, args.output)
                count = len(scraper.get_all_data())
                print(f"✅ Exported {count} records to {filename}")
            except Exception as e:
                print(f"❌ Export error: {e}")
                
        elif args.command == 'refresh':
            try:
                if args.ticker:
                    scraper.refresh_data(args.ticker)
                    print(f"✅ Refreshed {args.ticker.upper()}")
                else:
                    scraper.refresh_data()
                    print("✅ Refreshed all data")
            except Exception as e:
                print(f"❌ Refresh error: {e}")
                
        elif args.command == 'stats':
            stats = scraper.get_stats()
            print("📊 FinPull Statistics")
            print(f"  Total tickers: {stats['total_tickers']}")
            print(f"  Data sources: {stats['source_count']}")
            print(f"  Storage file: {stats['storage_file']}")
            
        elif args.command == 'list':
            tickers = scraper.get_ticker_list()
            if tickers:
                print("📈 Tracked tickers:", ", ".join(tickers))
            else:
                print("No tickers found. Use 'finpull add TICKER' to add some.")
                
        elif args.command == 'clear':
            ticker_count = len(scraper.get_ticker_list())
            if ticker_count == 0:
                print("No data to clear")
                return
                
            if args.force:
                scraper.clear_all()
                print("✅ All data cleared")
            else:
                confirm = input(f"Clear all {ticker_count} tickers? (y/N): ").strip().lower()
                if confirm == 'y':
                    scraper.clear_all()
                    print("✅ All data cleared")
                else:
                    print("Cancelled")
                    
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

def main():
    """Main function to run appropriate interface"""
    parser = create_parser()
    
    # If no arguments, launch GUI (if available) instead of help
    if len(sys.argv) == 1:
        if HAS_TKINTER:
            try:
                from .interfaces.gui import FinancialDataGUI
                gui = FinancialDataGUI()
                gui.run()
                return 0
            except Exception as e:
                print(f"❌ GUI failed: {e}")
                # Fallback to help
        parser.print_help()
        return 0
    
    args = parser.parse_args()
    
    # Handle interface modes
    if args.gui:
        if HAS_TKINTER:
            try:
                from .interfaces.gui import FinancialDataGUI
                gui = FinancialDataGUI()
                gui.run()
                return 0
            except Exception as e:
                print(f"❌ GUI failed: {e}")
                return 1
        else:
            print("❌ GUI not available (tkinter not found)")
            return 1
            
    elif args.interactive:
        cli = FinancialDataCLI()
        cli.run()
        return 0
        
    elif args.api:
        api = FinancialDataAPI()
        print("🔌 API mode - use programmatically")
        print("Example:")
        print("  from finpull import FinancialDataScraper")
        print("  scraper = FinancialDataScraper()")
        print("  scraper.add_ticker('AAPL')")
        return 0
        
    # Handle specific commands
    elif args.command:
        return handle_command(args)
        
    else:
        parser.print_help()
        return 0

# For WASM/web environments - expose key functions globally
def setup_web_environment():
    """Setup for web/WASM environments"""
    try:
        # This will fail in normal Python but might work in Pyodide/WASM
        import js  # type: ignore
        # Web environment detected
        print("Web environment detected")
        global_api = FinancialDataAPI()
        
        # Expose functions to JavaScript
        js.pyodide_financial_scraper = {
            'add_ticker': global_api.add_ticker,
            'get_data': global_api.get_data,
            'refresh_data': global_api.refresh_data,
            'remove_ticker': global_api.remove_ticker,
            'export_data': global_api.export_data,
            'get_features': lambda: get_available_features()
        }
        print("Financial scraper API exposed to JavaScript")
        return True
        
    except ImportError:
        return False

if __name__ == "__main__":
    # Check if we're in a web environment first
    if not setup_web_environment():
        # Normal Python environment
        sys.exit(main()) 
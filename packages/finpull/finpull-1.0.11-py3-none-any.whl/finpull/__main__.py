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
        epilog="""Examples:
  finpull                    Launch GUI (if available)
  finpull --gui              Launch GUI explicitly
  finpull add AAPL GOOGL     Add multiple tickers
  finpull remove AAPL        Remove a ticker
  finpull show AAPL          Show specific ticker details
  finpull show --full        Show all tickers in detail
  finpull refresh            Refresh all tickers
  finpull refresh AAPL       Refresh specific ticker
  finpull export --csv       Export to CSV format
  finpull export data.json   Export to specific file
"""
    )
    
    # Interface mode arguments
    interface_group = parser.add_mutually_exclusive_group()
    interface_group.add_argument('--gui', '-g', action='store_true', help='Launch GUI interface')
    interface_group.add_argument('--interactive', '-i', action='store_true', help='Interactive CLI mode')
    
    # Commands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add one or more tickers')
    add_parser.add_argument('tickers', nargs='+', help='Ticker symbol(s) to add')
    
    # Remove command
    remove_parser = subparsers.add_parser('remove', help='Remove one or more tickers')
    remove_parser.add_argument('tickers', nargs='+', help='Ticker symbol(s) to remove')
    
    # Show command
    show_parser = subparsers.add_parser('show', help='Show ticker data (summary by default)')
    show_parser.add_argument('tickers', nargs='*', help='Ticker symbol(s) to display')
    show_parser.add_argument('--full', '-f', action='store_true', help='Show detailed view')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export data to file')
    export_parser.add_argument('path', nargs='?', help='Export file path')
    
    # Format options
    export_parser.add_argument('--json', '-j', action='store_true', help='Export as JSON')
    export_parser.add_argument('--csv', '-c', action='store_true', help='Export as CSV') 
    export_parser.add_argument('--xlsx', '-x', action='store_true', help='Export as Excel')
    
    # Refresh command
    refresh_parser = subparsers.add_parser('refresh', help='Refresh data (all by default)')
    refresh_parser.add_argument('tickers', nargs='*', help='Specific ticker(s) to refresh')
    
    # Stats command
    subparsers.add_parser('stats', help='Show statistics')
    
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
            removed = 0
            for tk in args.tickers:
                if scraper.has_ticker(tk):
                    scraper.remove_ticker(tk)
                    print(f"✅ Removed {tk.upper()}")
                    removed += 1
                else:
                    print(f"❌ {tk.upper()} not found")
            if removed:
                print(f"Removed {removed} ticker(s)")
                
        elif args.command == 'show':
            cli = FinancialDataCLI()
            cli.scraper = scraper
            
            if args.tickers:
                # Show specific tickers - automatically add if not present
                for tk in args.tickers:
                    if not scraper.has_ticker(tk):
                        print(f"🔍 {tk.upper()} not found. Fetching data...")
                        try:
                            scraper.add_ticker(tk)
                            print(f"✅ Added {tk.upper()}")
                        except Exception as e:
                            print(f"❌ Failed to fetch {tk.upper()}: {e}")
                            continue
                    
                    data = scraper.get_ticker_data(tk)
                    if data:
                        cli._display_detailed_table(data)
            elif args.full:
                # Show all tickers in detail
                data_list = scraper.get_all_data()
                if not data_list:
                    print("No tickers found. Use 'finpull add TICKER' to add some.")
                else:
                    for data in data_list:
                        cli._display_detailed_table(data)
            else:
                # Show summary by default
                data_list = scraper.get_all_data()
                if not data_list:
                    print("No tickers found. Use 'finpull add TICKER' to add some.")
                else:
                    cli._show_all_tickers_summary()
                        
        elif args.command == 'export':
            try:
                data_list = scraper.get_all_data()
                if not data_list:
                    print("No data to export")
                    return 0
                
                # Determine format
                format_type = None
                if args.json:
                    format_type = 'json'
                elif args.csv:
                    format_type = 'csv'
                elif args.xlsx:
                    format_type = 'xlsx'
                
                import os
                
                # If format specified but no path, ask for path
                if format_type and not args.path:
                    current_dir = os.getcwd()
                    custom_path = input(f"Enter file path (press Enter for current directory: {current_dir}, or # for file dialog): ").strip()
                    if custom_path == "#":
                        # Try to use GUI file dialog
                        try:
                            from .utils.compatibility import HAS_TKINTER
                            if HAS_TKINTER:
                                import tkinter as tk
                                from tkinter import filedialog
                                root = tk.Tk()
                                root.withdraw()  # Hide the main window
                                
                                # Set file types based on format
                                if format_type == 'csv':
                                    filetypes = [("CSV files", "*.csv"), ("All files", "*.*")]
                                    defaultextension = ".csv"
                                elif format_type == 'xlsx':
                                    filetypes = [("Excel files", "*.xlsx"), ("All files", "*.*")]
                                    defaultextension = ".xlsx"
                                else:
                                    filetypes = [("JSON files", "*.json"), ("All files", "*.*")]
                                    defaultextension = ".json"
                                
                                output_path = filedialog.asksaveasfilename(
                                    title=f"Save {format_type.upper()} file",
                                    filetypes=filetypes,
                                    defaultextension=defaultextension
                                )
                                root.destroy()
                                
                                if not output_path:  # User cancelled
                                    print("Export cancelled")
                                    return 0
                            else:
                                print("GUI file dialog not available (tkinter not found)")
                                return 1
                        except Exception as e:
                            print(f"Could not open file dialog: {e}")
                            return 1
                    else:
                        output_path = os.path.expanduser(custom_path) if custom_path else None
                elif args.path:
                    output_path = os.path.expanduser(args.path)
                    # Infer format from extension if not specified
                    if not format_type:
                        if output_path.lower().endswith('.csv'):
                            format_type = 'csv'
                        elif output_path.lower().endswith('.xlsx'):
                            format_type = 'xlsx'
                        else:
                            format_type = 'json'
                else:
                    # No format or path - interactive mode
                    print("\nExport formats:")
                    print("  1. JSON")
                    print("  2. CSV")
                    print("  3. Excel (XLSX)")
                    
                    choice = input("\nSelect format (1-3): ").strip()
                    format_map = {"1": "json", "2": "csv", "3": "xlsx"}
                    if choice not in format_map:
                        print("Invalid choice")
                        return 1
                    format_type = format_map[choice]
                    
                    current_dir = os.getcwd()
                    custom_path = input(f"Enter file path (press Enter for current directory: {current_dir}, or # for file dialog): ").strip()
                    if custom_path == "#":
                        # Try to use GUI file dialog
                        try:
                            from .utils.compatibility import HAS_TKINTER
                            if HAS_TKINTER:
                                import tkinter as tk
                                from tkinter import filedialog
                                root = tk.Tk()
                                root.withdraw()  # Hide the main window
                                
                                # Set file types based on format
                                if format_type == 'csv':
                                    filetypes = [("CSV files", "*.csv"), ("All files", "*.*")]
                                    defaultextension = ".csv"
                                elif format_type == 'xlsx':
                                    filetypes = [("Excel files", "*.xlsx"), ("All files", "*.*")]
                                    defaultextension = ".xlsx"
                                else:
                                    filetypes = [("JSON files", "*.json"), ("All files", "*.*")]
                                    defaultextension = ".json"
                                
                                output_path = filedialog.asksaveasfilename(
                                    title=f"Save {format_type.upper()} file",
                                    filetypes=filetypes,
                                    defaultextension=defaultextension
                                )
                                root.destroy()
                                
                                if not output_path:  # User cancelled
                                    print("Export cancelled")
                                    return 0
                            else:
                                print("GUI file dialog not available (tkinter not found)")
                                return 1
                        except Exception as e:
                            print(f"Could not open file dialog: {e}")
                            return 1
                    else:
                        output_path = os.path.expanduser(custom_path) if custom_path else None
                
                if output_path:
                    filename = scraper.export_data(format_type, output_path)
                else:
                    filename = scraper.export_data(format_type)
                print(f"✅ Exported {len(data_list)} records to {filename}")
            except Exception as e:
                print(f"❌ Export error: {e}")
                
        elif args.command == 'refresh':
            try:
                if args.tickers:
                    # Refresh specific tickers
                    for tk in args.tickers:
                        if not scraper.has_ticker(tk):
                            print(f"❌ {tk.upper()} not tracked")
                            continue
                        try:
                            scraper.refresh_data(tk)
                            print(f"✅ Refreshed {tk.upper()}")
                        except Exception as e:
                            print(f"❌ Error refreshing {tk.upper()}: {e}")
                else:
                    # Refresh all
                    ticker_list = scraper.get_ticker_list()
                    if not ticker_list:
                        print("No tickers to refresh")
                    else:
                        print(f"Refreshing {len(ticker_list)} tickers...")
                        scraper.refresh_data()
                        print("✅ Refreshed all data")
            except Exception as e:
                print(f"❌ Refresh error: {e}")
                
        elif args.command == 'stats':
            stats = scraper.get_stats()
            print("\n📊 FinPull Statistics")
            print(f"Total tickers: {stats['total_tickers']}")
            print(f"Cached tickers: {stats['cached_tickers']}")
            print(f"Missing cache: {stats['missing_cache']}")
            print(f"Stale data: {stats['stale_data']}")
            print(f"Storage file: {stats['storage_file']}")
            print(f"File size: {stats['file_size']} bytes")
            print()
            print("Data sources:")
            for i, source in enumerate(stats['data_sources'], 1):
                print(f"  {i}. {source}")
                
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
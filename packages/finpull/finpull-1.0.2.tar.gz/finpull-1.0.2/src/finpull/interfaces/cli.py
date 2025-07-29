"""
Command-line interface for the financial data scraper
"""

import logging
from typing import List

from ..core.scraper import FinancialDataScraper
from ..utils.compatibility import get_available_features, print_dependency_status

logger = logging.getLogger(__name__)


class FinancialDataCLI:
    """Command-line interface for the financial data scraper"""
    
    def __init__(self):
        self.scraper = FinancialDataScraper()
        print("Financial Data Scraper CLI")
        print("Commands: add, remove, show, refresh, export, stats, deps, clear, help, quit")
        print()
    
    def run(self):
        """Run the CLI interface"""
        while True:
            try:
                command = input("finpull> ").strip().lower()
                
                if command in ["quit", "exit", "q"]:
                    print("Goodbye!")
                    break
                elif command == "add":
                    self._handle_add()
                elif command == "remove":
                    self._handle_remove()
                elif command == "show":
                    self._handle_show()
                elif command == "list":
                    # Redirect 'list' to 'show' for backward compatibility
                    print("Note: 'list' command is deprecated. Use 'show' instead.")
                    self._handle_show()
                elif command == "refresh":
                    self._handle_refresh()
                elif command == "export":
                    self._handle_export()
                elif command == "stats":
                    self._handle_stats()
                elif command == "deps":
                    self._handle_deps()
                elif command == "clear":
                    self._handle_clear()
                elif command == "help":
                    self._handle_help()
                elif command == "":
                    continue  # Empty command
                else:
                    print(f"Unknown command: '{command}'. Type 'help' for available commands.")
                
                print()  # Add spacing between commands
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except EOFError:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
                logger.error(f"CLI error: {e}")
    
    def _handle_add(self):
        """Handle add ticker command"""
        ticker = input("Enter ticker symbol: ").strip()
        if not ticker:
            print("Please enter a ticker symbol")
            return
        
        if not self.scraper.validate_ticker(ticker):
            print(f"'{ticker}' doesn't appear to be a valid ticker symbol")
            return
        
        try:
            if self.scraper.add_ticker(ticker):
                print(f"✓ Added {ticker.upper()}")
            else:
                print(f"! {ticker.upper()} already exists")
        except Exception as e:
            print(f"✗ Error adding {ticker.upper()}: {e}")
    
    def _handle_remove(self):
        """Handle remove ticker command"""
        self._show_ticker_list()
        if not self.scraper.get_ticker_list():
            return
        
        ticker = input("Enter ticker to remove: ").strip()
        if not ticker:
            print("Please enter a ticker symbol")
            return
        
        if not self.scraper.has_ticker(ticker):
            print(f"'{ticker.upper()}' is not being tracked")
            return
        
        confirm = input(f"Remove {ticker.upper()}? (y/N): ").strip().lower()
        if confirm == 'y':
            self.scraper.remove_ticker(ticker)
            print(f"✓ Removed {ticker.upper()}")
        else:
            print("Cancelled")
    

    
    def _handle_show(self):
        """Handle show detailed ticker info command"""
        ticker_list = self.scraper.get_ticker_list()
        if not ticker_list:
            print("No tickers found. Use 'add' to add tickers first.")
            return
        
        print("Show options:")
        print("  1. Show specific ticker in detailed table")
        print("  2. Show all tickers summary")
        
        choice = input("Enter choice (1-2): ").strip()
        
        if choice == "1":
            self._show_specific_ticker()
        elif choice == "2":
            self._show_all_tickers_summary()
        else:
            print("Invalid choice. Showing specific ticker by default.")
            self._show_specific_ticker()
    
    def _show_specific_ticker(self):
        """Show detailed table for a specific ticker"""
        self._show_ticker_list()
        ticker = input("Enter ticker to display: ").strip()
        if not ticker:
            print("Please enter a ticker symbol")
            return
        
        if not self.scraper.has_ticker(ticker):
            print(f"'{ticker.upper()}' is not being tracked")
            return
        
        try:
            data = self.scraper.get_ticker_data(ticker)
            self._display_detailed_table(data)
        except Exception as e:
            print(f"✗ Error displaying {ticker.upper()}: {e}")
    
    def _show_all_tickers_summary(self):
        """Show summary table for all tickers"""
        data_list = self.scraper.get_all_data()
        if not data_list:
            print("No tickers found")
            return
        
        # Enhanced summary table with ASCII formatting
        box_width = 100
        print("+" + "=" * (box_width - 2) + "+")
        print(f"| {'PORTFOLIO SUMMARY':<{box_width - 4}} |")
        print("+" + "=" * (box_width - 2) + "+")
        
        # Header
        print(f"| {'Ticker':<8} | {'Company':<25} | {'Price':<10} | {'P/E':<8} | {'Market Cap':<12} | {'5Y Change':<10} |")
        print("+" + "-" * (box_width - 2) + "+")
        
        # Data rows
        for data in data_list:
            company = data.company_name[:24] if len(data.company_name) > 24 else data.company_name
            price = f"${data.price}" if data.price != "N/A" else "N/A"
            pe_ratio = data.pe_ratio if data.pe_ratio != "N/A" else "N/A"
            market_cap = data.market_cap if data.market_cap != "N/A" else "N/A"
            change_5y = data.change_5y if data.change_5y != "N/A" else "N/A"
            
            print(f"| {data.ticker:<8} | {company:<25} | {price:<10} | {pe_ratio:<8} | {market_cap:<12} | {change_5y:<10} |")
        
        print("+" + "=" * (box_width - 2) + "+")
        print(f"| {'Total Tickers: ' + str(len(data_list)):<{box_width - 4}} |")
        print("+" + "=" * (box_width - 2) + "+")
    
    def _display_detailed_table(self, data):
        """Display financial data in a beautiful ASCII table"""
        ticker = data.ticker
        company = data.company_name
        
        # Calculate box width based on content
        max_width = max(
            len(f"{ticker} - {company}"),
            60  # Minimum width
        )
        box_width = min(max_width + 4, 80)  # Max 80 chars wide
        
        # Header
        print()
        print("+" + "=" * (box_width - 2) + "+")
        title = f"{ticker} - {company}"
        if len(title) > box_width - 4:
            title = title[:box_width - 7] + "..."
        print(f"| {title:<{box_width - 4}} |")
        print("+" + "=" * (box_width - 2) + "+")
        
        # Basic Information Section
        self._print_section_header("BASIC INFORMATION", box_width)
        self._print_table_row("Sector", data.sector, box_width)
        self._print_table_row("Price", f"${data.price}" if data.price != "N/A" else "N/A", box_width)
        self._print_table_row("Market Cap", data.market_cap, box_width)
        
        # Valuation Ratios Section
        self._print_section_header("VALUATION RATIOS", box_width)
        self._print_table_row("P/E Ratio", data.pe_ratio, box_width)
        self._print_table_row("P/S Ratio", data.ps_ratio, box_width)
        self._print_table_row("P/B Ratio", data.pb_ratio, box_width)
        
        # Earnings & Growth Section
        self._print_section_header("EARNINGS & GROWTH", box_width)
        self._print_table_row("EPS (TTM)", data.eps_ttm, box_width)
        self._print_table_row("EPS Next Year", data.eps_next_year, box_width)
        self._print_table_row("EPS Next 5Y", data.eps_next_5y, box_width)
        self._print_table_row("5-Year Change", data.change_5y, box_width)
        
        # Dividend Information Section
        self._print_section_header("DIVIDEND INFORMATION", box_width)
        self._print_table_row("Dividend TTM", data.dividend_ttm, box_width)
        self._print_table_row("Dividend Yield", data.dividend_yield, box_width)
        
        # Performance Metrics Section
        self._print_section_header("PERFORMANCE METRICS", box_width)
        self._print_table_row("ROA", data.roa, box_width)
        self._print_table_row("ROE", data.roe, box_width)
        self._print_table_row("ROI (ROIC)", data.roi, box_width)
        self._print_table_row("Profit Margin", data.profit_margin, box_width)
        self._print_table_row("Operating Margin", data.operating_margin, box_width)
        
        # Financial Position Section
        self._print_section_header("FINANCIAL POSITION", box_width)
        self._print_table_row("Revenue", data.revenue, box_width)
        self._print_table_row("Total Assets", self._format_large_number(data.total_assets), box_width)
        self._print_table_row("Total Liabilities", self._format_large_number(data.total_liabilities), box_width)
        
        # Market Data Section
        self._print_section_header("MARKET DATA", box_width)
        self._print_table_row("Beta", data.beta, box_width)
        self._print_table_row("Volume", self._format_volume(data.volume), box_width)
        self._print_table_row("Avg Volume", data.avg_volume, box_width)
        
        # Footer
        print("+" + "-" * (box_width - 2) + "+")
        timestamp = "N/A"
        if data.timestamp:
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(data.timestamp.replace('Z', '+00:00'))
                timestamp = dt.strftime('%Y-%m-%d %H:%M:%S UTC')
            except:
                timestamp = data.timestamp
        
        footer = f"Last Updated: {timestamp}"
        if len(footer) > box_width - 4:
            footer = footer[:box_width - 7] + "..."
        print(f"| {footer:<{box_width - 4}} |")
        print("+" + "=" * (box_width - 2) + "+")
        print()
    
    def _print_section_header(self, title, box_width):
        """Print a section header in the table"""
        print("+" + "-" * (box_width - 2) + "+")
        print(f"| {title:<{box_width - 4}} |")
        print("+" + "-" * (box_width - 2) + "+")
    
    def _print_table_row(self, label, value, box_width):
        """Print a data row in the table"""
        if value == "N/A" or value is None:
            value = "N/A"
        else:
            value = str(value)
        
        # Calculate spacing
        available_space = box_width - 6  # Account for "| " and " |" and ": "
        label_space = min(len(label), available_space // 2)
        value_space = available_space - label_space - 2  # -2 for ": "
        
        # Truncate if necessary
        if len(label) > label_space:
            label = label[:label_space - 3] + "..."
        if len(value) > value_space:
            value = value[:value_space - 3] + "..."
        
        print(f"| {label:<{label_space}}: {value:<{value_space}} |")
    
    def _format_large_number(self, value):
        """Format large numbers for display"""
        if value == "N/A" or value is None:
            return "N/A"
        
        try:
            num = float(value)
            if num >= 1e9:
                return f"${num/1e9:.1f}B"
            elif num >= 1e6:
                return f"${num/1e6:.1f}M"
            else:
                return f"${num:,.0f}"
        except:
            return str(value)
    
    def _format_volume(self, value):
        """Format volume numbers for display"""
        if value == "N/A" or value is None:
            return "N/A"
        
        try:
            # Remove commas and convert
            clean_value = str(value).replace(',', '')
            num = float(clean_value)
            if num >= 1e9:
                return f"{num/1e9:.1f}B"
            elif num >= 1e6:
                return f"{num/1e6:.1f}M"
            elif num >= 1e3:
                return f"{num/1e3:.1f}K"
            else:
                return f"{num:,.0f}"
        except:
            return str(value)
    
    def _handle_refresh(self):
        """Handle refresh data command"""
        ticker_list = self.scraper.get_ticker_list()
        if not ticker_list:
            print("No tickers to refresh")
            return
        
        print("Refresh options:")
        print("  1. Refresh all tickers")
        print("  2. Refresh specific ticker")
        
        choice = input("Enter choice (1-2): ").strip()
        
        if choice == "1":
            print(f"Refreshing {len(ticker_list)} tickers...")
            try:
                self.scraper.refresh_data()
                print("✓ Refreshed all data")
            except Exception as e:
                print(f"✗ Error refreshing: {e}")
        
        elif choice == "2":
            self._show_ticker_list()
            ticker = input("Enter ticker to refresh: ").strip()
            if not ticker:
                print("Please enter a ticker symbol")
                return
            
            if not self.scraper.has_ticker(ticker):
                print(f"'{ticker.upper()}' is not being tracked")
                return
            
            try:
                self.scraper.refresh_data(ticker)
                print(f"✓ Refreshed {ticker.upper()}")
            except Exception as e:
                print(f"✗ Error refreshing {ticker.upper()}: {e}")
        else:
            print("Invalid choice")
    
    def _handle_export(self):
        """Handle export data command"""
        data_list = self.scraper.get_all_data()
        if not data_list:
            print("No data to export")
            return
        
        print("Export formats:")
        print("  1. JSON")
        print("  2. CSV")
        
        features = get_available_features()
        if features["excel_export"]:
            print("  3. Excel (XLSX)")
        
        choice = input("Enter choice: ").strip()
        
        format_map = {"1": "json", "2": "csv"}
        if features["excel_export"]:
            format_map["3"] = "xlsx"
        
        if choice not in format_map:
            print("Invalid choice")
            return
        
        format_type = format_map[choice]
        
        # Ask for custom export path
        print("\nExport location:")
        print("  1. Default location (current directory)")
        print("  2. Custom path")
        
        path_choice = input("Enter choice (1-2): ").strip()
        custom_filename = None
        
        if path_choice == "2":
            custom_path = input("Enter full file path (e.g., /home/user/data.json): ").strip()
            if custom_path:
                custom_filename = custom_path
            else:
                print("Invalid path, using default location")
        
        try:
            filename = self.scraper.export_data(format_type, custom_filename)
            print(f"✓ Exported {len(data_list)} records to {filename}")
        except Exception as e:
            print(f"✗ Export error: {e}")
    
    def _handle_stats(self):
        """Handle stats command"""
        stats = self.scraper.get_stats()
        
        print("=== FinPull Statistics ===")
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
        
        # Show feature availability
        features = get_available_features()
        print("\nFeatures:")
        for feature, available in features.items():
            status = "✓" if available else "✗"
            print(f"  {status} {feature.replace('_', ' ').title()}")
    
    def _handle_deps(self):
        """Handle dependencies check command"""
        print("=== Dependency Status ===")
        print_dependency_status()
    
    def _handle_clear(self):
        """Handle clear all data command"""
        ticker_count = len(self.scraper.get_ticker_list())
        if ticker_count == 0:
            print("No data to clear")
            return
        
        print(f"This will remove all {ticker_count} tickers and cached data.")
        confirm = input("Are you sure? (y/N): ").strip().lower()
        
        if confirm == 'y':
            self.scraper.clear_all()
            print("✓ All data cleared")
        else:
            print("Cancelled")
    
    def _handle_help(self):
        """Handle help command"""
        print("Available commands:")
        print("  add      - Add a new ticker")
        print("  remove   - Remove a ticker")
        print("  show     - Show ticker data in beautiful ASCII tables")
        print("           - Option 1: Detailed view for specific ticker")
        print("           - Option 2: Summary view for all tickers")
        print("  refresh  - Refresh data for ticker(s)")
        print("  export   - Export data to file (with custom path option)")
        print("  stats    - Show scraper statistics")
        print("  deps     - Check dependency status")
        print("  clear    - Clear all data")
        print("  help     - Show this help")
        print("  quit     - Exit the program")
        print()
        print("Tips:")
        print("  - Use Ctrl+C to exit at any time")
        print("  - Ticker symbols are case-insensitive")
        print("  - Data is automatically saved between sessions")
    
    def _show_ticker_list(self):
        """Show current ticker list"""
        tickers = self.scraper.get_ticker_list()
        if not tickers:
            print("No tickers currently tracked")
        else:
            print(f"Currently tracking: {', '.join(tickers)}") 
"""
Data storage and persistence functionality
"""

import json
import os
import csv
import logging
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

from .data_models import FinancialData

logger = logging.getLogger(__name__)


class DataStorage:
    """Handles data persistence"""
    
    def __init__(self, storage_file: str = None):
        # Use user data directory to avoid permission issues
        if storage_file is None:
            storage_file = os.getenv('FINPULL_STORAGE_FILE')
            if not storage_file:
                # Try to use user data directory first
                try:
                    if os.name == 'nt':  # Windows
                        data_dir = Path(os.environ.get('APPDATA', Path.home()))
                    else:  # Unix/Linux/Mac
                        data_dir = Path.home() / '.local' / 'share'
                    
                    data_dir = data_dir / 'finpull'
                    data_dir.mkdir(parents=True, exist_ok=True)
                    storage_file = str(data_dir / 'financial_data.json')
                except Exception as e:
                    logger.warning(f"Could not create user data directory: {e}. Using current directory.")
                    storage_file = 'financial_data.json'
        
        self.storage_file = storage_file
        self.data_cache: Dict[str, FinancialData] = {}
        self.tickers_list: List[str] = []
        self.load_data()
    
    def load_data(self):
        """Load data from storage file"""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.tickers_list = data.get('tickers', [])
                    
                    # Convert dict data back to FinancialData objects
                    cache_data = data.get('cache', {})
                    for ticker, item_data in cache_data.items():
                        self.data_cache[ticker] = FinancialData.from_dict(item_data)
                        
                logger.info(f"Loaded {len(self.tickers_list)} tickers from {self.storage_file}")
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            # Initialize empty state on error
            self.data_cache = {}
            self.tickers_list = []
    
    def save_data(self):
        """Save data to storage file with proper error handling"""
        try:
            data = {
                'tickers': self.tickers_list,
                'cache': {ticker: data.to_dict() for ticker, data in self.data_cache.items()},
                'last_updated': datetime.now().isoformat(),
                'version': '1.0.6'
            }
            
            # Ensure directory exists
            storage_dir = Path(self.storage_file).parent
            try:
                storage_dir.mkdir(parents=True, exist_ok=True)
            except Exception as dir_error:
                logger.warning(f"Could not create storage directory: {dir_error}")
            
            # Create backup if file exists
            if os.path.exists(self.storage_file):
                backup_file = f"{self.storage_file}.backup"
                try:
                    import shutil
                    shutil.copy2(self.storage_file, backup_file)
                except Exception as backup_error:
                    logger.warning(f"Could not create backup: {backup_error}")
            
            # Write data atomically
            temp_file = f"{self.storage_file}.tmp"
            try:
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                # Replace original file
                os.replace(temp_file, self.storage_file)
                logger.debug(f"Saved data to {self.storage_file}")
                
            except PermissionError as pe:
                logger.error(f"Permission denied writing to {self.storage_file}: {pe}")
                # Try to fall back to current directory
                fallback_file = 'financial_data.json'
                if fallback_file != self.storage_file:
                    logger.info(f"Attempting to save to current directory: {fallback_file}")
                    try:
                        with open(fallback_file, 'w', encoding='utf-8') as f:
                            json.dump(data, f, indent=2, ensure_ascii=False)
                        self.storage_file = fallback_file
                        logger.info(f"Successfully saved to {fallback_file}")
                    except Exception as fallback_error:
                        logger.error(f"Fallback save also failed: {fallback_error}")
                        raise Exception(f"Cannot save data: Permission denied to {self.storage_file} and fallback failed: {fallback_error}")
                else:
                    raise Exception(f"Cannot save data: Permission denied to {self.storage_file}")
            
        except Exception as e:
            logger.error(f"Error saving data: {e}")
            # Clean up temp file if it exists
            temp_file = f"{self.storage_file}.tmp"
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
            # Re-raise the exception so calling code can handle it
            raise
    
    def add_ticker(self, ticker: str) -> bool:
        """Add ticker to the list if not already present"""
        ticker = ticker.upper().strip()
        if ticker and ticker not in self.tickers_list:
            self.tickers_list.append(ticker)
            try:
                self.save_data()
                logger.info(f"Added ticker {ticker}")
                return True
            except Exception as e:
                # Rollback the addition if save failed
                self.tickers_list.remove(ticker)
                logger.error(f"Failed to save after adding {ticker}: {e}")
                raise
        return False
    
    def add_multiple_tickers(self, tickers: List[str]) -> List[str]:
        """Add multiple tickers at once, returns list of successfully added tickers"""
        added_tickers = []
        original_list = self.tickers_list.copy()
        
        for ticker in tickers:
            ticker = ticker.upper().strip()
            if ticker and ticker not in self.tickers_list:
                self.tickers_list.append(ticker)
                added_tickers.append(ticker)
        
        if added_tickers:
            try:
                self.save_data()
                logger.info(f"Added tickers: {', '.join(added_tickers)}")
            except Exception as e:
                # Rollback all additions if save failed
                self.tickers_list = original_list
                logger.error(f"Failed to save after adding tickers: {e}")
                raise
        
        return added_tickers
    
    def remove_ticker(self, ticker: str):
        """Remove ticker from the list"""
        ticker = ticker.upper().strip()
        if ticker in self.tickers_list:
            # Store original state for rollback
            original_ticker_in_list = True
            original_cache_data = self.data_cache.get(ticker)
            
            self.tickers_list.remove(ticker)
            if ticker in self.data_cache:
                del self.data_cache[ticker]
            
            try:
                self.save_data()
                logger.info(f"Removed ticker {ticker}")
            except Exception as e:
                # Rollback the removal if save failed
                self.tickers_list.append(ticker)
                if original_cache_data:
                    self.data_cache[ticker] = original_cache_data
                logger.error(f"Failed to save after removing {ticker}: {e}")
                raise
    
    def clear_all(self):
        """Clear all tickers and cached data"""
        # Store original state for rollback
        original_tickers = self.tickers_list.copy()
        original_cache = self.data_cache.copy()
        
        self.tickers_list.clear()
        self.data_cache.clear()
        
        try:
            self.save_data()
            logger.info("Cleared all data")
        except Exception as e:
            # Rollback if save failed
            self.tickers_list = original_tickers
            self.data_cache = original_cache
            logger.error(f"Failed to save after clearing data: {e}")
            raise
    
    def update_cache(self, ticker: str, data: FinancialData):
        """Update cached data for a ticker"""
        ticker = ticker.upper().strip()
        # Store original state for rollback
        original_data = self.data_cache.get(ticker)
        
        self.data_cache[ticker] = data
        
        try:
            self.save_data()
            logger.debug(f"Updated cache for {ticker}")
        except Exception as e:
            # Rollback the cache update if save failed
            if original_data:
                self.data_cache[ticker] = original_data
            else:
                del self.data_cache[ticker]
            logger.error(f"Failed to save after updating cache for {ticker}: {e}")
            raise
    
    def get_cached_data(self, ticker: str) -> Optional[FinancialData]:
        """Get cached data for a ticker"""
        return self.data_cache.get(ticker.upper())
    
    def get_all_tickers(self) -> List[str]:
        """Get all ticker symbols"""
        return self.tickers_list.copy()
    
    def get_all_cached_data(self) -> Dict[str, FinancialData]:
        """Get all cached data"""
        return self.data_cache.copy()
    
    def export_to_json(self, filename: str = None) -> str:
        """Export data to JSON file"""
        if not filename:
            filename = f"financial_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_data = []
        for ticker in self.tickers_list:
            if ticker in self.data_cache:
                export_data.append(self.data_cache[ticker].to_dict())
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported {len(export_data)} records to {filename}")
            return filename
        except Exception as e:
            logger.error(f"Export to JSON failed: {e}")
            raise Exception(f"Failed to export to {filename}: {e}")
    
    def export_to_csv(self, filename: str = None) -> str:
        """Export data to CSV file"""
        if not filename:
            filename = f"financial_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        try:
            if not self.data_cache:
                # Create empty CSV file
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['ticker'])  # At least write header
                return filename
            
            # Get all field names from the first item
            first_item = next(iter(self.data_cache.values()))
            fieldnames = list(first_item.to_dict().keys())
            
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                count = 0
                for ticker in self.tickers_list:
                    if ticker in self.data_cache:
                        writer.writerow(self.data_cache[ticker].to_dict())
                        count += 1
            
            logger.info(f"Exported {count} records to {filename}")
            return filename
        except Exception as e:
            logger.error(f"Export to CSV failed: {e}")
            raise Exception(f"Failed to export to {filename}: {e}")
    
    def get_stats(self) -> Dict[str, any]:
        """Get storage statistics"""
        total_tickers = len(self.tickers_list)
        cached_tickers = len(self.data_cache)
        stale_count = sum(1 for data in self.data_cache.values() if data.is_stale())
        
        return {
            'total_tickers': total_tickers,
            'cached_tickers': cached_tickers,
            'missing_cache': total_tickers - cached_tickers,
            'stale_data': stale_count,
            'storage_file': self.storage_file,
            'file_exists': os.path.exists(self.storage_file),
            'file_size': os.path.getsize(self.storage_file) if os.path.exists(self.storage_file) else 0
        }
    
    def cleanup_stale_data(self, max_age_hours: int = 24):
        """Remove stale data from cache"""
        removed_count = 0
        tickers_to_remove = []
        
        for ticker, data in self.data_cache.items():
            if data.is_stale(max_age_hours * 60):  # Convert hours to minutes
                tickers_to_remove.append(ticker)
        
        if tickers_to_remove:
            # Store original state for rollback
            original_cache = {ticker: self.data_cache[ticker] for ticker in tickers_to_remove}
            
            for ticker in tickers_to_remove:
                del self.data_cache[ticker]
                removed_count += 1
            
            try:
                self.save_data()
                logger.info(f"Cleaned up {removed_count} stale records")
            except Exception as e:
                # Rollback if save failed
                for ticker, data in original_cache.items():
                    self.data_cache[ticker] = data
                logger.error(f"Failed to save after cleanup: {e}")
                raise
        
        return removed_count 
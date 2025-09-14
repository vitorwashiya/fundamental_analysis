"""
Service for integrating with fundamentus library and processing stock data
"""
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Set
from sqlalchemy.orm import Session
from loguru import logger
import fundamentus
import pandas as pd

from app.models.models import Sector, Stock, DataUpdateLog
from app.sectors import SectorAnalyzerFactory


class FundamentusService:
    """
    Service for integrating with fundamentus library
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.analyzer_factory = SectorAnalyzerFactory()
    
    def get_stocks_data(self) -> pd.DataFrame:
        """
        Get stocks data from fundamentus.get_resultado()
        
        Returns:
            pd.DataFrame: Stocks data with indicators
        """
        try:
            logger.info("Fetching stock data from fundamentus.get_resultado()")
            df = fundamentus.get_resultado()
            logger.info(f"Retrieved {len(df)} stocks from fundamentus")
            return df
        except Exception as e:
            logger.error(f"Error fetching data from fundamentus: {e}")
            raise
    
    def get_stock_details(self, symbols: List[str]) -> pd.DataFrame:
        """
        Get detailed stock information using fundamentus.get_papel()
        
        Args:
            symbols: List of stock symbols
            
        Returns:
            pd.DataFrame: Detailed stock information including sectors
        """
        try:
            logger.info(f"Fetching detailed data for {len(symbols)} stocks")
            df = fundamentus.get_papel(symbols)
            logger.info(f"Retrieved detailed data for {len(df)} stocks")
            return df
        except Exception as e:
            logger.error(f"Error fetching detailed stock data: {e}")
            raise
    
    def clean_stock_symbol(self, symbol: str) -> str:
        """
        Clean and normalize stock symbol
        
        Args:
            symbol: Raw stock symbol
            
        Returns:
            str: Cleaned symbol
        """
        # Remove any extra characters and convert to uppercase
        cleaned = re.sub(r'[^A-Z0-9]', '', symbol.upper())
        return cleaned
    
    def get_base_symbol(self, symbol: str) -> str:
        """
        Extract base symbol (first 4 characters) from stock symbol
        
        Args:
            symbol: Stock symbol (e.g., ITUB4, ITUB3)
            
        Returns:
            str: Base symbol (e.g., ITUB)
        """
        cleaned = self.clean_stock_symbol(symbol)
        return cleaned[:4] if len(cleaned) >= 4 else cleaned
    
    def remove_duplicate_stocks(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove duplicate stocks, keeping the one with highest number
        (e.g., keep ITUB4 over ITUB3)
        
        Args:
            df: DataFrame with stock data
            
        Returns:
            pd.DataFrame: DataFrame with duplicates removed
        """
        # Add base symbol column
        df['base_symbol'] = df.index.map(self.get_base_symbol)
        
        # Sort by symbol to ensure we get the highest number
        df_sorted = df.sort_index()
        
        # Keep last occurrence (highest number) for each base symbol
        df_deduplicated = df_sorted.groupby('base_symbol').last()
        
        # Reset index to get the original symbol back
        df_deduplicated = df_deduplicated.reset_index()
        df_deduplicated = df_deduplicated.set_index(df_sorted.index[df_deduplicated.index])
        
        # Drop the helper column
        df_deduplicated = df_deduplicated.drop('base_symbol', axis=1)
        
        logger.info(f"Removed duplicates: {len(df)} -> {len(df_deduplicated)} stocks")
        return df_deduplicated
    
    def extract_sectors_from_details(self, details_df: pd.DataFrame) -> Dict[str, Dict[str, str]]:
        """
        Extract sector and subsector information from detailed stock data
        
        Args:
            details_df: DataFrame from fundamentus.get_papel()
            
        Returns:
            Dict: Mapping of stock symbol to sector info
        """
        sectors_map = {}
        
        for symbol, row in details_df.iterrows():
            if pd.notna(row.get('Setor', None)) and pd.notna(row.get('Subsetor', None)):
                sectors_map[symbol] = {
                    'sector': row['Setor'],
                    'subsector': row['Subsetor']
                }
        
        logger.info(f"Extracted sector information for {len(sectors_map)} stocks")
        return sectors_map
    
    def create_or_update_sectors(self, sectors_map: Dict[str, Dict[str, str]]) -> Dict[str, int]:
        """
        Create or update sectors in the database
        
        Args:
            sectors_map: Mapping of stock symbols to sector info
            
        Returns:
            Dict: Mapping of sector names to sector IDs
        """
        # Get unique sectors
        unique_sectors = {}
        for symbol, sector_info in sectors_map.items():
            sector_name = sector_info['sector']
            subsector = sector_info['subsector']
            
            if sector_name not in unique_sectors:
                unique_sectors[sector_name] = set()
            unique_sectors[sector_name].add(subsector)
        
        # Get sector categories using the analyzer factory
        sector_ids = {}
        
        for sector_name, subsectors in unique_sectors.items():
            # Find the category for this sector
            category = None
            for subsector in subsectors:
                category = self.analyzer_factory.get_sector_category(subsector)
                if category:
                    break
            
            if not category:
                category = "Outros"  # Default category
            
            # Check if sector exists
            existing_sector = self.db.query(Sector).filter(Sector.name == sector_name).first()
            
            if existing_sector:
                # Update subsectors if needed
                existing_subsectors = set(existing_sector.subsectors.split(',')) if existing_sector.subsectors else set()
                all_subsectors = existing_subsectors.union(subsectors)
                existing_sector.subsectors = ','.join(sorted(all_subsectors))
                existing_sector.updated_at = datetime.utcnow()
                sector_ids[sector_name] = existing_sector.id
            else:
                # Create new sector
                new_sector = Sector(
                    name=sector_name,
                    category=category,
                    subsectors=','.join(sorted(subsectors))
                )
                self.db.add(new_sector)
                self.db.flush()  # Get the ID
                sector_ids[sector_name] = new_sector.id
        
        self.db.commit()
        logger.info(f"Created/updated {len(sector_ids)} sectors")
        return sector_ids
    
    def calculate_additional_indicators(self, stock_data: Dict) -> Dict:
        """
        Calculate additional indicators from existing data
        
        Args:
            stock_data: Dictionary with stock financial data
            
        Returns:
            Dict: Updated stock data with additional indicators
        """
        # Calculate Net Debt / EBITDA if both are available
        if (stock_data.get('divida_liquida') is not None and 
            stock_data.get('ebitda') is not None and 
            stock_data['ebitda'] != 0):
            stock_data['div_liq_ebitda'] = stock_data['divida_liquida'] / stock_data['ebitda']
        
        # Add other calculated metrics as needed
        # Examples:
        # - Free cash flow yield
        # - Debt to equity ratio improvements
        # - Asset quality metrics
        
        return stock_data
    
    def convert_stock_data(self, symbol: str, row: pd.Series, sector_id: int, subsector: str) -> Dict:
        """
        Convert pandas Series to dictionary with proper data types
        
        Args:
            symbol: Stock symbol
            row: Pandas Series with stock data
            sector_id: Sector ID from database
            subsector: Subsector name
            
        Returns:
            Dict: Converted stock data
        """
        def safe_float(value):
            """Safely convert value to float"""
            if pd.isna(value) or value in ['', '-', None]:
                return None
            try:
                return float(value)
            except (ValueError, TypeError):
                return None
        
        stock_data = {
            'symbol': symbol,
            'company_name': str(row.get('Empresa', row.get('nome', ''))),  # From get_papel or fallback
            'sector_id': sector_id,
            'subsector': subsector,
            
            # Financial indicators from fundamentus.get_resultado() - using correct column names
            'cotacao': safe_float(row.get('cotacao', row.get('Cotacao'))),
            'pl': safe_float(row.get('pl', row.get('PL'))),
            'pvp': safe_float(row.get('pvp', row.get('PVP'))),
            'psr': safe_float(row.get('psr', row.get('PSR'))),
            'div_yield': safe_float(row.get('dy', row.get('Div_Yield'))),  # 'dy' in get_resultado
            'p_ativo': safe_float(row.get('pa', row.get('PAtivos'))),  # 'pa' in get_resultado
            'p_cap_giro': safe_float(row.get('pcg', row.get('PCap_Giro'))),  # 'pcg' in get_resultado
            'p_ebit': safe_float(row.get('pebit', row.get('PEBIT'))),  # 'pebit' in get_resultado
            'p_ativ_circ_liq': safe_float(row.get('pacl', row.get('PAtiv_Circ_Liq'))),  # 'pacl' in get_resultado
            'ev_ebit': safe_float(row.get('evebit', row.get('EV_EBIT'))),  # 'evebit' in get_resultado
            'ev_ebitda': safe_float(row.get('evebitda', row.get('EV_EBITDA'))),  # 'evebitda' in get_resultado
            'mrg_ebit': safe_float(row.get('mrgebit', row.get('Marg_EBIT'))),  # 'mrgebit' in get_resultado
            'mrg_liq': safe_float(row.get('mrgliq', row.get('Marg_Liquida'))),  # 'mrgliq' in get_resultado
            'liq_corr': safe_float(row.get('liqc', row.get('Liquidez_Corr'))),  # 'liqc' in get_resultado
            'roic': safe_float(row.get('roic', row.get('ROIC'))),
            'roe': safe_float(row.get('roe', row.get('ROE'))),
            'liq_2meses': safe_float(row.get('liq2m', row.get('Vol_med_2m'))),  # 'liq2m' in get_resultado
            'patrim_liq': safe_float(row.get('patrliq', row.get('Patrim_Liq'))),  # 'patrliq' in get_resultado
            'div_br_patrim': safe_float(row.get('divbpatr', row.get('Div_Br_Patrim'))),  # 'divbpatr' in get_resultado
            'cresc_rec_5a': safe_float(row.get('c5y', row.get('Cres_Rec_5a'))),  # 'c5y' in get_resultado
            
            # Additional fields from fundamentus.get_papel() if available
            'receita_liquida': safe_float(row.get('Receita_Liquida_12m')),
            'ebit': safe_float(row.get('EBIT_12m')),
            'lucro_liquido': safe_float(row.get('Lucro_Liquido_12m')),
            'divida_liquida': safe_float(row.get('Div_Liquida')),
            'ativo_total': safe_float(row.get('Ativo')),
            'patrimonio_liquido': safe_float(row.get('Patrim_Liq')),
            
            'is_active': True,
            'last_updated': datetime.utcnow()
        }
        
        # Calculate additional indicators
        stock_data = self.calculate_additional_indicators(stock_data)
        
        return stock_data
    
    def create_or_update_stock(self, stock_data: Dict) -> Stock:
        """
        Create or update stock in the database
        
        Args:
            stock_data: Dictionary with stock data
            
        Returns:
            Stock: Created or updated stock instance
        """
        existing_stock = self.db.query(Stock).filter(Stock.symbol == stock_data['symbol']).first()
        
        if existing_stock:
            # Update existing stock
            for key, value in stock_data.items():
                if hasattr(existing_stock, key):
                    setattr(existing_stock, key, value)
            existing_stock.updated_at = datetime.utcnow()
            return existing_stock
        else:
            # Create new stock
            new_stock = Stock(**stock_data)
            self.db.add(new_stock)
            return new_stock
    
    def log_update_start(self, update_type: str) -> DataUpdateLog:
        """
        Log the start of a data update process
        
        Args:
            update_type: Type of update ('full', 'incremental', 'rankings')
            
        Returns:
            DataUpdateLog: Created log entry
        """
        log_entry = DataUpdateLog(
            update_type=update_type,
            status='started',
            start_time=datetime.utcnow()
        )
        self.db.add(log_entry)
        self.db.commit()
        return log_entry
    
    def log_update_end(self, log_entry: DataUpdateLog, status: str, 
                       stocks_processed: int = 0, sectors_processed: int = 0, 
                       error_message: str = None):
        """
        Log the end of a data update process
        
        Args:
            log_entry: The log entry to update
            status: Final status ('completed', 'failed')
            stocks_processed: Number of stocks processed
            sectors_processed: Number of sectors processed
            error_message: Error message if failed
        """
        log_entry.status = status
        log_entry.end_time = datetime.utcnow()
        log_entry.stocks_processed = stocks_processed
        log_entry.sectors_processed = sectors_processed
        log_entry.error_message = error_message
        
        if log_entry.start_time and log_entry.end_time:
            duration = log_entry.end_time - log_entry.start_time
            log_entry.duration_seconds = duration.total_seconds()
        
        self.db.commit()
    
    def full_data_update(self) -> Tuple[int, int]:
        """
        Perform a full data update from fundamentus
        
        Returns:
            Tuple[int, int]: Number of stocks and sectors processed
        """
        log_entry = self.log_update_start('full')
        
        try:
            # Get basic stock data
            stocks_df = self.get_stocks_data()
            
            # Remove duplicates
            stocks_df = self.remove_duplicate_stocks(stocks_df)
            
            # Get detailed information for sector mapping
            symbols = list(stocks_df.index)
            details_df = self.get_stock_details(symbols)
            
            # Extract sector information
            sectors_map = self.extract_sectors_from_details(details_df)
            
            # Create/update sectors
            sector_ids = self.create_or_update_sectors(sectors_map)
            
            # Process each stock
            stocks_processed = 0
            
            for symbol, row in stocks_df.iterrows():
                try:
                    # Get sector information
                    sector_info = sectors_map.get(symbol)
                    if not sector_info:
                        logger.warning(f"No sector information for {symbol}, skipping")
                        continue
                    
                    sector_name = sector_info['sector']
                    subsector = sector_info['subsector']
                    sector_id = sector_ids.get(sector_name)
                    
                    if not sector_id:
                        logger.warning(f"No sector ID for {sector_name}, skipping {symbol}")
                        continue
                    
                    # Merge with detailed data if available
                    if symbol in details_df.index:
                        detailed_row = details_df.loc[symbol]
                        # Combine data, giving priority to detailed data
                        combined_row = row.copy()
                        for col in detailed_row.index:
                            if pd.notna(detailed_row[col]):
                                combined_row[col] = detailed_row[col]
                        row = combined_row
                    
                    # Convert to stock data
                    stock_data = self.convert_stock_data(symbol, row, sector_id, subsector)
                    
                    # Create or update stock
                    self.create_or_update_stock(stock_data)
                    stocks_processed += 1
                    
                    if stocks_processed % 50 == 0:
                        logger.info(f"Processed {stocks_processed} stocks")
                        self.db.commit()  # Commit periodically
                
                except Exception as e:
                    logger.error(f"Error processing stock {symbol}: {e}")
                    continue
            
            # Final commit
            self.db.commit()
            
            self.log_update_end(log_entry, 'completed', stocks_processed, len(sector_ids))
            logger.info(f"Full update completed: {stocks_processed} stocks, {len(sector_ids)} sectors")
            
            return stocks_processed, len(sector_ids)
        
        except Exception as e:
            logger.error(f"Full update failed: {e}")
            self.log_update_end(log_entry, 'failed', error_message=str(e))
            raise

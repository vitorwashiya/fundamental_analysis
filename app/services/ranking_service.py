"""
Service for calculating rankings and scores using sector-specific analyzers
"""
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_
from loguru import logger
import pandas as pd

from app.models.models import Sector, Stock, SectorRanking
from app.sectors import SectorAnalyzerFactory


class RankingService:
    """
    Service for calculating sector-specific rankings and scores
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.analyzer_factory = SectorAnalyzerFactory()
    
    def get_stocks_by_sector(self, sector_id: int) -> List[Stock]:
        """
        Get all active stocks for a specific sector
        
        Args:
            sector_id: Sector ID
            
        Returns:
            List[Stock]: List of stocks in the sector
        """
        return self.db.query(Stock).filter(
            and_(Stock.sector_id == sector_id, Stock.is_active == True)
        ).all()
    
    def stock_to_dict(self, stock: Stock) -> Dict:
        """
        Convert Stock model to dictionary for analysis
        
        Args:
            stock: Stock model instance
            
        Returns:
            Dict: Stock data as dictionary
        """
        return {
            'symbol': stock.symbol,
            'company_name': stock.company_name,
            'cotacao': stock.cotacao,
            'pl': stock.pl,
            'pvp': stock.pvp,
            'psr': stock.psr,
            'div_yield': stock.div_yield,
            'p_ativo': stock.p_ativo,
            'p_cap_giro': stock.p_cap_giro,
            'p_ebit': stock.p_ebit,
            'p_ativ_circ_liq': stock.p_ativ_circ_liq,
            'ev_ebit': stock.ev_ebit,
            'ev_ebitda': stock.ev_ebitda,
            'mrg_ebit': stock.mrg_ebit,
            'mrg_liq': stock.mrg_liq,
            'liq_corr': stock.liq_corr,
            'roic': stock.roic,
            'roe': stock.roe,
            'liq_2meses': stock.liq_2meses,
            'patrim_liq': stock.patrim_liq,
            'div_br_patrim': stock.div_br_patrim,
            'cresc_rec_5a': stock.cresc_rec_5a,
            'receita_liquida': stock.receita_liquida,
            'ebit': stock.ebit,
            'ebitda': stock.ebitda,
            'lucro_liquido': stock.lucro_liquido,
            'divida_liquida': stock.divida_liquida,
            'ativo_total': stock.ativo_total,
            'patrimonio_liquido': stock.patrimonio_liquido,
            'div_liq_ebitda': stock.div_liq_ebitda
        }
    
    def calculate_sector_rankings(self, sector_id: int) -> List[Dict]:
        """
        Calculate rankings for all stocks in a specific sector
        
        Args:
            sector_id: Sector ID
            
        Returns:
            List[Dict]: List of ranked stocks with scores
        """
        # Get sector information
        sector = self.db.query(Sector).filter(Sector.id == sector_id).first()
        if not sector:
            raise ValueError(f"Sector with ID {sector_id} not found")
        
        # Get stocks in this sector
        stocks = self.get_stocks_by_sector(sector_id)
        if not stocks:
            logger.warning(f"No stocks found for sector {sector.name}")
            return []
        
        # Convert stocks to DataFrame for analysis
        stock_data = []
        stock_objects = {}
        
        for stock in stocks:
            stock_dict = self.stock_to_dict(stock)
            stock_data.append(stock_dict)
            stock_objects[stock.symbol] = stock
        
        stocks_df = pd.DataFrame(stock_data)
        stocks_df.set_index('symbol', inplace=True)
        
        # Get appropriate analyzer for this sector
        analyzer = self.analyzer_factory.get_analyzer(sector.category, sector.name)
        
        # Calculate rankings
        ranked_df = analyzer.rank_stocks(stocks_df)
        
        # Convert results back to list of dictionaries
        results = []
        for _, row in ranked_df.iterrows():
            stock_symbol = row.name if hasattr(row, 'name') else row['symbol']
            stock_obj = stock_objects.get(stock_symbol)
            
            if stock_obj:
                result = {
                    'stock_id': stock_obj.id,
                    'stock_symbol': stock_symbol,
                    'sector_id': sector_id,
                    'rank_position': int(row['rank_position']),
                    'earnings_yield_score': float(row.get('earnings_yield_score', 0)),
                    'return_on_capital_score': float(row.get('return_on_capital_score', 0)),
                    'value_score': float(row.get('value_score', 0)),
                    'quality_score': float(row.get('quality_score', 0)),
                    'growth_score': float(row.get('growth_score', 0)),
                    'dividend_score': float(row.get('dividend_score', 0)),
                    'final_score': float(row['final_score'])
                }
                results.append(result)
        
        logger.info(f"Calculated rankings for {len(results)} stocks in sector {sector.name}")
        return results
    
    def update_sector_rankings(self, sector_id: int) -> int:
        """
        Update rankings for a specific sector in the database
        
        Args:
            sector_id: Sector ID
            
        Returns:
            int: Number of rankings updated
        """
        try:
            # Calculate new rankings
            rankings_data = self.calculate_sector_rankings(sector_id)
            
            if not rankings_data:
                return 0
            
            # Delete existing rankings for this sector
            self.db.query(SectorRanking).filter(SectorRanking.sector_id == sector_id).delete()
            
            # Insert new rankings
            for ranking_data in rankings_data:
                ranking = SectorRanking(**ranking_data)
                self.db.add(ranking)
            
            # Update stock sector ranks
            for ranking_data in rankings_data:
                stock = self.db.query(Stock).filter(Stock.id == ranking_data['stock_id']).first()
                if stock:
                    stock.sector_rank = ranking_data['rank_position']
            
            self.db.commit()
            logger.info(f"Updated {len(rankings_data)} rankings for sector {sector_id}")
            return len(rankings_data)
        
        except Exception as e:
            logger.error(f"Error updating rankings for sector {sector_id}: {e}")
            self.db.rollback()
            raise
    
    def update_all_sector_rankings(self) -> Dict[str, int]:
        """
        Update rankings for all sectors
        
        Returns:
            Dict[str, int]: Summary of updates by sector
        """
        # Get all sectors
        sectors = self.db.query(Sector).all()
        
        results = {}
        total_rankings = 0
        
        for sector in sectors:
            try:
                count = self.update_sector_rankings(sector.id)
                results[sector.name] = count
                total_rankings += count
                logger.info(f"Updated {count} rankings for sector {sector.name}")
            except Exception as e:
                logger.error(f"Failed to update rankings for sector {sector.name}: {e}")
                results[sector.name] = 0
        
        logger.info(f"Total rankings updated: {total_rankings} across {len(sectors)} sectors")
        return results
    
    def calculate_magic_formula_rankings(self) -> int:
        """
        Calculate Magic Formula rankings across all stocks
        (Based on "The Little Book That Beats the Market")
        
        Returns:
            int: Number of stocks ranked
        """
        try:
            # Get all active stocks with required data
            stocks = self.db.query(Stock).filter(
                and_(
                    Stock.is_active == True,
                    Stock.ev_ebit.isnot(None),
                    Stock.roic.isnot(None),
                    Stock.ev_ebit > 0
                )
            ).all()
            
            if not stocks:
                logger.warning("No stocks with sufficient data for Magic Formula ranking")
                return 0
            
            # Create DataFrame for ranking
            stock_data = []
            for stock in stocks:
                # Calculate earnings yield (EBIT/EV)
                earnings_yield = 1 / stock.ev_ebit if stock.ev_ebit > 0 else 0
                
                stock_data.append({
                    'id': stock.id,
                    'symbol': stock.symbol,
                    'earnings_yield': earnings_yield,
                    'roic': stock.roic or 0
                })
            
            df = pd.DataFrame(stock_data)
            
            # Rank by earnings yield (higher is better)
            df['earnings_yield_rank'] = df['earnings_yield'].rank(ascending=False)
            
            # Rank by ROIC (higher is better) 
            df['roic_rank'] = df['roic'].rank(ascending=False)
            
            # Combined rank (lower is better)
            df['combined_rank'] = df['earnings_yield_rank'] + df['roic_rank']
            df['magic_formula_rank'] = df['combined_rank'].rank()
            
            # Update stocks with Magic Formula rankings
            for _, row in df.iterrows():
                stock = self.db.query(Stock).filter(Stock.id == row['id']).first()
                if stock:
                    stock.magic_formula_rank = int(row['magic_formula_rank'])
            
            self.db.commit()
            logger.info(f"Updated Magic Formula rankings for {len(stocks)} stocks")
            return len(stocks)
        
        except Exception as e:
            logger.error(f"Error calculating Magic Formula rankings: {e}")
            self.db.rollback()
            raise
    
    def get_top_stocks_by_sector(self, sector_id: int, limit: int = 10) -> List[SectorRanking]:
        """
        Get top N stocks for a specific sector
        
        Args:
            sector_id: Sector ID
            limit: Number of top stocks to return
            
        Returns:
            List[SectorRanking]: Top ranked stocks
        """
        return self.db.query(SectorRanking).filter(
            SectorRanking.sector_id == sector_id
        ).order_by(SectorRanking.rank_position).limit(limit).all()
    
    def get_top_stocks_all_sectors(self, limit_per_sector: int = 5) -> Dict[str, List[SectorRanking]]:
        """
        Get top N stocks for each sector
        
        Args:
            limit_per_sector: Number of top stocks per sector
            
        Returns:
            Dict: Mapping of sector names to top stocks
        """
        sectors = self.db.query(Sector).all()
        results = {}
        
        for sector in sectors:
            top_stocks = self.get_top_stocks_by_sector(sector.id, limit_per_sector)
            if top_stocks:
                results[sector.name] = top_stocks
        
        return results
    
    def get_top_magic_formula_stocks(self, limit: int = 20) -> List[Stock]:
        """
        Get top stocks by Magic Formula ranking
        
        Args:
            limit: Number of top stocks to return
            
        Returns:
            List[Stock]: Top Magic Formula stocks
        """
        return self.db.query(Stock).filter(
            and_(
                Stock.is_active == True,
                Stock.magic_formula_rank.isnot(None)
            )
        ).order_by(Stock.magic_formula_rank).limit(limit).all()

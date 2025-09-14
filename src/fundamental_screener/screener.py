"""
Main fundamental analysis screener for Brazilian stocks.
"""
from typing import List, Dict, Optional
import logging

from .models import StockData, Sector, ScreeningCriteria, AnalysisResult
from .data_provider import DataProvider, FundamentusProvider, MockDataProvider
from .sector_screeners import (
    SectorScreener, BankScreener, CommodityScreener, 
    TechnologyScreener, IndustrialScreener
)


logger = logging.getLogger(__name__)


class FundamentalScreener:
    """Main screener class for Brazilian stock fundamental analysis."""
    
    def __init__(self, data_provider: Optional[DataProvider] = None, use_mock_data: bool = False):
        """
        Initialize the screener.
        
        Args:
            data_provider: Optional data provider. If None, will try FundamentusProvider first.
            use_mock_data: If True, uses mock data for demonstration.
        """
        if data_provider:
            self.data_provider = data_provider
        elif use_mock_data:
            self.data_provider = MockDataProvider()
        else:
            try:
                self.data_provider = FundamentusProvider()
            except Exception as e:
                logger.warning(f"Failed to initialize FundamentusProvider: {e}")
                logger.info("Falling back to MockDataProvider")
                self.data_provider = MockDataProvider()
        
        self.sector_screeners = self._initialize_sector_screeners()
    
    def _initialize_sector_screeners(self) -> Dict[Sector, SectorScreener]:
        """Initialize sector-specific screeners."""
        screeners = {}
        
        # Financial sector
        screeners[Sector.FINANCEIROS] = BankScreener(self.data_provider)
        
        # Commodity sectors
        screeners[Sector.MINERACAO] = CommodityScreener(self.data_provider, Sector.MINERACAO)
        screeners[Sector.PETROLEO_GAS] = CommodityScreener(self.data_provider, Sector.PETROLEO_GAS)
        
        # Technology sector
        screeners[Sector.SOFTWARE_DADOS] = TechnologyScreener(self.data_provider)
        
        # Industrial sectors
        screeners[Sector.MACHINES_EQUIPMENTS] = IndustrialScreener(self.data_provider, Sector.MACHINES_EQUIPMENTS)
        screeners[Sector.SIDERURGIA_METALURGIA] = IndustrialScreener(self.data_provider, Sector.SIDERURGIA_METALURGIA)
        screeners[Sector.QUIMICOS] = IndustrialScreener(self.data_provider, Sector.QUIMICOS)
        screeners[Sector.PAPEL_CELULOSE] = IndustrialScreener(self.data_provider, Sector.PAPEL_CELULOSE)
        screeners[Sector.CONSTRUCAO] = IndustrialScreener(self.data_provider, Sector.CONSTRUCAO)
        screeners[Sector.VEICULOS_PECAS] = IndustrialScreener(self.data_provider, Sector.VEICULOS_PECAS)
        
        return screeners
    
    def screen_all_sectors(self, additional_criteria: Optional[ScreeningCriteria] = None) -> Dict[Sector, List[AnalysisResult]]:
        """
        Screen stocks across all sectors.
        
        Args:
            additional_criteria: Additional screening criteria to apply.
            
        Returns:
            Dictionary mapping sectors to their screening results.
        """
        results = {}
        
        for sector, screener in self.sector_screeners.items():
            try:
                sector_results = screener.screen_stocks(additional_criteria)
                if sector_results:
                    results[sector] = sector_results
                    logger.info(f"Found {len(sector_results)} opportunities in {sector.value}")
            except Exception as e:
                logger.error(f"Error screening {sector.value}: {e}")
        
        return results
    
    def screen_sector(self, sector: Sector, additional_criteria: Optional[ScreeningCriteria] = None) -> List[AnalysisResult]:
        """
        Screen stocks in a specific sector.
        
        Args:
            sector: The sector to screen.
            additional_criteria: Additional screening criteria to apply.
            
        Returns:
            List of analysis results for the sector.
        """
        if sector not in self.sector_screeners:
            logger.warning(f"No specialized screener for {sector.value}, using general criteria")
            return self._screen_sector_general(sector, additional_criteria)
        
        screener = self.sector_screeners[sector]
        return screener.screen_stocks(additional_criteria)
    
    def _screen_sector_general(self, sector: Sector, criteria: Optional[ScreeningCriteria] = None) -> List[AnalysisResult]:
        """Screen sector using general criteria when no specialized screener exists."""
        if not criteria:
            criteria = ScreeningCriteria(
                pl_min=5.0,
                pl_max=20.0,
                roe_min=0.10,
                mrgliq_min=0.05,
                divida_liquida_ebitda_max=4.0
            )
        
        stocks = self.data_provider.get_sector_stocks(sector)
        results = []
        
        for stock in stocks:
            if self._meets_general_criteria(stock, criteria):
                score = self._calculate_general_score(stock)
                reasons = self._get_general_reasons(stock, criteria)
                warnings = self._get_general_warnings(stock)
                
                results.append(AnalysisResult(
                    stock=stock,
                    score=score,
                    reasons=reasons,
                    warnings=warnings
                ))
        
        results.sort(key=lambda x: x.score, reverse=True)
        return results
    
    def _meets_general_criteria(self, stock: StockData, criteria: ScreeningCriteria) -> bool:
        """Check if stock meets general criteria."""
        if criteria.pl_min and (not stock.pl or stock.pl < criteria.pl_min):
            return False
        if criteria.pl_max and (not stock.pl or stock.pl > criteria.pl_max):
            return False
        if criteria.roe_min and (not stock.roe or stock.roe < criteria.roe_min):
            return False
        if criteria.mrgliq_min and (not stock.mrgliq or stock.mrgliq < criteria.mrgliq_min):
            return False
        if criteria.divida_liquida_ebitda_max and (not stock.divida_liquida_ebitda or 
                                                   stock.divida_liquida_ebitda > criteria.divida_liquida_ebitda_max):
            return False
        return True
    
    def _calculate_general_score(self, stock: StockData) -> float:
        """Calculate general score for stocks without specialized screener."""
        score = 0.0
        
        # P/L score
        if stock.pl and 5 <= stock.pl <= 15:
            score += 20
        
        # ROE score
        if stock.roe and stock.roe >= 0.15:
            score += 25
        elif stock.roe and stock.roe >= 0.10:
            score += 15
        
        # Net margin score
        if stock.mrgliq and stock.mrgliq >= 0.10:
            score += 20
        elif stock.mrgliq and stock.mrgliq >= 0.05:
            score += 10
        
        # Debt score
        if stock.divida_liquida_ebitda and stock.divida_liquida_ebitda <= 2.0:
            score += 15
        elif stock.divida_liquida_ebitda and stock.divida_liquida_ebitda <= 3.0:
            score += 10
        
        # Dividend yield score
        if stock.dy and stock.dy >= 0.05:
            score += 20
        elif stock.dy and stock.dy >= 0.03:
            score += 10
        
        return score
    
    def _get_general_reasons(self, stock: StockData, criteria: ScreeningCriteria) -> List[str]:
        """Get general analysis reasons."""
        reasons = []
        
        if stock.pl and stock.pl <= 15:
            reasons.append(f"Reasonable P/L: {stock.pl:.1f}")
        
        if stock.roe and stock.roe >= 0.15:
            reasons.append(f"Strong ROE: {stock.roe*100:.1f}%")
        
        if stock.mrgliq and stock.mrgliq >= 0.10:
            reasons.append(f"Good profitability: {stock.mrgliq*100:.1f}% net margin")
        
        if stock.dy and stock.dy >= 0.05:
            reasons.append(f"Attractive dividend: {stock.dy*100:.1f}%")
        
        return reasons
    
    def _get_general_warnings(self, stock: StockData) -> List[str]:
        """Get general warnings."""
        warnings = []
        
        if stock.pl and stock.pl > 25:
            warnings.append("High P/L - potential overvaluation")
        
        if stock.mrgliq and stock.mrgliq < 0:
            warnings.append("Negative margins - company losing money")
        
        if stock.divida_liquida_ebitda and stock.divida_liquida_ebitda > 4:
            warnings.append("High debt levels")
        
        return warnings
    
    def get_top_opportunities(self, max_results: int = 10, sectors: Optional[List[Sector]] = None, 
                              additional_criteria: Optional[ScreeningCriteria] = None) -> List[AnalysisResult]:
        """
        Get top investment opportunities across sectors.
        
        Args:
            max_results: Maximum number of results to return.
            sectors: Optional list of sectors to focus on.
            additional_criteria: Additional screening criteria to apply.
            
        Returns:
            List of top analysis results sorted by score.
        """
        all_results = []
        
        target_sectors = sectors if sectors else list(self.sector_screeners.keys())
        
        for sector in target_sectors:
            sector_results = self.screen_sector(sector, additional_criteria)
            all_results.extend(sector_results)
        
        # Sort all results by score and return top ones
        all_results.sort(key=lambda x: x.score, reverse=True)
        return all_results[:max_results]
    
    def analyze_specific_stock(self, symbol: str) -> Optional[AnalysisResult]:
        """
        Analyze a specific stock symbol.
        
        Args:
            symbol: Stock symbol to analyze.
            
        Returns:
            Analysis result for the stock, or None if not found.
        """
        stocks = self.data_provider.get_stock_data(symbol)
        if not stocks:
            return None
        
        stock = stocks[0]
        
        # Use sector-specific screener if available
        if stock.sector in self.sector_screeners:
            screener = self.sector_screeners[stock.sector]
            score = screener.calculate_sector_score(stock)
            criteria = screener.get_sector_criteria()
            reasons = screener._get_analysis_reasons(stock, criteria)
            warnings = screener._get_warnings(stock)
        else:
            # Use general analysis
            score = self._calculate_general_score(stock)
            reasons = self._get_general_reasons(stock, ScreeningCriteria())
            warnings = self._get_general_warnings(stock)
        
        return AnalysisResult(
            stock=stock,
            score=score,
            reasons=reasons,
            warnings=warnings
        )
"""
Sector-specific fundamental analysis screeners for Brazilian stocks.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
import logging

from .models import StockData, Sector, ScreeningCriteria, AnalysisResult
from .data_provider import DataProvider


logger = logging.getLogger(__name__)


class SectorScreener(ABC):
    """Abstract base class for sector-specific screeners."""
    
    def __init__(self, data_provider: DataProvider):
        self.data_provider = data_provider
    
    @abstractmethod
    def get_sector(self) -> Sector:
        """Return the sector this screener handles."""
        pass
    
    @abstractmethod
    def get_sector_criteria(self) -> ScreeningCriteria:
        """Return sector-specific screening criteria."""
        pass
    
    @abstractmethod
    def calculate_sector_score(self, stock: StockData) -> float:
        """Calculate sector-specific score for the stock."""
        pass
    
    def screen_stocks(self, additional_criteria: ScreeningCriteria = None) -> List[AnalysisResult]:
        """Screen stocks in this sector."""
        # Get sector stocks
        stocks = self.data_provider.get_sector_stocks(self.get_sector())
        
        # Get criteria
        criteria = self.get_sector_criteria()
        if additional_criteria:
            criteria = self._merge_criteria(criteria, additional_criteria)
        
        results = []
        for stock in stocks:
            if self._meets_criteria(stock, criteria):
                score = self.calculate_sector_score(stock)
                reasons = self._get_analysis_reasons(stock, criteria)
                warnings = self._get_warnings(stock)
                
                results.append(AnalysisResult(
                    stock=stock,
                    score=score,
                    reasons=reasons,
                    warnings=warnings
                ))
        
        # Sort by score (highest first)
        results.sort(key=lambda x: x.score, reverse=True)
        return results
    
    def _merge_criteria(self, base: ScreeningCriteria, additional: ScreeningCriteria) -> ScreeningCriteria:
        """Merge additional criteria with sector-specific criteria, using most restrictive values."""
        merged = ScreeningCriteria()
        
        # For each criterion, use the most restrictive value
        
        # P/L min: use higher value (more restrictive)
        merged.pl_min = max(filter(None, [base.pl_min, additional.pl_min]), default=None)
        
        # P/L max: use lower value (more restrictive)
        merged.pl_max = min(filter(None, [base.pl_max, additional.pl_max]), default=None)
        
        # ROE min: use higher value (more restrictive)
        merged.roe_min = max(filter(None, [base.roe_min, additional.roe_min]), default=None)
        
        # Margin minimums: use higher values (more restrictive)
        merged.mrgliq_min = max(filter(None, [base.mrgliq_min, additional.mrgliq_min]), default=None)
        merged.mrgebitda_min = max(filter(None, [base.mrgebitda_min, additional.mrgebitda_min]), default=None)
        
        # EV/EBITDA min: use higher value (more restrictive)
        merged.evebitda_min = max(filter(None, [base.evebitda_min, additional.evebitda_min]), default=None)
        
        # EV/EBITDA max: use lower value (more restrictive)
        merged.evebitda_max = min(filter(None, [base.evebitda_max, additional.evebitda_max]), default=None)
        
        # Debt/EBITDA max: use lower value (more restrictive)
        merged.divida_liquida_ebitda_max = min(filter(None, [base.divida_liquida_ebitda_max, 
                                                             additional.divida_liquida_ebitda_max]), default=None)
        
        # Dividend yield min: use higher value (more restrictive)
        merged.dy_min = max(filter(None, [base.dy_min, additional.dy_min]), default=None)
        
        # Market cap min: use higher value (more restrictive)
        merged.market_cap_min = max(filter(None, [base.market_cap_min, additional.market_cap_min]), default=None)
        
        # Sectors: combine both if specified
        if base.sectors and additional.sectors:
            merged.sectors = list(set(base.sectors + additional.sectors))
        elif additional.sectors:
            merged.sectors = additional.sectors
        elif base.sectors:
            merged.sectors = base.sectors
        
        return merged
    
    def _meets_criteria(self, stock: StockData, criteria: ScreeningCriteria) -> bool:
        """Check if stock meets screening criteria."""
        if criteria.pl_min and (not stock.pl or stock.pl < criteria.pl_min):
            return False
        if criteria.pl_max and (not stock.pl or stock.pl > criteria.pl_max):
            return False
        if criteria.mrgliq_min and (not stock.mrgliq or stock.mrgliq < criteria.mrgliq_min):
            return False
        if criteria.mrgebitda_min and (not stock.mrgebitda or stock.mrgebitda < criteria.mrgebitda_min):
            return False
        if criteria.evebitda_min and (not stock.evebitda or stock.evebitda < criteria.evebitda_min):
            return False
        if criteria.evebitda_max and (not stock.evebitda or stock.evebitda > criteria.evebitda_max):
            return False
        if criteria.divida_liquida_ebitda_max and (not stock.divida_liquida_ebitda or 
                                                   stock.divida_liquida_ebitda > criteria.divida_liquida_ebitda_max):
            return False
        if criteria.roe_min and (not stock.roe or stock.roe < criteria.roe_min):
            return False
        if criteria.dy_min and (not stock.dy or stock.dy < criteria.dy_min):
            return False
        
        return True
    
    def _get_analysis_reasons(self, stock: StockData, criteria: ScreeningCriteria) -> List[str]:
        """Get reasons why stock is recommended."""
        reasons = []
        
        if stock.pl and criteria.pl_max and stock.pl <= criteria.pl_max:
            reasons.append(f"Attractive P/L ratio: {stock.pl:.1f}")
        
        if stock.mrgliq and criteria.mrgliq_min and stock.mrgliq >= criteria.mrgliq_min:
            reasons.append(f"Good net margin: {stock.mrgliq*100:.1f}%")
        
        if stock.evebitda and criteria.evebitda_max and stock.evebitda <= criteria.evebitda_max:
            reasons.append(f"Reasonable EV/EBITDA: {stock.evebitda:.1f}")
        
        if stock.roe and criteria.roe_min and stock.roe >= criteria.roe_min:
            reasons.append(f"Strong ROE: {stock.roe*100:.1f}%")
        
        if stock.dy and criteria.dy_min and stock.dy >= criteria.dy_min:
            reasons.append(f"Good dividend yield: {stock.dy*100:.1f}%")
        
        if stock.divida_liquida_ebitda and criteria.divida_liquida_ebitda_max and \
           stock.divida_liquida_ebitda <= criteria.divida_liquida_ebitda_max:
            reasons.append(f"Low debt/EBITDA: {stock.divida_liquida_ebitda:.1f}")
        
        return reasons
    
    def _get_warnings(self, stock: StockData) -> List[str]:
        """Get warnings about the stock."""
        warnings = []
        
        if stock.pl and stock.pl > 25:
            warnings.append("High P/L ratio - stock might be overvalued")
        
        if stock.mrgliq and stock.mrgliq < 0:
            warnings.append("Negative net margin - company is losing money")
        
        if stock.divida_liquida_ebitda and stock.divida_liquida_ebitda > 4:
            warnings.append("High debt levels relative to EBITDA")
        
        if stock.roe and stock.roe < 0:
            warnings.append("Negative ROE - poor return on equity")
        
        return warnings


class BankScreener(SectorScreener):
    """Screener for banking/financial sector stocks."""
    
    def get_sector(self) -> Sector:
        return Sector.FINANCEIROS
    
    def get_sector_criteria(self) -> ScreeningCriteria:
        """Banking sector criteria - typically lower P/E, good ROE, reasonable margins."""
        return ScreeningCriteria(
            pl_min=3.0,
            pl_max=12.0,
            roe_min=0.12,  # 12% ROE minimum
            dy_min=0.04,   # 4% dividend yield minimum
            divida_liquida_ebitda_max=3.0,  # Banks have different debt structure
        )
    
    def calculate_sector_score(self, stock: StockData) -> float:
        """Calculate score for banking stocks."""
        score = 0.0
        
        # P/L score (lower is better for banks)
        if stock.pl:
            if stock.pl <= 8:
                score += 25
            elif stock.pl <= 12:
                score += 15
            else:
                score += 5
        
        # ROE score (higher is better)
        if stock.roe:
            if stock.roe >= 0.20:
                score += 30
            elif stock.roe >= 0.15:
                score += 20
            elif stock.roe >= 0.12:
                score += 10
        
        # Dividend yield score
        if stock.dy:
            if stock.dy >= 0.08:
                score += 25
            elif stock.dy >= 0.06:
                score += 15
            elif stock.dy >= 0.04:
                score += 10
        
        # Net margin score
        if stock.mrgliq:
            if stock.mrgliq >= 0.20:
                score += 20
            elif stock.mrgliq >= 0.15:
                score += 15
            elif stock.mrgliq >= 0.10:
                score += 10
        
        return score


class CommodityScreener(SectorScreener):
    """Screener for commodity-related stocks (mining, oil & gas)."""
    
    def __init__(self, data_provider: DataProvider, sector: Sector):
        super().__init__(data_provider)
        self._sector = sector
    
    def get_sector(self) -> Sector:
        return self._sector
    
    def get_sector_criteria(self) -> ScreeningCriteria:
        """Commodity sector criteria - cyclical nature requires different approach."""
        return ScreeningCriteria(
            pl_min=2.0,
            pl_max=15.0,
            evebitda_max=8.0,
            mrgebitda_min=0.15,  # 15% EBITDA margin minimum
            divida_liquida_ebitda_max=3.0,
            dy_min=0.05,  # 5% dividend yield minimum
        )
    
    def calculate_sector_score(self, stock: StockData) -> float:
        """Calculate score for commodity stocks."""
        score = 0.0
        
        # EV/EBITDA score (lower is better)
        if stock.evebitda:
            if stock.evebitda <= 4:
                score += 30
            elif stock.evebitda <= 6:
                score += 20
            elif stock.evebitda <= 8:
                score += 10
        
        # EBITDA margin score
        if stock.mrgebitda:
            if stock.mrgebitda >= 0.40:
                score += 25
            elif stock.mrgebitda >= 0.25:
                score += 15
            elif stock.mrgebitda >= 0.15:
                score += 10
        
        # Debt/EBITDA score (lower is better)
        if stock.divida_liquida_ebitda:
            if stock.divida_liquida_ebitda <= 1.5:
                score += 25
            elif stock.divida_liquida_ebitda <= 2.5:
                score += 15
            elif stock.divida_liquida_ebitda <= 3.0:
                score += 10
        
        # Dividend yield score
        if stock.dy:
            if stock.dy >= 0.10:
                score += 20
            elif stock.dy >= 0.07:
                score += 15
            elif stock.dy >= 0.05:
                score += 10
        
        return score


class TechnologyScreener(SectorScreener):
    """Screener for technology/software stocks."""
    
    def get_sector(self) -> Sector:
        return Sector.SOFTWARE_DADOS
    
    def get_sector_criteria(self) -> ScreeningCriteria:
        """Technology sector criteria - growth-focused."""
        return ScreeningCriteria(
            pl_max=30.0,  # Higher P/E acceptable for tech
            mrgliq_min=0.10,  # 10% net margin minimum
            roe_min=0.15,  # 15% ROE minimum
            divida_liquida_ebitda_max=2.0,  # Low debt preferred
        )
    
    def calculate_sector_score(self, stock: StockData) -> float:
        """Calculate score for technology stocks."""
        score = 0.0
        
        # Growth-adjusted P/E (simplified)
        if stock.pl:
            if stock.pl <= 15:
                score += 20
            elif stock.pl <= 25:
                score += 15
            elif stock.pl <= 30:
                score += 10
        
        # ROE score (very important for tech)
        if stock.roe:
            if stock.roe >= 0.25:
                score += 30
            elif stock.roe >= 0.20:
                score += 25
            elif stock.roe >= 0.15:
                score += 15
        
        # Net margin score
        if stock.mrgliq:
            if stock.mrgliq >= 0.20:
                score += 25
            elif stock.mrgliq >= 0.15:
                score += 20
            elif stock.mrgliq >= 0.10:
                score += 15
        
        # Low debt score
        if stock.divida_liquida_ebitda:
            if stock.divida_liquida_ebitda <= 1.0:
                score += 25
            elif stock.divida_liquida_ebitda <= 2.0:
                score += 15
        
        return score


class IndustrialScreener(SectorScreener):
    """Screener for industrial stocks."""
    
    def __init__(self, data_provider: DataProvider, sector: Sector):
        super().__init__(data_provider)
        self._sector = sector
    
    def get_sector(self) -> Sector:
        return self._sector
    
    def get_sector_criteria(self) -> ScreeningCriteria:
        """Industrial sector criteria - balanced approach."""
        return ScreeningCriteria(
            pl_min=5.0,
            pl_max=20.0,
            evebitda_max=12.0,
            mrgliq_min=0.08,  # 8% net margin minimum
            roe_min=0.12,  # 12% ROE minimum
            divida_liquida_ebitda_max=3.5,
        )
    
    def calculate_sector_score(self, stock: StockData) -> float:
        """Calculate score for industrial stocks."""
        score = 0.0
        
        # P/L score
        if stock.pl:
            if stock.pl <= 12:
                score += 20
            elif stock.pl <= 16:
                score += 15
            elif stock.pl <= 20:
                score += 10
        
        # ROE score
        if stock.roe:
            if stock.roe >= 0.20:
                score += 25
            elif stock.roe >= 0.15:
                score += 20
            elif stock.roe >= 0.12:
                score += 15
        
        # EV/EBITDA score
        if stock.evebitda:
            if stock.evebitda <= 8:
                score += 20
            elif stock.evebitda <= 10:
                score += 15
            elif stock.evebitda <= 12:
                score += 10
        
        # Net margin score
        if stock.mrgliq:
            if stock.mrgliq >= 0.15:
                score += 20
            elif stock.mrgliq >= 0.12:
                score += 15
            elif stock.mrgliq >= 0.08:
                score += 10
        
        # Debt management score
        if stock.divida_liquida_ebitda:
            if stock.divida_liquida_ebitda <= 2.0:
                score += 15
            elif stock.divida_liquida_ebitda <= 3.0:
                score += 10
            elif stock.divida_liquida_ebitda <= 3.5:
                score += 5
        
        return score
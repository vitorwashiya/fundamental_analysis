"""
Utilities sector analyzer - Energy, Water, Gas
"""
from typing import Dict, List
from app.sectors.base_sector import BaseSectorAnalyzer, SectorWeights


class UtilitiesSectorAnalyzer(BaseSectorAnalyzer):
    """
    Analyzer for utilities sector companies
    Focus on stability, dividend yield, and regulated returns
    """
    
    def __init__(self, sector_name: str = "Utilities"):
        super().__init__(sector_name, "Utilities")
    
    def get_sector_weights(self) -> SectorWeights:
        """
        Utilities sector weights - focus on dividends and stability
        """
        return SectorWeights(
            earnings_yield=0.20,     # Steady cash flows
            return_on_capital=0.15,  # Regulated returns
            value_metrics=0.25,      # Traditional value metrics
            quality_metrics=0.15,    # Financial stability
            growth_metrics=0.05,     # Low growth expectations
            dividend_metrics=0.20    # High dividend focus
        )
    
    def get_excluded_metrics(self) -> List[str]:
        """
        Utilities use most standard metrics
        """
        return []
    
    def calculate_custom_metrics(self, stock_data: Dict) -> Dict[str, float]:
        """
        Calculate utilities-specific metrics
        """
        custom_scores = {}
        
        # Dividend sustainability score
        if ('div_yield' in stock_data and stock_data['div_yield'] is not None and
            'div_br_patrim' in stock_data and stock_data['div_br_patrim'] is not None):
            
            div_yield = stock_data['div_yield']
            debt_to_equity = stock_data['div_br_patrim']
            
            # Utilities can handle higher debt levels
            if div_yield > 5 and debt_to_equity < 2:  # Good dividend with manageable debt
                custom_scores['utility_dividend_sustainability'] = 100
            elif div_yield > 3:
                custom_scores['utility_dividend_sustainability'] = 70
            else:
                custom_scores['utility_dividend_sustainability'] = max(0, div_yield * 20)
        
        # Debt management score for utilities
        if 'div_br_patrim' in stock_data and stock_data['div_br_patrim'] is not None:
            debt_ratio = stock_data['div_br_patrim']
            if debt_ratio < 1.5:  # Conservative debt
                custom_scores['utility_debt_score'] = 100
            elif debt_ratio < 2.5:  # Acceptable for utilities
                custom_scores['utility_debt_score'] = 80
            else:
                custom_scores['utility_debt_score'] = max(0, 100 - (debt_ratio - 2.5) * 20)
        
        return custom_scores


class EnergyElectricSectorAnalyzer(UtilitiesSectorAnalyzer):
    """
    Specific analyzer for electric energy companies
    """
    
    def __init__(self, sector_name: str = "Energia Elétrica"):
        super().__init__(sector_name)
    
    def calculate_custom_metrics(self, stock_data: Dict) -> Dict[str, float]:
        """
        Electric utilities specific metrics
        """
        custom_scores = super().calculate_custom_metrics(stock_data)
        
        # Capacity utilization proxy using margins
        if 'mrg_ebit' in stock_data and stock_data['mrg_ebit'] is not None:
            ebit_margin = stock_data['mrg_ebit']
            if ebit_margin >= 20:  # High efficiency
                custom_scores['energy_efficiency_score'] = 100
            elif ebit_margin >= 15:
                custom_scores['energy_efficiency_score'] = 80
            elif ebit_margin >= 10:
                custom_scores['energy_efficiency_score'] = 60
            else:
                custom_scores['energy_efficiency_score'] = max(0, ebit_margin * 5)
        
        return custom_scores


class WaterSanitationAnalyzer(UtilitiesSectorAnalyzer):
    """
    Specific analyzer for water and sanitation companies
    """
    
    def __init__(self, sector_name: str = "Água e Saneamento"):
        super().__init__(sector_name)
    
    def get_sector_weights(self) -> SectorWeights:
        """
        Water sector weights - focus on growth due to expansion opportunities
        """
        return SectorWeights(
            earnings_yield=0.20,
            return_on_capital=0.20,
            value_metrics=0.20,
            quality_metrics=0.15,
            growth_metrics=0.15,     # Higher growth potential
            dividend_metrics=0.10
        )
    
    def calculate_custom_metrics(self, stock_data: Dict) -> Dict[str, float]:
        """
        Water/sanitation specific metrics
        """
        custom_scores = super().calculate_custom_metrics(stock_data)
        
        # Growth opportunity score
        if 'cresc_rec_5a' in stock_data and stock_data['cresc_rec_5a'] is not None:
            growth = stock_data['cresc_rec_5a']
            if growth >= 10:  # High growth for utilities
                custom_scores['water_growth_score'] = 100
            elif growth >= 5:
                custom_scores['water_growth_score'] = 80
            else:
                custom_scores['water_growth_score'] = max(0, growth * 10)
        
        return custom_scores


class GasSectorAnalyzer(UtilitiesSectorAnalyzer):
    """
    Specific analyzer for gas distribution companies
    """
    
    def __init__(self, sector_name: str = "Gás"):
        super().__init__(sector_name)
    
    def calculate_custom_metrics(self, stock_data: Dict) -> Dict[str, float]:
        """
        Gas distribution specific metrics
        """
        custom_scores = super().calculate_custom_metrics(stock_data)
        
        # Volume efficiency (using asset turnover proxy)
        if ('receita_liquida' in stock_data and stock_data['receita_liquida'] is not None and
            'ativo_total' in stock_data and stock_data['ativo_total'] is not None):
            
            if stock_data['ativo_total'] > 0:
                asset_turnover = stock_data['receita_liquida'] / stock_data['ativo_total']
                custom_scores['gas_efficiency_score'] = min(100, asset_turnover * 200)
        
        return custom_scores

"""
Financial sector analyzer - Banks, Insurance, Financial Services
"""
from typing import Dict, List
from app.sectors.base_sector import BaseSectorAnalyzer, SectorWeights


class FinancialSectorAnalyzer(BaseSectorAnalyzer):
    """
    Analyzer for financial sector companies
    Banks, insurance companies, and financial services have different metrics
    """
    
    def __init__(self, sector_name: str = "Financeiro"):
        super().__init__(sector_name, "Financeiro")
    
    def get_sector_weights(self) -> SectorWeights:
        """
        Financial sector weights - focus on ROE, book value, and efficiency
        """
        return SectorWeights(
            earnings_yield=0.15,     # Less important for banks
            return_on_capital=0.30,  # ROE is crucial for banks
            value_metrics=0.25,      # P/B ratio is key
            quality_metrics=0.20,    # Asset quality and efficiency
            growth_metrics=0.05,     # Growth less important than stability
            dividend_metrics=0.05    # Moderate dividend focus
        )
    
    def get_excluded_metrics(self) -> List[str]:
        """
        Banks don't use EV/EBITDA, focus on different metrics
        """
        return ['earnings_yield']  # EV/EBIT not meaningful for banks
    
    def calculate_custom_metrics(self, stock_data: Dict) -> Dict[str, float]:
        """
        Calculate bank-specific metrics
        """
        custom_scores = {}
        
        # Price to Book is critical for banks
        if 'pvp' in stock_data and stock_data['pvp'] is not None:
            pvp = stock_data['pvp']
            if 0.5 <= pvp <= 1.5:
                custom_scores['bank_pb_score'] = 100
            elif pvp < 0.5:
                custom_scores['bank_pb_score'] = pvp * 200  # Scale 0-0.5 to 0-100
            else:
                custom_scores['bank_pb_score'] = max(0, 100 - (pvp - 1.5) * 50)
        
        # ROE efficiency for banks
        if 'roe' in stock_data and stock_data['roe'] is not None:
            roe = stock_data['roe']
            if roe >= 15:  # Strong ROE for banks
                custom_scores['bank_roe_score'] = 100
            elif roe >= 10:
                custom_scores['bank_roe_score'] = 50 + (roe - 10) * 10
            else:
                custom_scores['bank_roe_score'] = max(0, roe * 5)
        
        return custom_scores
    
    def calculate_earnings_yield_score(self, stock_data: Dict) -> float:
        """
        For banks, use a different approach - focus on earnings efficiency
        """
        # Use P/E ratio instead of EV/EBIT for banks
        if 'pl' in stock_data and stock_data['pl'] is not None and stock_data['pl'] > 0:
            pe = stock_data['pl']
            if 5 <= pe <= 15:  # Ideal P/E range for banks
                return 100
            elif pe < 5:
                return 80  # Too low might indicate problems
            else:
                return max(0, 100 - (pe - 15) * 5)
        return 0.0


class InsuranceSectorAnalyzer(BaseSectorAnalyzer):
    """
    Analyzer for insurance companies
    """
    
    def __init__(self, sector_name: str = "Previdência e Seguros"):
        super().__init__(sector_name, "Financeiro")
    
    def get_sector_weights(self) -> SectorWeights:
        """
        Insurance sector weights
        """
        return SectorWeights(
            earnings_yield=0.10,
            return_on_capital=0.25,
            value_metrics=0.30,
            quality_metrics=0.20,
            growth_metrics=0.10,
            dividend_metrics=0.05
        )
    
    def get_excluded_metrics(self) -> List[str]:
        """
        Insurance companies also don't use traditional EV/EBITDA
        """
        return ['earnings_yield']
    
    def calculate_custom_metrics(self, stock_data: Dict) -> Dict[str, float]:
        """
        Calculate insurance-specific metrics
        """
        custom_scores = {}
        
        # Combined ratio proxy using margins
        if 'mrg_liq' in stock_data and stock_data['mrg_liq'] is not None:
            margin = stock_data['mrg_liq']
            # Insurance companies should have consistent margins
            if margin >= 10:
                custom_scores['insurance_efficiency_score'] = 100
            elif margin >= 5:
                custom_scores['insurance_efficiency_score'] = 50 + (margin - 5) * 10
            else:
                custom_scores['insurance_efficiency_score'] = max(0, margin * 10)
        
        return custom_scores


class HoldingsSectorAnalyzer(BaseSectorAnalyzer):
    """
    Analyzer for holding companies
    """
    
    def __init__(self, sector_name: str = "Holdings Diversificadas"):
        super().__init__(sector_name, "Financeiro")
    
    def get_sector_weights(self) -> SectorWeights:
        """
        Holdings sector weights - focus on asset value and dividend yield
        """
        return SectorWeights(
            earnings_yield=0.15,
            return_on_capital=0.20,
            value_metrics=0.35,  # Asset value is key
            quality_metrics=0.15,
            growth_metrics=0.05,
            dividend_metrics=0.10  # Holdings often pay good dividends
        )
    
    def get_excluded_metrics(self) -> List[str]:
        """
        Holdings may have different operational metrics
        """
        return []
    
    def calculate_custom_metrics(self, stock_data: Dict) -> Dict[str, float]:
        """
        Calculate holding-specific metrics
        """
        custom_scores = {}
        
        # Asset efficiency
        if 'p_ativo' in stock_data and stock_data['p_ativo'] is not None:
            p_ativo = stock_data['p_ativo']
            if p_ativo < 1:  # Trading below book value
                custom_scores['holding_discount_score'] = 100
            else:
                custom_scores['holding_discount_score'] = max(0, 100 - (p_ativo - 1) * 50)
        
        return custom_scores

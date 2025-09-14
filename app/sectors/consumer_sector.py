"""
Consumer sectors analyzer - Cyclical and Non-Cyclical
"""
from typing import Dict, List
from app.sectors.base_sector import BaseSectorAnalyzer, SectorWeights


class ConsumerCyclicalAnalyzer(BaseSectorAnalyzer):
    """
    Analyzer for consumer cyclical sector
    Retail, construction, automotive, etc.
    """
    
    def __init__(self, sector_name: str = "Consumo Cíclico"):
        super().__init__(sector_name, "Consumo Cíclico")
    
    def get_sector_weights(self) -> SectorWeights:
        """
        Consumer cyclical weights - focus on growth and efficiency
        """
        return SectorWeights(
            earnings_yield=0.25,     # Cash flow generation important
            return_on_capital=0.20,  # Capital efficiency
            value_metrics=0.20,      # Traditional valuation
            quality_metrics=0.20,    # Operational efficiency
            growth_metrics=0.15,     # Growth important but volatile
            dividend_metrics=0.00    # Usually low dividend yield
        )
    
    def get_excluded_metrics(self) -> List[str]:
        """
        Consumer cyclical uses most metrics
        """
        return []
    
    def calculate_custom_metrics(self, stock_data: Dict) -> Dict[str, float]:
        """
        Calculate consumer cyclical specific metrics
        """
        custom_scores = {}
        
        # Asset turnover efficiency
        if ('receita_liquida' in stock_data and stock_data['receita_liquida'] is not None and
            'ativo_total' in stock_data and stock_data['ativo_total'] is not None):
            
            if stock_data['ativo_total'] > 0:
                asset_turnover = stock_data['receita_liquida'] / stock_data['ativo_total']
                # Higher turnover is better for retail/cyclical
                custom_scores['asset_efficiency_score'] = min(100, asset_turnover * 50)
        
        # Working capital management
        if 'p_cap_giro' in stock_data and stock_data['p_cap_giro'] is not None:
            p_working_capital = stock_data['p_cap_giro']
            if p_working_capital < 10:  # Efficient working capital use
                custom_scores['working_capital_score'] = 100
            elif p_working_capital < 20:
                custom_scores['working_capital_score'] = 80
            else:
                custom_scores['working_capital_score'] = max(0, 100 - (p_working_capital - 20) * 2)
        
        return custom_scores


class RetailSectorAnalyzer(ConsumerCyclicalAnalyzer):
    """
    Specific analyzer for retail companies
    """
    
    def __init__(self, sector_name: str = "Comércio"):
        super().__init__(sector_name)
    
    def get_sector_weights(self) -> SectorWeights:
        """
        Retail specific weights - focus on efficiency and margins
        """
        return SectorWeights(
            earnings_yield=0.20,
            return_on_capital=0.25,  # High capital efficiency needed
            value_metrics=0.20,
            quality_metrics=0.25,    # Margins are crucial
            growth_metrics=0.10,
            dividend_metrics=0.00
        )
    
    def calculate_custom_metrics(self, stock_data: Dict) -> Dict[str, float]:
        """
        Retail specific metrics
        """
        custom_scores = super().calculate_custom_metrics(stock_data)
        
        # Inventory turnover proxy using margins
        if 'mrg_liq' in stock_data and stock_data['mrg_liq'] is not None:
            net_margin = stock_data['mrg_liq']
            # Retail margins are typically low but should be consistent
            if net_margin >= 5:
                custom_scores['retail_margin_score'] = 100
            elif net_margin >= 2:
                custom_scores['retail_margin_score'] = 70
            elif net_margin >= 0:
                custom_scores['retail_margin_score'] = 40
            else:
                custom_scores['retail_margin_score'] = 0
        
        return custom_scores


class ConstructionAnalyzer(ConsumerCyclicalAnalyzer):
    """
    Specific analyzer for construction companies
    """
    
    def __init__(self, sector_name: str = "Construção Civil"):
        super().__init__(sector_name)
    
    def get_sector_weights(self) -> SectorWeights:
        """
        Construction weights - focus on working capital and margins
        """
        return SectorWeights(
            earnings_yield=0.30,     # Cash flow very important
            return_on_capital=0.25,
            value_metrics=0.15,
            quality_metrics=0.20,
            growth_metrics=0.10,
            dividend_metrics=0.00
        )
    
    def calculate_custom_metrics(self, stock_data: Dict) -> Dict[str, float]:
        """
        Construction specific metrics
        """
        custom_scores = super().calculate_custom_metrics(stock_data)
        
        # Project efficiency (using EBIT margin as proxy)
        if 'mrg_ebit' in stock_data and stock_data['mrg_ebit'] is not None:
            ebit_margin = stock_data['mrg_ebit']
            if ebit_margin >= 15:
                custom_scores['construction_efficiency_score'] = 100
            elif ebit_margin >= 10:
                custom_scores['construction_efficiency_score'] = 80
            elif ebit_margin >= 5:
                custom_scores['construction_efficiency_score'] = 60
            else:
                custom_scores['construction_efficiency_score'] = max(0, ebit_margin * 10)
        
        return custom_scores


class ConsumerNonCyclicalAnalyzer(BaseSectorAnalyzer):
    """
    Analyzer for consumer non-cyclical sector
    Food, beverages, personal care, etc.
    """
    
    def __init__(self, sector_name: str = "Consumo Não Cíclico"):
        super().__init__(sector_name, "Consumo Não Cíclico")
    
    def get_sector_weights(self) -> SectorWeights:
        """
        Consumer non-cyclical weights - focus on stability and quality
        """
        return SectorWeights(
            earnings_yield=0.20,
            return_on_capital=0.25,  # Consistent returns important
            value_metrics=0.20,
            quality_metrics=0.25,    # Brand strength and margins
            growth_metrics=0.05,     # Stable growth
            dividend_metrics=0.05    # Some dividend income
        )
    
    def get_excluded_metrics(self) -> List[str]:
        """
        Consumer non-cyclical uses most metrics
        """
        return []
    
    def calculate_custom_metrics(self, stock_data: Dict) -> Dict[str, float]:
        """
        Calculate consumer non-cyclical specific metrics
        """
        custom_scores = {}
        
        # Brand premium (high margins indicate strong brands)
        if 'mrg_liq' in stock_data and stock_data['mrg_liq'] is not None:
            net_margin = stock_data['mrg_liq']
            if net_margin >= 15:  # Strong brand premium
                custom_scores['brand_strength_score'] = 100
            elif net_margin >= 10:
                custom_scores['brand_strength_score'] = 80
            elif net_margin >= 5:
                custom_scores['brand_strength_score'] = 60
            else:
                custom_scores['brand_strength_score'] = max(0, net_margin * 10)
        
        # Market stability (consistent ROIC)
        if 'roic' in stock_data and stock_data['roic'] is not None:
            roic = stock_data['roic']
            if roic >= 20:  # Very strong returns
                custom_scores['market_stability_score'] = 100
            elif roic >= 15:
                custom_scores['market_stability_score'] = 90
            elif roic >= 10:
                custom_scores['market_stability_score'] = 70
            else:
                custom_scores['market_stability_score'] = max(0, roic * 5)
        
        return custom_scores


class FoodBeverageAnalyzer(ConsumerNonCyclicalAnalyzer):
    """
    Specific analyzer for food and beverage companies
    """
    
    def __init__(self, sector_name: str = "Alimentos e Bebidas"):
        super().__init__(sector_name)
    
    def get_sector_weights(self) -> SectorWeights:
        """
        Food/beverage weights - premium on quality and dividends
        """
        return SectorWeights(
            earnings_yield=0.15,
            return_on_capital=0.30,
            value_metrics=0.20,
            quality_metrics=0.25,
            growth_metrics=0.05,
            dividend_metrics=0.05
        )
    
    def calculate_custom_metrics(self, stock_data: Dict) -> Dict[str, float]:
        """
        Food/beverage specific metrics
        """
        custom_scores = super().calculate_custom_metrics(stock_data)
        
        # Distribution efficiency
        if ('receita_liquida' in stock_data and stock_data['receita_liquida'] is not None and
            'ativo_total' in stock_data and stock_data['ativo_total'] is not None):
            
            if stock_data['ativo_total'] > 0:
                asset_turnover = stock_data['receita_liquida'] / stock_data['ativo_total']
                custom_scores['distribution_efficiency'] = min(100, asset_turnover * 100)
        
        return custom_scores

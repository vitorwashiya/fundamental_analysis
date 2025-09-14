"""
Materials and Industrial sectors analyzer
"""
from typing import Dict, List
from app.sectors.base_sector import BaseSectorAnalyzer, SectorWeights


class MaterialsBasicAnalyzer(BaseSectorAnalyzer):
    """
    Analyzer for basic materials sector
    Mining, steel, chemicals, etc.
    """
    
    def __init__(self, sector_name: str = "Materiais Básicos"):
        super().__init__(sector_name, "Materiais Básicos")
    
    def get_sector_weights(self) -> SectorWeights:
        """
        Materials sector weights - focus on earnings yield and efficiency
        """
        return SectorWeights(
            earnings_yield=0.30,     # Cyclical cash flows important
            return_on_capital=0.25,  # Capital intensive
            value_metrics=0.20,      # Often trade at low multiples
            quality_metrics=0.20,    # Operational efficiency
            growth_metrics=0.05,     # Cyclical growth
            dividend_metrics=0.00    # Usually low dividend yield
        )
    
    def get_excluded_metrics(self) -> List[str]:
        """
        Materials uses most metrics
        """
        return []
    
    def calculate_custom_metrics(self, stock_data: Dict) -> Dict[str, float]:
        """
        Calculate materials specific metrics
        """
        custom_scores = {}
        
        # Commodity cycle efficiency (using EV/EBITDA)
        if 'ev_ebitda' in stock_data and stock_data['ev_ebitda'] is not None:
            ev_ebitda = stock_data['ev_ebitda']
            if 0 < ev_ebitda <= 5:  # Very cheap
                custom_scores['commodity_value_score'] = 100
            elif ev_ebitda <= 8:
                custom_scores['commodity_value_score'] = 80
            elif ev_ebitda <= 12:
                custom_scores['commodity_value_score'] = 60
            else:
                custom_scores['commodity_value_score'] = max(0, 100 - (ev_ebitda - 12) * 5)
        
        # Asset intensity management
        if ('ativo_total' in stock_data and stock_data['ativo_total'] is not None and
            'receita_liquida' in stock_data and stock_data['receita_liquida'] is not None):
            
            if stock_data['ativo_total'] > 0:
                asset_turnover = stock_data['receita_liquida'] / stock_data['ativo_total']
                # Materials companies typically have low asset turnover
                custom_scores['asset_utilization_score'] = min(100, asset_turnover * 200)
        
        return custom_scores


class MiningAnalyzer(MaterialsBasicAnalyzer):
    """
    Specific analyzer for mining companies
    """
    
    def __init__(self, sector_name: str = "Mineração"):
        super().__init__(sector_name)
    
    def get_sector_weights(self) -> SectorWeights:
        """
        Mining weights - focus on cash generation and low valuation
        """
        return SectorWeights(
            earnings_yield=0.35,     # Cash flow critical for mining
            return_on_capital=0.20,
            value_metrics=0.25,
            quality_metrics=0.15,
            growth_metrics=0.05,
            dividend_metrics=0.00
        )
    
    def calculate_custom_metrics(self, stock_data: Dict) -> Dict[str, float]:
        """
        Mining specific metrics
        """
        custom_scores = super().calculate_custom_metrics(stock_data)
        
        # Resource efficiency (using EBIT margin)
        if 'mrg_ebit' in stock_data and stock_data['mrg_ebit'] is not None:
            ebit_margin = stock_data['mrg_ebit']
            if ebit_margin >= 30:  # High efficiency mining
                custom_scores['mining_efficiency_score'] = 100
            elif ebit_margin >= 20:
                custom_scores['mining_efficiency_score'] = 80
            elif ebit_margin >= 10:
                custom_scores['mining_efficiency_score'] = 60
            else:
                custom_scores['mining_efficiency_score'] = max(0, ebit_margin * 5)
        
        return custom_scores


class SteelMetallurgyAnalyzer(MaterialsBasicAnalyzer):
    """
    Specific analyzer for steel and metallurgy companies
    """
    
    def __init__(self, sector_name: str = "Siderurgia e Metalurgia"):
        super().__init__(sector_name)
    
    def calculate_custom_metrics(self, stock_data: Dict) -> Dict[str, float]:
        """
        Steel/metallurgy specific metrics
        """
        custom_scores = super().calculate_custom_metrics(stock_data)
        
        # Capacity utilization proxy
        if 'mrg_ebit' in stock_data and stock_data['mrg_ebit'] is not None:
            ebit_margin = stock_data['mrg_ebit']
            # Steel margins are typically cyclical
            if ebit_margin >= 15:
                custom_scores['steel_cycle_score'] = 100
            elif ebit_margin >= 8:
                custom_scores['steel_cycle_score'] = 70
            elif ebit_margin >= 0:
                custom_scores['steel_cycle_score'] = 40
            else:
                custom_scores['steel_cycle_score'] = 0
        
        return custom_scores


class IndustrialGoodsAnalyzer(BaseSectorAnalyzer):
    """
    Analyzer for industrial goods sector
    Machinery, equipment, transportation, etc.
    """
    
    def __init__(self, sector_name: str = "Bens Industriais"):
        super().__init__(sector_name, "Bens Industriais")
    
    def get_sector_weights(self) -> SectorWeights:
        """
        Industrial goods weights - balanced approach
        """
        return SectorWeights(
            earnings_yield=0.25,
            return_on_capital=0.25,
            value_metrics=0.20,
            quality_metrics=0.20,
            growth_metrics=0.10,
            dividend_metrics=0.00
        )
    
    def get_excluded_metrics(self) -> List[str]:
        """
        Industrial goods uses most metrics
        """
        return []
    
    def calculate_custom_metrics(self, stock_data: Dict) -> Dict[str, float]:
        """
        Calculate industrial goods specific metrics
        """
        custom_scores = {}
        
        # Operating leverage (using EBIT margin)
        if 'mrg_ebit' in stock_data and stock_data['mrg_ebit'] is not None:
            ebit_margin = stock_data['mrg_ebit']
            if ebit_margin >= 15:
                custom_scores['operating_leverage_score'] = 100
            elif ebit_margin >= 10:
                custom_scores['operating_leverage_score'] = 80
            elif ebit_margin >= 5:
                custom_scores['operating_leverage_score'] = 60
            else:
                custom_scores['operating_leverage_score'] = max(0, ebit_margin * 10)
        
        # Capital efficiency
        if 'roic' in stock_data and stock_data['roic'] is not None:
            roic = stock_data['roic']
            if roic >= 15:
                custom_scores['capital_efficiency_score'] = 100
            elif roic >= 10:
                custom_scores['capital_efficiency_score'] = 80
            elif roic >= 5:
                custom_scores['capital_efficiency_score'] = 60
            else:
                custom_scores['capital_efficiency_score'] = max(0, roic * 10)
        
        return custom_scores


class MachineryEquipmentAnalyzer(IndustrialGoodsAnalyzer):
    """
    Specific analyzer for machinery and equipment companies
    """
    
    def __init__(self, sector_name: str = "Máquinas e Equipamentos"):
        super().__init__(sector_name)
    
    def get_sector_weights(self) -> SectorWeights:
        """
        Machinery weights - focus on ROIC and quality
        """
        return SectorWeights(
            earnings_yield=0.20,
            return_on_capital=0.30,  # High ROIC important
            value_metrics=0.20,
            quality_metrics=0.25,    # Quality of equipment matters
            growth_metrics=0.05,
            dividend_metrics=0.00
        )
    
    def calculate_custom_metrics(self, stock_data: Dict) -> Dict[str, float]:
        """
        Machinery specific metrics
        """
        custom_scores = super().calculate_custom_metrics(stock_data)
        
        # Innovation proxy (using margins)
        if 'mrg_liq' in stock_data and stock_data['mrg_liq'] is not None:
            net_margin = stock_data['mrg_liq']
            if net_margin >= 10:  # High-tech, innovative products
                custom_scores['innovation_score'] = 100
            elif net_margin >= 6:
                custom_scores['innovation_score'] = 80
            elif net_margin >= 3:
                custom_scores['innovation_score'] = 60
            else:
                custom_scores['innovation_score'] = max(0, net_margin * 20)
        
        return custom_scores


class TransportationAnalyzer(IndustrialGoodsAnalyzer):
    """
    Specific analyzer for transportation companies
    """
    
    def __init__(self, sector_name: str = "Transporte"):
        super().__init__(sector_name)
    
    def get_sector_weights(self) -> SectorWeights:
        """
        Transportation weights - focus on asset utilization
        """
        return SectorWeights(
            earnings_yield=0.30,     # Cash flow important
            return_on_capital=0.25,
            value_metrics=0.20,
            quality_metrics=0.20,
            growth_metrics=0.05,
            dividend_metrics=0.00
        )
    
    def calculate_custom_metrics(self, stock_data: Dict) -> Dict[str, float]:
        """
        Transportation specific metrics
        """
        custom_scores = super().calculate_custom_metrics(stock_data)
        
        # Fleet utilization (using asset turnover)
        if ('receita_liquida' in stock_data and stock_data['receita_liquida'] is not None and
            'ativo_total' in stock_data and stock_data['ativo_total'] is not None):
            
            if stock_data['ativo_total'] > 0:
                asset_turnover = stock_data['receita_liquida'] / stock_data['ativo_total']
                custom_scores['fleet_utilization_score'] = min(100, asset_turnover * 150)
        
        return custom_scores

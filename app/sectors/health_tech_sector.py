"""
Health and Technology sectors analyzer
"""
from typing import Dict, List
from app.sectors.base_sector import BaseSectorAnalyzer, SectorWeights


class HealthSectorAnalyzer(BaseSectorAnalyzer):
    """
    Analyzer for health sector
    Healthcare services, pharmaceuticals, medical devices
    """
    
    def __init__(self, sector_name: str = "Saúde"):
        super().__init__(sector_name, "Saúde")
    
    def get_sector_weights(self) -> SectorWeights:
        """
        Health sector weights - focus on quality and growth
        """
        return SectorWeights(
            earnings_yield=0.20,
            return_on_capital=0.25,
            value_metrics=0.20,
            quality_metrics=0.25,    # Quality of service important
            growth_metrics=0.10,     # Demographic growth
            dividend_metrics=0.00
        )
    
    def get_excluded_metrics(self) -> List[str]:
        """
        Health uses most metrics
        """
        return []
    
    def calculate_custom_metrics(self, stock_data: Dict) -> Dict[str, float]:
        """
        Calculate health sector specific metrics
        """
        custom_scores = {}
        
        # Service quality proxy (using margins)
        if 'mrg_liq' in stock_data and stock_data['mrg_liq'] is not None:
            net_margin = stock_data['mrg_liq']
            if net_margin >= 15:  # High quality healthcare services
                custom_scores['service_quality_score'] = 100
            elif net_margin >= 10:
                custom_scores['service_quality_score'] = 85
            elif net_margin >= 5:
                custom_scores['service_quality_score'] = 70
            else:
                custom_scores['service_quality_score'] = max(0, net_margin * 12)
        
        # Demographic tailwind (growth potential)
        if 'cresc_rec_5a' in stock_data and stock_data['cresc_rec_5a'] is not None:
            growth = stock_data['cresc_rec_5a']
            if growth >= 15:  # Strong growth in health sector
                custom_scores['demographic_growth_score'] = 100
            elif growth >= 10:
                custom_scores['demographic_growth_score'] = 80
            elif growth >= 5:
                custom_scores['demographic_growth_score'] = 60
            else:
                custom_scores['demographic_growth_score'] = max(0, growth * 10)
        
        return custom_scores


class MedicalServicesAnalyzer(HealthSectorAnalyzer):
    """
    Specific analyzer for medical services companies
    """
    
    def __init__(self, sector_name: str = "Serv.Méd.Hospit. Análises e Diagnósticos"):
        super().__init__(sector_name)
    
    def get_sector_weights(self) -> SectorWeights:
        """
        Medical services weights - focus on ROIC and growth
        """
        return SectorWeights(
            earnings_yield=0.15,
            return_on_capital=0.30,  # High ROIC for service companies
            value_metrics=0.20,
            quality_metrics=0.20,
            growth_metrics=0.15,     # Growing market
            dividend_metrics=0.00
        )
    
    def calculate_custom_metrics(self, stock_data: Dict) -> Dict[str, float]:
        """
        Medical services specific metrics
        """
        custom_scores = super().calculate_custom_metrics(stock_data)
        
        # Utilization efficiency
        if ('receita_liquida' in stock_data and stock_data['receita_liquida'] is not None and
            'ativo_total' in stock_data and stock_data['ativo_total'] is not None):
            
            if stock_data['ativo_total'] > 0:
                asset_turnover = stock_data['receita_liquida'] / stock_data['ativo_total']
                custom_scores['utilization_efficiency'] = min(100, asset_turnover * 80)
        
        return custom_scores


class PharmaceuticalAnalyzer(HealthSectorAnalyzer):
    """
    Specific analyzer for pharmaceutical companies
    """
    
    def __init__(self, sector_name: str = "Medicamentos e Outros Produtos"):
        super().__init__(sector_name)
    
    def get_sector_weights(self) -> SectorWeights:
        """
        Pharmaceutical weights - focus on margins and innovation
        """
        return SectorWeights(
            earnings_yield=0.20,
            return_on_capital=0.25,
            value_metrics=0.15,
            quality_metrics=0.30,    # R&D and brand strength
            growth_metrics=0.10,
            dividend_metrics=0.00
        )
    
    def calculate_custom_metrics(self, stock_data: Dict) -> Dict[str, float]:
        """
        Pharmaceutical specific metrics
        """
        custom_scores = super().calculate_custom_metrics(stock_data)
        
        # Innovation/R&D proxy (using high margins)
        if 'mrg_ebit' in stock_data and stock_data['mrg_ebit'] is not None:
            ebit_margin = stock_data['mrg_ebit']
            if ebit_margin >= 25:  # High R&D investment and innovation
                custom_scores['innovation_score'] = 100
            elif ebit_margin >= 20:
                custom_scores['innovation_score'] = 85
            elif ebit_margin >= 15:
                custom_scores['innovation_score'] = 70
            else:
                custom_scores['innovation_score'] = max(0, ebit_margin * 4)
        
        return custom_scores


class TechnologyTelecomAnalyzer(BaseSectorAnalyzer):
    """
    Analyzer for technology and telecommunications sector
    """
    
    def __init__(self, sector_name: str = "Tecnologia e Telecomunicações"):
        super().__init__(sector_name, "Tecnologia e Telecomunicações")
    
    def get_sector_weights(self) -> SectorWeights:
        """
        Technology weights - focus on growth and ROIC
        """
        return SectorWeights(
            earnings_yield=0.15,
            return_on_capital=0.30,  # High ROIC important for tech
            value_metrics=0.15,      # Growth more important than value
            quality_metrics=0.20,
            growth_metrics=0.20,     # High growth expectations
            dividend_metrics=0.00
        )
    
    def get_excluded_metrics(self) -> List[str]:
        """
        Technology uses most metrics
        """
        return []
    
    def calculate_custom_metrics(self, stock_data: Dict) -> Dict[str, float]:
        """
        Calculate technology specific metrics
        """
        custom_scores = {}
        
        # Innovation efficiency (high margins with high growth)
        if ('mrg_liq' in stock_data and stock_data['mrg_liq'] is not None and
            'cresc_rec_5a' in stock_data and stock_data['cresc_rec_5a'] is not None):
            
            margin = stock_data['mrg_liq']
            growth = stock_data['cresc_rec_5a']
            
            if margin >= 15 and growth >= 15:
                custom_scores['tech_innovation_score'] = 100
            elif margin >= 10 and growth >= 10:
                custom_scores['tech_innovation_score'] = 80
            elif margin >= 5 and growth >= 5:
                custom_scores['tech_innovation_score'] = 60
            else:
                custom_scores['tech_innovation_score'] = max(0, (margin + growth) * 3)
        
        # Scalability (asset light model)
        if ('receita_liquida' in stock_data and stock_data['receita_liquida'] is not None and
            'ativo_total' in stock_data and stock_data['ativo_total'] is not None):
            
            if stock_data['ativo_total'] > 0:
                asset_turnover = stock_data['receita_liquida'] / stock_data['ativo_total']
                # Higher asset turnover indicates scalable business model
                custom_scores['scalability_score'] = min(100, asset_turnover * 30)
        
        return custom_scores


class TelecomAnalyzer(TechnologyTelecomAnalyzer):
    """
    Specific analyzer for telecommunications companies
    """
    
    def __init__(self, sector_name: str = "Telecomunicações"):
        super().__init__(sector_name)
    
    def get_sector_weights(self) -> SectorWeights:
        """
        Telecom weights - focus on cash flow and dividends
        """
        return SectorWeights(
            earnings_yield=0.25,     # Stable cash flows
            return_on_capital=0.20,
            value_metrics=0.20,
            quality_metrics=0.20,
            growth_metrics=0.05,     # Mature market
            dividend_metrics=0.10    # Dividend income important
        )
    
    def calculate_custom_metrics(self, stock_data: Dict) -> Dict[str, float]:
        """
        Telecom specific metrics
        """
        custom_scores = super().calculate_custom_metrics(stock_data)
        
        # Network efficiency (EBITDA margins)
        if 'ev_ebitda' in stock_data and stock_data['ev_ebitda'] is not None:
            ev_ebitda = stock_data['ev_ebitda']
            if 3 <= ev_ebitda <= 6:  # Good range for telecoms
                custom_scores['network_efficiency_score'] = 100
            elif ev_ebitda <= 8:
                custom_scores['network_efficiency_score'] = 80
            else:
                custom_scores['network_efficiency_score'] = max(0, 100 - (ev_ebitda - 8) * 10)
        
        return custom_scores


class SoftwareServicesAnalyzer(TechnologyTelecomAnalyzer):
    """
    Specific analyzer for software and services companies
    """
    
    def __init__(self, sector_name: str = "Programas e Serviços"):
        super().__init__(sector_name)
    
    def get_sector_weights(self) -> SectorWeights:
        """
        Software weights - premium on growth and ROIC
        """
        return SectorWeights(
            earnings_yield=0.10,
            return_on_capital=0.35,  # Very high ROIC expected
            value_metrics=0.10,
            quality_metrics=0.20,
            growth_metrics=0.25,     # High growth expected
            dividend_metrics=0.00
        )
    
    def calculate_custom_metrics(self, stock_data: Dict) -> Dict[str, float]:
        """
        Software specific metrics
        """
        custom_scores = super().calculate_custom_metrics(stock_data)
        
        # Software margin excellence
        if 'mrg_liq' in stock_data and stock_data['mrg_liq'] is not None:
            margin = stock_data['mrg_liq']
            if margin >= 25:  # Excellent software margins
                custom_scores['software_margin_score'] = 100
            elif margin >= 20:
                custom_scores['software_margin_score'] = 90
            elif margin >= 15:
                custom_scores['software_margin_score'] = 80
            else:
                custom_scores['software_margin_score'] = max(0, margin * 5)
        
        return custom_scores


class OthersSectorAnalyzer(BaseSectorAnalyzer):
    """
    Generic analyzer for other/miscellaneous sectors
    """
    
    def __init__(self, sector_name: str = "Outros"):
        super().__init__(sector_name, "Outros")
    
    def get_sector_weights(self) -> SectorWeights:
        """
        Balanced weights for other sectors
        """
        return SectorWeights(
            earnings_yield=0.20,
            return_on_capital=0.20,
            value_metrics=0.20,
            quality_metrics=0.20,
            growth_metrics=0.10,
            dividend_metrics=0.10
        )
    
    def get_excluded_metrics(self) -> List[str]:
        """
        Other sectors use all metrics
        """
        return []
    
    def calculate_custom_metrics(self, stock_data: Dict) -> Dict[str, float]:
        """
        No specific custom metrics for other sectors
        """
        return {}

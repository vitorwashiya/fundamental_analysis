"""
Sector analyzer factory and main sector management
"""
from typing import Dict, Type, Optional
from app.sectors.base_sector import BaseSectorAnalyzer
from app.sectors.financial_sector import (
    FinancialSectorAnalyzer, 
    InsuranceSectorAnalyzer, 
    HoldingsSectorAnalyzer
)
from app.sectors.utilities_sector import (
    UtilitiesSectorAnalyzer,
    EnergyElectricSectorAnalyzer,
    WaterSanitationAnalyzer,
    GasSectorAnalyzer
)
from app.sectors.consumer_sector import (
    ConsumerCyclicalAnalyzer,
    RetailSectorAnalyzer,
    ConstructionAnalyzer,
    ConsumerNonCyclicalAnalyzer,
    FoodBeverageAnalyzer
)
from app.sectors.materials_industrial_sector import (
    MaterialsBasicAnalyzer,
    MiningAnalyzer,
    SteelMetallurgyAnalyzer,
    IndustrialGoodsAnalyzer,
    MachineryEquipmentAnalyzer,
    TransportationAnalyzer
)
from app.sectors.health_tech_sector import (
    HealthSectorAnalyzer,
    MedicalServicesAnalyzer,
    PharmaceuticalAnalyzer,
    TechnologyTelecomAnalyzer,
    TelecomAnalyzer,
    SoftwareServicesAnalyzer,
    OthersSectorAnalyzer
)


# Sector configuration mapping subsectors to their specific analyzers
SECTOR_CONFIGURATION = {
    "Financeiro": {
        "Intermediários Financeiros": FinancialSectorAnalyzer,
        "Previdência e Seguros": InsuranceSectorAnalyzer,
        "Serviços Financeiros Diversos": FinancialSectorAnalyzer,
        "Holdings Diversificadas": HoldingsSectorAnalyzer
    },
    "Utilities": {
        "Energia Elétrica": EnergyElectricSectorAnalyzer,
        "Água e Saneamento": WaterSanitationAnalyzer,
        "Gás": GasSectorAnalyzer
    },
    "Consumo Cíclico": {
        "Construção Civil": ConstructionAnalyzer,
        "Comércio e Distribuição": RetailSectorAnalyzer,
        "Comércio": RetailSectorAnalyzer,
        "Viagens e Lazer": ConsumerCyclicalAnalyzer,
        "Tecidos, Vestuário e Calçados": ConsumerCyclicalAnalyzer,
        "Automóveis e Motocicletas": ConsumerCyclicalAnalyzer,
        "Exploração de Imóveis": ConsumerCyclicalAnalyzer,
        "Hoteis e Restaurantes": ConsumerCyclicalAnalyzer,
        "Mídia": ConsumerCyclicalAnalyzer,
        "Utilidades Domésticas": ConsumerCyclicalAnalyzer
    },
    "Consumo Não Cíclico": {
        "Alimentos Processados": FoodBeverageAnalyzer,
        "Bebidas": FoodBeverageAnalyzer,
        "Agropecuária": ConsumerNonCyclicalAnalyzer,
        "Produtos de Uso Pessoal e de Limpeza": ConsumerNonCyclicalAnalyzer
    },
    "Materiais Básicos": {
        "Siderurgia e Metalurgia": SteelMetallurgyAnalyzer,
        "Mineração": MiningAnalyzer,
        "Petróleo, Gás e Biocombustíveis": MaterialsBasicAnalyzer,
        "Madeira e Papel": MaterialsBasicAnalyzer,
        "Químicos": MaterialsBasicAnalyzer,
        "Embalagens": MaterialsBasicAnalyzer,
        "Materiais Diversos": MaterialsBasicAnalyzer
    },
    "Bens Industriais": {
        "Máquinas e Equipamentos": MachineryEquipmentAnalyzer,
        "Transporte": TransportationAnalyzer,
        "Construção e Engenharia": IndustrialGoodsAnalyzer,
        "Material de Transporte": IndustrialGoodsAnalyzer,
        "Equipamentos": IndustrialGoodsAnalyzer,
        "Serviços Diversos": IndustrialGoodsAnalyzer
    },
    "Saúde": {
        "Serv.Méd.Hospit. Análises e Diagnósticos": MedicalServicesAnalyzer,
        "Medicamentos e Outros Produtos": PharmaceuticalAnalyzer
    },
    "Tecnologia e Telecomunicações": {
        "Programas e Serviços": SoftwareServicesAnalyzer,
        "Computadores e Equipamentos": TechnologyTelecomAnalyzer,
        "Telecomunicações": TelecomAnalyzer
    },
    "Outros": {
        "Diversos": OthersSectorAnalyzer,
        "Outros": OthersSectorAnalyzer
    }
}


class SectorAnalyzerFactory:
    """
    Factory class to create appropriate sector analyzers
    """
    
    @staticmethod
    def get_analyzer(sector_name: str, subsector: Optional[str] = None) -> BaseSectorAnalyzer:
        """
        Get the appropriate analyzer for a given sector/subsector
        
        Args:
            sector_name: Main sector name (e.g., "Financeiro")
            subsector: Subsector name (e.g., "Intermediários Financeiros")
            
        Returns:
            BaseSectorAnalyzer: Appropriate analyzer instance
        """
        # Try to find specific analyzer for subsector
        if sector_name in SECTOR_CONFIGURATION and subsector:
            analyzer_class = SECTOR_CONFIGURATION[sector_name].get(subsector)
            if analyzer_class:
                return analyzer_class(subsector)
        
        # Fall back to general sector analyzer
        if sector_name == "Financeiro":
            return FinancialSectorAnalyzer()
        elif sector_name == "Utilities":
            return UtilitiesSectorAnalyzer()
        elif sector_name == "Consumo Cíclico":
            return ConsumerCyclicalAnalyzer()
        elif sector_name == "Consumo Não Cíclico":
            return ConsumerNonCyclicalAnalyzer()
        elif sector_name == "Materiais Básicos":
            return MaterialsBasicAnalyzer()
        elif sector_name == "Bens Industriais":
            return IndustrialGoodsAnalyzer()
        elif sector_name == "Saúde":
            return HealthSectorAnalyzer()
        elif sector_name == "Tecnologia e Telecomunicações":
            return TechnologyTelecomAnalyzer()
        else:
            return OthersSectorAnalyzer()
    
    @staticmethod
    def get_all_sectors() -> Dict[str, list]:
        """
        Get all configured sectors and their subsectors
        
        Returns:
            Dict: Mapping of sector categories to their subsectors
        """
        result = {}
        for category, subsectors in SECTOR_CONFIGURATION.items():
            result[category] = list(subsectors.keys())
        return result
    
    @staticmethod
    def get_sector_category(subsector: str) -> Optional[str]:
        """
        Get the main sector category for a given subsector
        
        Args:
            subsector: Subsector name
            
        Returns:
            str: Main sector category or None if not found
        """
        for category, subsectors in SECTOR_CONFIGURATION.items():
            if subsector in subsectors:
                return category
        return None

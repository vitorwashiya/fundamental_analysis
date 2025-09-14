"""
Data provider interface and implementations for Brazilian stock data.
"""
import pandas as pd
from typing import List, Optional
from abc import ABC, abstractmethod
import fundamentus as fd
import logging

from .models import StockData, Sector


logger = logging.getLogger(__name__)


class DataProvider(ABC):
    """Abstract base class for data providers."""
    
    @abstractmethod
    def get_stock_data(self, symbol: Optional[str] = None) -> List[StockData]:
        """Get stock data for specific symbol or all stocks."""
        pass
    
    @abstractmethod
    def get_sector_stocks(self, sector: Sector) -> List[StockData]:
        """Get all stocks from a specific sector."""
        pass


class FundamentusProvider(DataProvider):
    """Data provider using fundamentus library."""
    
    def __init__(self):
        self._sector_mapping = self._create_sector_mapping()
    
    def _create_sector_mapping(self) -> dict:
        """Create mapping from fundamentus sector names to our Sector enum."""
        return {
            "Agronegócios": Sector.AGRONEGOCIO,
            "Bebidas": Sector.BEBIDAS,
            "Construção": Sector.CONSTRUCAO,
            "Eletroeletrônicos": Sector.ELETROELECTRONICOS,
            "Energia Elétrica": Sector.ENERGIA_ELETRICA,
            "Finanças e Seguros": Sector.FINANCEIROS,
            "Diversos": Sector.OUTROS,
            "Máquinas Industriais": Sector.MACHINES_EQUIPMENTS,
            "Mineração": Sector.MINERACAO,
            "Papel e Celulose": Sector.PAPEL_CELULOSE,
            "Petróleo e Gás": Sector.PETROLEO_GAS,
            "Química": Sector.QUIMICOS,
            "Siderurgia e Metalurgia": Sector.SIDERURGIA_METALURGIA,
            "Software e Dados": Sector.SOFTWARE_DADOS,
            "Telecomunicações": Sector.TELECOMUNICACOES,
            "Têxtil": Sector.TEXTIL,
            "Transporte e Logística": Sector.TRANSPORTE_SERVICOS,
            "Veículos e peças": Sector.VEICULOS_PECAS,
        }
    
    def _map_sector(self, sector_name: str) -> Sector:
        """Map fundamentus sector name to our Sector enum."""
        return self._sector_mapping.get(sector_name, Sector.OUTROS)
    
    def _convert_to_stock_data(self, row: pd.Series) -> StockData:
        """Convert fundamentus dataframe row to StockData object."""
        # Get sector information
        try:
            sector_name = fd.get_setor_id(row.name)
            sector = self._map_sector(sector_name)
        except Exception:
            sector = Sector.OUTROS
        
        # Convert data types and handle NaN values
        def safe_float(value):
            try:
                if pd.isna(value) or value == '-':
                    return None
                return float(str(value).replace(',', '.').replace('%', ''))
            except (ValueError, TypeError):
                return None
        
        stock_data = StockData(
            symbol=row.name,
            company_name=row.name,  # fundamentus doesn't provide company name in resultado
            sector=sector,
            price=safe_float(row.get('Cotacao')),
            pl=safe_float(row.get('P/L')),
            pvp=safe_float(row.get('P/VP')),
            psr=safe_float(row.get('PSR')),
            dy=safe_float(row.get('Div.Yield')),
            pa=safe_float(row.get('P/Ativo')),
            pcg=safe_float(row.get('P/Cap.Giro')),
            pebit=safe_float(row.get('P/EBIT')),
            pacl=safe_float(row.get('P/ACL')),
            evebit=safe_float(row.get('EV/EBIT')),
            evebitda=safe_float(row.get('EV/EBITDA')),
            mrgebit=safe_float(row.get('Marg. EBIT')),
            mrgebitda=safe_float(row.get('Marg. EBITDA')),
            mrgliq=safe_float(row.get('Marg. Liquida')),
            roic=safe_float(row.get('ROIC')),
            roe=safe_float(row.get('ROE')),
            roa=safe_float(row.get('ROA')),
            liqc=safe_float(row.get('Liq. Corr.')),
            liq2m=safe_float(row.get('Liq.2meses')),
            divbr_pl=safe_float(row.get('Div.Br/Patrim.')),
            crescrec=safe_float(row.get('Cresc. Rec.5a')),
        )
        
        # Calculate additional indicators
        self._calculate_derived_indicators(stock_data)
        
        return stock_data
    
    def _calculate_derived_indicators(self, stock_data: StockData):
        """Calculate derived financial indicators."""
        # Calculate Debt/EBITDA ratio (simplified)
        # In a real implementation, we would need actual debt and EBITDA values
        if stock_data.evebitda and stock_data.divbr_pl:
            # This is a simplified approximation
            # Real calculation would require market cap and enterprise value
            stock_data.divida_liquida_ebitda = stock_data.divbr_pl * 0.1  # Placeholder
    
    def get_stock_data(self, symbol: Optional[str] = None) -> List[StockData]:
        """Get stock data using fundamentus."""
        try:
            if symbol:
                # Get specific stock
                df = fd.get_resultado()
                if symbol in df.index:
                    return [self._convert_to_stock_data(df.loc[symbol])]
                else:
                    logger.warning(f"Symbol {symbol} not found")
                    return []
            else:
                # Get all stocks
                df = fd.get_resultado()
                return [self._convert_to_stock_data(row) for _, row in df.iterrows()]
        
        except Exception as e:
            logger.error(f"Error getting stock data: {e}")
            return []
    
    def get_sector_stocks(self, sector: Sector) -> List[StockData]:
        """Get all stocks from a specific sector."""
        all_stocks = self.get_stock_data()
        return [stock for stock in all_stocks if stock.sector == sector]


class MockDataProvider(DataProvider):
    """Mock data provider for testing and demonstration."""
    
    def __init__(self):
        self._mock_data = self._create_mock_data()
    
    def _create_mock_data(self) -> List[StockData]:
        """Create sample mock data for demonstration."""
        return [
            StockData(
                symbol="ITUB4",
                company_name="Itaú Unibanco",
                sector=Sector.FINANCEIROS,
                price=32.50,
                pl=8.5,
                pvp=1.2,
                dy=0.065,
                evebitda=4.2,
                mrgliq=0.22,
                mrgebitda=0.45,
                roe=0.18,
                divida_liquida_ebitda=2.1,
            ),
            StockData(
                symbol="PETR4",
                company_name="Petrobras",
                sector=Sector.PETROLEO_GAS,
                price=38.75,
                pl=6.8,
                pvp=0.9,
                dy=0.085,
                evebitda=3.5,
                mrgliq=0.25,
                mrgebitda=0.55,
                roe=0.25,
                divida_liquida_ebitda=1.8,
            ),
            StockData(
                symbol="VALE3",
                company_name="Vale",
                sector=Sector.MINERACAO,
                price=68.20,
                pl=7.2,
                pvp=1.1,
                dy=0.12,
                evebitda=4.8,
                mrgliq=0.35,
                mrgebitda=0.48,
                roe=0.22,
                divida_liquida_ebitda=1.5,
            ),
            StockData(
                symbol="MGLU3",
                company_name="Magazine Luiza",
                sector=Sector.LOJA_DEPARTAMENTO,
                price=4.25,
                pl=15.3,
                pvp=2.1,
                dy=0.02,
                evebitda=25.8,
                mrgliq=-0.05,
                mrgebitda=0.08,
                roe=-0.02,
                divida_liquida_ebitda=8.5,
            ),
            StockData(
                symbol="WEGE3",
                company_name="WEG",
                sector=Sector.MACHINES_EQUIPMENTS,
                price=45.80,
                pl=18.5,
                pvp=4.2,
                dy=0.018,
                evebitda=12.5,
                mrgliq=0.15,
                mrgebitda=0.22,
                roe=0.18,
                divida_liquida_ebitda=0.8,
            ),
        ]
    
    def get_stock_data(self, symbol: Optional[str] = None) -> List[StockData]:
        """Get mock stock data."""
        if symbol:
            return [stock for stock in self._mock_data if stock.symbol == symbol]
        return self._mock_data.copy()
    
    def get_sector_stocks(self, sector: Sector) -> List[StockData]:
        """Get mock stocks from a specific sector."""
        return [stock for stock in self._mock_data if stock.sector == sector]
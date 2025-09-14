"""
Data models for Brazilian stock fundamental analysis.
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum


class Sector(Enum):
    """Brazilian stock market sectors."""
    AGRONEGOCIO = "Agronegócio"
    BEBIDAS = "Bebidas"
    CONSTRUCAO = "Construção"
    ELETROELECTRONICOS = "Eletroeletrônicos"
    ENERGIA_ELETRICA = "Energia Elétrica"
    FINANCEIROS = "Financeiros"
    LOJA_DEPARTAMENTO = "Loja Departamento"
    MACHINES_EQUIPMENTS = "Máquinas e Equipamentos"
    MINERACAO = "Mineração"
    PAPEL_CELULOSE = "Papel e Celulose"
    PETROLEO_GAS = "Petróleo e Gás"
    QUIMICOS = "Químicos"
    SIDERURGIA_METALURGIA = "Siderurgia e Metalurgia"
    SOFTWARE_DADOS = "Software e Dados"
    TELECOMUNICACOES = "Telecomunicações"
    TEXTIL = "Têxtil"
    TRANSPORTE_SERVICOS = "Transporte e Serviços"
    VEICULOS_PECAS = "Veículos e Peças"
    OUTROS = "Outros"


@dataclass
class StockData:
    """Stock fundamental data structure."""
    symbol: str
    company_name: str
    sector: Sector
    
    # Price indicators
    price: Optional[float] = None
    
    # Valuation indicators
    pl: Optional[float] = None  # P/L (Price/Earnings)
    pvp: Optional[float] = None  # P/VP (Price/Book Value)
    psr: Optional[float] = None  # P/Receita (Price/Sales)
    dy: Optional[float] = None  # Dividend Yield
    pa: Optional[float] = None  # P/Ativos (Price/Assets)
    pcg: Optional[float] = None  # P/Capital de Giro
    pebit: Optional[float] = None  # P/EBIT
    pacl: Optional[float] = None  # P/Ativos Circulantes Líquidos
    evebit: Optional[float] = None  # EV/EBIT
    evebitda: Optional[float] = None  # EV/EBITDA
    mrgebit: Optional[float] = None  # Margem EBIT
    mrgebitda: Optional[float] = None  # Margem EBITDA
    mrgliq: Optional[float] = None  # Margem Líquida
    
    # Efficiency indicators
    roic: Optional[float] = None  # ROIC (Return on Invested Capital)
    roe: Optional[float] = None  # ROE (Return on Equity)
    roa: Optional[float] = None  # ROA (Return on Assets)
    liqc: Optional[float] = None  # Liquidez Corrente
    liq2m: Optional[float] = None  # Liquidez 2 meses
    
    # Debt indicators
    divbr_pl: Optional[float] = None  # Dívida Bruta/Patrimônio
    crescrec: Optional[float] = None  # Crescimento Receita (5 anos)
    
    # Additional calculated fields
    divida_liquida_ebitda: Optional[float] = None  # Debt to EBITDA ratio
    
    def __post_init__(self):
        """Calculate additional derived indicators."""
        if self.evebitda and self.divbr_pl:
            # Simplified calculation for demonstration
            # In real implementation, would need actual debt and EBITDA values
            pass


@dataclass
class ScreeningCriteria:
    """Criteria for screening stocks."""
    # P/L filters
    pl_min: Optional[float] = None
    pl_max: Optional[float] = None
    
    # Margin filters
    mrgliq_min: Optional[float] = None  # Minimum net margin
    mrgebitda_min: Optional[float] = None  # Minimum EBITDA margin
    
    # EV/EBITDA filters
    evebitda_min: Optional[float] = None
    evebitda_max: Optional[float] = None
    
    # Debt filters
    divida_liquida_ebitda_max: Optional[float] = None  # Maximum debt/EBITDA
    
    # ROE filters
    roe_min: Optional[float] = None
    
    # Dividend Yield filters
    dy_min: Optional[float] = None
    
    # Sector filters
    sectors: Optional[list[Sector]] = None
    
    # Market cap filters (in millions BRL)
    market_cap_min: Optional[float] = None
    

@dataclass
class AnalysisResult:
    """Result of fundamental analysis screening."""
    stock: StockData
    score: float
    reasons: list[str]
    warnings: list[str]
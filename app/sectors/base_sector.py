"""
Abstract base class for sector-specific analysis
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import pandas as pd


@dataclass
class SectorWeights:
    """
    Weights for different scoring criteria by sector
    """
    earnings_yield: float = 0.0  # EBIT/EV weight
    return_on_capital: float = 0.0  # ROIC weight
    value_metrics: float = 0.0  # P/E, P/B, P/S weights
    quality_metrics: float = 0.0  # Margins, liquidity weights
    growth_metrics: float = 0.0  # Revenue/earnings growth weights
    dividend_metrics: float = 0.0  # Dividend yield, payout weights
    
    def normalize(self) -> 'SectorWeights':
        """Normalize weights to sum to 1.0"""
        total = (
            self.earnings_yield + self.return_on_capital + 
            self.value_metrics + self.quality_metrics + 
            self.growth_metrics + self.dividend_metrics
        )
        if total == 0:
            return self
        
        return SectorWeights(
            earnings_yield=self.earnings_yield / total,
            return_on_capital=self.return_on_capital / total,
            value_metrics=self.value_metrics / total,
            quality_metrics=self.quality_metrics / total,
            growth_metrics=self.growth_metrics / total,
            dividend_metrics=self.dividend_metrics / total
        )


class BaseSectorAnalyzer(ABC):
    """
    Abstract base class for sector-specific financial analysis
    """
    
    def __init__(self, sector_name: str, category: str):
        self.sector_name = sector_name
        self.category = category
        self._weights = self.get_sector_weights()
    
    @abstractmethod
    def get_sector_weights(self) -> SectorWeights:
        """
        Define the weights for different metrics for this sector
        """
        pass
    
    @abstractmethod
    def get_excluded_metrics(self) -> List[str]:
        """
        Return list of metrics that should be excluded for this sector
        Example: Banks don't use EV/EBITDA
        """
        pass
    
    @abstractmethod
    def calculate_custom_metrics(self, stock_data: Dict) -> Dict[str, float]:
        """
        Calculate sector-specific custom metrics
        """
        pass
    
    def calculate_earnings_yield_score(self, stock_data: Dict) -> float:
        """
        Calculate earnings yield score (EBIT/EV or sector-specific equivalent)
        """
        if 'ev_ebit' in stock_data and stock_data['ev_ebit'] is not None:
            ev_ebit = stock_data['ev_ebit']
            if ev_ebit > 0:
                return min(100, (1 / ev_ebit) * 100)  # Higher EBIT/EV is better
        return 0.0
    
    def calculate_return_on_capital_score(self, stock_data: Dict) -> float:
        """
        Calculate return on invested capital score
        """
        if 'roic' in stock_data and stock_data['roic'] is not None:
            roic = stock_data['roic']
            if roic is not None:
                return min(100, max(0, roic * 5))  # Scale ROIC to 0-100
        return 0.0
    
    def calculate_value_score(self, stock_data: Dict) -> float:
        """
        Calculate composite value score based on P/E, P/B, P/S ratios
        """
        scores = []
        
        # P/E score (lower is better)
        if 'pl' in stock_data and stock_data['pl'] is not None and stock_data['pl'] > 0:
            pe_score = max(0, 100 - (stock_data['pl'] - 5) * 5)  # Optimal PE around 5-15
            scores.append(pe_score)
        
        # P/B score (lower is better) 
        if 'pvp' in stock_data and stock_data['pvp'] is not None and stock_data['pvp'] > 0:
            pb_score = max(0, 100 - (stock_data['pvp'] - 1) * 25)  # Optimal PB around 1-2
            scores.append(pb_score)
        
        # P/S score (lower is better)
        if 'psr' in stock_data and stock_data['psr'] is not None and stock_data['psr'] > 0:
            ps_score = max(0, 100 - stock_data['psr'] * 20)  # Lower P/S is better
            scores.append(ps_score)
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def calculate_quality_score(self, stock_data: Dict) -> float:
        """
        Calculate quality score based on margins and financial health
        """
        scores = []
        
        # EBIT margin
        if 'mrg_ebit' in stock_data and stock_data['mrg_ebit'] is not None:
            margin_score = min(100, max(0, stock_data['mrg_ebit'] * 5))
            scores.append(margin_score)
        
        # Net margin
        if 'mrg_liq' in stock_data and stock_data['mrg_liq'] is not None:
            net_margin_score = min(100, max(0, stock_data['mrg_liq'] * 5))
            scores.append(net_margin_score)
        
        # Current liquidity
        if 'liq_corr' in stock_data and stock_data['liq_corr'] is not None:
            liquidity_score = min(100, max(0, (stock_data['liq_corr'] - 1) * 50))
            scores.append(liquidity_score)
        
        # ROE
        if 'roe' in stock_data and stock_data['roe'] is not None:
            roe_score = min(100, max(0, stock_data['roe'] * 5))
            scores.append(roe_score)
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def calculate_growth_score(self, stock_data: Dict) -> float:
        """
        Calculate growth score based on revenue growth
        """
        if 'cresc_rec_5a' in stock_data and stock_data['cresc_rec_5a'] is not None:
            growth = stock_data['cresc_rec_5a']
            if growth is not None:
                return min(100, max(0, growth * 5))  # Scale growth to 0-100
        return 0.0
    
    def calculate_dividend_score(self, stock_data: Dict) -> float:
        """
        Calculate dividend score based on dividend yield
        """
        if 'div_yield' in stock_data and stock_data['div_yield'] is not None:
            div_yield = stock_data['div_yield']
            if div_yield is not None and div_yield > 0:
                # Optimal dividend yield around 4-8%
                if 4 <= div_yield <= 8:
                    return 100
                elif div_yield < 4:
                    return div_yield * 25  # Scale 0-4% to 0-100
                else:
                    return max(0, 100 - (div_yield - 8) * 10)  # Penalize very high yields
        return 0.0
    
    def calculate_final_score(self, stock_data: Dict) -> Tuple[Dict[str, float], float]:
        """
        Calculate final weighted score for the stock
        """
        excluded_metrics = self.get_excluded_metrics()
        
        # Calculate individual scores
        earnings_yield_score = 0.0 if 'earnings_yield' in excluded_metrics else self.calculate_earnings_yield_score(stock_data)
        return_on_capital_score = 0.0 if 'return_on_capital' in excluded_metrics else self.calculate_return_on_capital_score(stock_data)
        value_score = 0.0 if 'value_metrics' in excluded_metrics else self.calculate_value_score(stock_data)
        quality_score = 0.0 if 'quality_metrics' in excluded_metrics else self.calculate_quality_score(stock_data)
        growth_score = 0.0 if 'growth_metrics' in excluded_metrics else self.calculate_growth_score(stock_data)
        dividend_score = 0.0 if 'dividend_metrics' in excluded_metrics else self.calculate_dividend_score(stock_data)
        
        # Apply custom metrics
        custom_metrics = self.calculate_custom_metrics(stock_data)
        
        # Calculate weighted final score
        weights = self._weights.normalize()
        final_score = (
            earnings_yield_score * weights.earnings_yield +
            return_on_capital_score * weights.return_on_capital +
            value_score * weights.value_metrics +
            quality_score * weights.quality_metrics +
            growth_score * weights.growth_metrics +
            dividend_score * weights.dividend_metrics
        )
        
        scores = {
            'earnings_yield_score': earnings_yield_score,
            'return_on_capital_score': return_on_capital_score,
            'value_score': value_score,
            'quality_score': quality_score,
            'growth_score': growth_score,
            'dividend_score': dividend_score,
            'final_score': final_score
        }
        
        # Add custom metrics to scores
        scores.update(custom_metrics)
        
        return scores, final_score
    
    def rank_stocks(self, stocks_df: pd.DataFrame) -> pd.DataFrame:
        """
        Rank stocks within this sector
        """
        ranked_stocks = []
        
        for _, stock in stocks_df.iterrows():
            stock_dict = stock.to_dict()
            scores, final_score = self.calculate_final_score(stock_dict)
            
            stock_result = stock_dict.copy()
            stock_result.update(scores)
            ranked_stocks.append(stock_result)
        
        # Create DataFrame and sort by final score
        result_df = pd.DataFrame(ranked_stocks)
        result_df = result_df.sort_values('final_score', ascending=False)
        result_df['rank_position'] = range(1, len(result_df) + 1)
        
        return result_df

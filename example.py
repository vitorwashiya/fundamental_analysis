#!/usr/bin/env python3
"""
Example usage of the Brazilian Stock Fundamental Analysis Screener.

This script demonstrates various ways to use the screener to find
investment opportunities in Brazilian stocks.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from fundamental_screener import (
    FundamentalScreener, 
    ScreeningCriteria, 
    Sector
)


def main():
    """Demonstrate the screener capabilities."""
    print("=" * 80)
    print("BRAZILIAN STOCK FUNDAMENTAL ANALYSIS SCREENER - DEMO")
    print("=" * 80)
    
    # Initialize screener with mock data for demo
    screener = FundamentalScreener(use_mock_data=True)
    print("✓ Screener initialized with mock data\n")
    
    # Example 1: Top opportunities across all sectors
    print("1. TOP 3 INVESTMENT OPPORTUNITIES")
    print("-" * 40)
    top_opportunities = screener.get_top_opportunities(max_results=3)
    
    for i, result in enumerate(top_opportunities, 1):
        stock = result.stock
        print(f"{i}. {stock.symbol} - {stock.company_name}")
        print(f"   Sector: {stock.sector.value}")
        print(f"   Score: {result.score:.1f}/100")
        print(f"   P/L: {stock.pl:.1f} | ROE: {stock.roe*100:.1f}% | DY: {stock.dy*100:.1f}%")
        print(f"   Reasons: {', '.join(result.reasons[:2])}")
        print()
    
    # Example 2: Sector-specific analysis
    print("2. BANKING SECTOR ANALYSIS")
    print("-" * 40)
    bank_results = screener.screen_sector(Sector.FINANCEIROS)
    
    for result in bank_results:
        stock = result.stock
        print(f"• {stock.symbol}: Score {result.score:.1f}, P/L {stock.pl:.1f}, ROE {stock.roe*100:.1f}%")
    print()
    
    # Example 3: Custom criteria screening
    print("3. CONSERVATIVE DIVIDEND SCREENING")
    print("-" * 40)
    
    conservative_criteria = ScreeningCriteria(
        pl_max=12.0,        # P/L <= 12
        roe_min=0.15,       # ROE >= 15%
        dy_min=0.05,        # Dividend yield >= 5%
        divida_liquida_ebitda_max=2.5  # Low debt
    )
    
    conservative_results = screener.get_top_opportunities(
        max_results=5, 
        additional_criteria=conservative_criteria
    )
    
    print(f"Found {len(conservative_results)} stocks meeting conservative criteria:")
    for result in conservative_results:
        stock = result.stock
        print(f"• {stock.symbol}: P/L {stock.pl:.1f}, ROE {stock.roe*100:.1f}%, "
              f"DY {stock.dy*100:.1f}%, Debt/EBITDA {stock.divida_liquida_ebitda:.1f}")
    print()
    
    # Example 4: Analyze specific stock
    print("4. SPECIFIC STOCK ANALYSIS")
    print("-" * 40)
    
    symbol = "PETR4"
    analysis = screener.analyze_specific_stock(symbol)
    
    if analysis:
        stock = analysis.stock
        print(f"Analysis for {symbol} - {stock.company_name}")
        print(f"Sector: {stock.sector.value}")
        print(f"Score: {analysis.score:.1f}/100")
        print(f"Price: R$ {stock.price:.2f}")
        print(f"Key Metrics:")
        print(f"  • P/L: {stock.pl:.1f}")
        print(f"  • ROE: {stock.roe*100:.1f}%")
        print(f"  • Net Margin: {stock.mrgliq*100:.1f}%")
        print(f"  • EV/EBITDA: {stock.evebitda:.1f}")
        print(f"  • Dividend Yield: {stock.dy*100:.1f}%")
        print(f"  • Debt/EBITDA: {stock.divida_liquida_ebitda:.1f}")
        
        print("\nInvestment Case:")
        for reason in analysis.reasons:
            print(f"  ✓ {reason}")
        
        if analysis.warnings:
            print("\nWarnings:")
            for warning in analysis.warnings:
                print(f"  ⚠ {warning}")
    else:
        print(f"Stock {symbol} not found.")
    
    print("\n" + "=" * 80)
    print("DEMO COMPLETE")
    print("=" * 80)
    
    print("\nTo run with real data (requires internet):")
    print("  python main.py --top 5")
    print("\nTo see all options:")
    print("  python main.py --help")


if __name__ == "__main__":
    main()
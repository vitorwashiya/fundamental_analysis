"""
Command line interface for the fundamental analysis screener.
"""
import argparse
import logging
from typing import List

from .screener import FundamentalScreener
from .models import Sector, ScreeningCriteria, AnalysisResult


def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def print_results(results: List[AnalysisResult], title: str = "Analysis Results"):
    """Print analysis results in a formatted way."""
    print(f"\n{'='*80}")
    print(f"{title.center(80)}")
    print(f"{'='*80}")
    
    if not results:
        print("No opportunities found with the specified criteria.")
        return
    
    for i, result in enumerate(results, 1):
        stock = result.stock
        print(f"\n{i}. {stock.symbol} - {stock.company_name}")
        print(f"   Sector: {stock.sector.value}")
        print(f"   Score: {result.score:.1f}/100")
        print(f"   Price: R$ {stock.price:.2f}" if stock.price else "   Price: N/A")
        
        # Key metrics
        metrics = []
        if stock.pl:
            metrics.append(f"P/L: {stock.pl:.1f}")
        if stock.roe:
            metrics.append(f"ROE: {stock.roe*100:.1f}%")
        if stock.dy:
            metrics.append(f"DY: {stock.dy*100:.1f}%")
        if stock.evebitda:
            metrics.append(f"EV/EBITDA: {stock.evebitda:.1f}")
        if stock.mrgliq:
            metrics.append(f"Net Margin: {stock.mrgliq*100:.1f}%")
        
        if metrics:
            print(f"   Metrics: {' | '.join(metrics)}")
        
        # Reasons
        if result.reasons:
            print("   ✓ Reasons:")
            for reason in result.reasons:
                print(f"     • {reason}")
        
        # Warnings
        if result.warnings:
            print("   ⚠ Warnings:")
            for warning in result.warnings:
                print(f"     • {warning}")
        
        print("-" * 80)


def parse_sectors(sector_names: str) -> List[Sector]:
    """Parse comma-separated sector names."""
    if not sector_names:
        return []
    
    sector_map = {sector.name: sector for sector in Sector}
    sectors = []
    
    for name in sector_names.split(','):
        name = name.strip().upper()
        if name in sector_map:
            sectors.append(sector_map[name])
        else:
            print(f"Warning: Unknown sector '{name}'. Available sectors:")
            for sector in Sector:
                print(f"  - {sector.name}")
    
    return sectors


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Brazilian Stock Fundamental Analysis Screener",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Screen all sectors for top opportunities
  python -m src.fundamental_screener.cli --top 5

  # Screen specific sectors
  python -m src.fundamental_screener.cli --sectors FINANCEIROS,MINERACAO

  # Analyze specific stock
  python -m src.fundamental_screener.cli --symbol ITUB4

  # Screen with custom criteria
  python -m src.fundamental_screener.cli --max-pe 15 --min-roe 0.15 --max-debt-ebitda 2.0

  # Use mock data for demonstration
  python -m src.fundamental_screener.cli --mock --top 5
        """
    )
    
    # General options
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Verbose output')
    parser.add_argument('--mock', action='store_true',
                        help='Use mock data for demonstration')
    
    # Screening modes
    parser.add_argument('--top', type=int, metavar='N',
                        help='Show top N opportunities across all sectors')
    parser.add_argument('--sectors', type=str, metavar='SECTORS',
                        help='Comma-separated list of sectors to screen (e.g., FINANCEIROS,MINERACAO)')
    parser.add_argument('--symbol', type=str, metavar='SYMBOL',
                        help='Analyze specific stock symbol')
    
    # Custom criteria
    parser.add_argument('--min-pe', type=float, metavar='VALUE',
                        help='Minimum P/E ratio')
    parser.add_argument('--max-pe', type=float, metavar='VALUE',
                        help='Maximum P/E ratio')
    parser.add_argument('--min-roe', type=float, metavar='VALUE',
                        help='Minimum ROE (as decimal, e.g., 0.15 for 15%%)')
    parser.add_argument('--min-margin', type=float, metavar='VALUE',
                        help='Minimum net margin (as decimal)')
    parser.add_argument('--min-ebitda-margin', type=float, metavar='VALUE',
                        help='Minimum EBITDA margin (as decimal)')
    parser.add_argument('--max-ev-ebitda', type=float, metavar='VALUE',
                        help='Maximum EV/EBITDA ratio')
    parser.add_argument('--max-debt-ebitda', type=float, metavar='VALUE',
                        help='Maximum Debt/EBITDA ratio')
    parser.add_argument('--min-dividend-yield', type=float, metavar='VALUE',
                        help='Minimum dividend yield (as decimal)')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Initialize screener
    screener = FundamentalScreener(use_mock_data=args.mock)
    
    # Build custom criteria if provided
    criteria = None
    if any([args.min_pe, args.max_pe, args.min_roe, args.min_margin, 
            args.min_ebitda_margin, args.max_ev_ebitda, args.max_debt_ebitda, 
            args.min_dividend_yield]):
        criteria = ScreeningCriteria(
            pl_min=args.min_pe,
            pl_max=args.max_pe,
            roe_min=args.min_roe,
            mrgliq_min=args.min_margin,
            mrgebitda_min=args.min_ebitda_margin,
            evebitda_max=args.max_ev_ebitda,
            divida_liquida_ebitda_max=args.max_debt_ebitda,
            dy_min=args.min_dividend_yield
        )
    
    # Execute based on mode
    if args.symbol:
        # Analyze specific stock
        result = screener.analyze_specific_stock(args.symbol)
        if result:
            print_results([result], f"Analysis for {args.symbol}")
        else:
            print(f"Stock {args.symbol} not found.")
    
    elif args.top:
        # Top opportunities
        sectors = parse_sectors(args.sectors) if args.sectors else None
        results = screener.get_top_opportunities(args.top, sectors, criteria)
        print_results(results, f"Top {args.top} Investment Opportunities")
    
    elif args.sectors:
        # Specific sectors
        sectors = parse_sectors(args.sectors)
        if sectors:
            all_results = []
            for sector in sectors:
                sector_results = screener.screen_sector(sector, criteria)
                all_results.extend(sector_results)
            
            all_results.sort(key=lambda x: x.score, reverse=True)
            print_results(all_results, f"Opportunities in Selected Sectors")
        else:
            print("No valid sectors specified.")
    
    else:
        # Default: screen all sectors
        sector_results = screener.screen_all_sectors(criteria)
        
        if sector_results:
            print(f"\n{'='*80}")
            print("FUNDAMENTAL ANALYSIS SCREENING RESULTS")
            print(f"{'='*80}")
            
            for sector, results in sector_results.items():
                if results:
                    print_results(results[:3], f"{sector.value} - Top 3 Opportunities")
        else:
            print("No opportunities found.")


if __name__ == '__main__':
    main()
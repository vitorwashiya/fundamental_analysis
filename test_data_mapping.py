"""
Script para testar o mapeamento correto dos dados do fundamentus
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import fundamentus
import pandas as pd
from app.services.fundamentus_service import FundamentusService
from app.database.connection import get_db

def test_data_mapping():
    """Testa o mapeamento de dados"""
    
    print("=== TESTANDO MAPEAMENTO DE DADOS ===")
    
    # Buscar dados do fundamentus
    df = fundamentus.get_resultado()
    print(f"Total de ações: {len(df)}")
    
    # Pegar algumas ações para teste
    test_symbols = ['PETR4', 'VALE3', 'ITUB4', 'BBDC4', 'ABEV3']
    
    for symbol in test_symbols:
        if symbol in df.index:
            print(f"\n=== DADOS DE {symbol} ===")
            row = df.loc[symbol]
            
            # Simular o processamento do FundamentusService
            def safe_float(value):
                if pd.isna(value) or value in ['', '-', None]:
                    return None
                try:
                    return float(value)
                except (ValueError, TypeError):
                    return None
            
            # Mapear dados com os nomes corretos
            mapped_data = {
                'symbol': symbol,
                'cotacao': safe_float(row.get('cotacao')),
                'pl': safe_float(row.get('pl')),
                'pvp': safe_float(row.get('pvp')),
                'psr': safe_float(row.get('psr')),
                'div_yield': safe_float(row.get('dy')),  # dy no get_resultado
                'p_ativo': safe_float(row.get('pa')),   # pa no get_resultado
                'p_cap_giro': safe_float(row.get('pcg')), # pcg no get_resultado
                'p_ebit': safe_float(row.get('pebit')),   # pebit no get_resultado
                'ev_ebit': safe_float(row.get('evebit')), # evebit no get_resultado
                'ev_ebitda': safe_float(row.get('evebitda')), # evebitda no get_resultado
                'mrg_ebit': safe_float(row.get('mrgebit')), # mrgebit no get_resultado
                'mrg_liq': safe_float(row.get('mrgliq')),   # mrgliq no get_resultado
                'roic': safe_float(row.get('roic')),
                'roe': safe_float(row.get('roe')),
                'liq_corr': safe_float(row.get('liqc')),    # liqc no get_resultado
                'liq_2meses': safe_float(row.get('liq2m')), # liq2m no get_resultado
                'patrim_liq': safe_float(row.get('patrliq')), # patrliq no get_resultado
                'div_br_patrim': safe_float(row.get('divbpatr')), # divbpatr no get_resultado
                'cresc_rec_5a': safe_float(row.get('c5y')),       # c5y no get_resultado
            }
            
            print("Dados mapeados:")
            for key, value in mapped_data.items():
                if value is not None:
                    print(f"  {key}: {value}")
            
            # Contar quantos campos não são None
            non_null_fields = sum(1 for v in mapped_data.values() if v is not None)
            total_fields = len(mapped_data)
            print(f"\nCampos preenchidos: {non_null_fields}/{total_fields} ({non_null_fields/total_fields*100:.1f}%)")
            
            break  # Só testar um para não poluir a saída

if __name__ == "__main__":
    test_data_mapping()

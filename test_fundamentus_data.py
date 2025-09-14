"""
Script para testar e verificar os dados que chegam da biblioteca fundamentus
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import fundamentus
import pandas as pd
from pprint import pprint

def test_fundamentus_data():
    """Testa os dados que chegam do fundamentus"""
    
    print("=== TESTANDO FUNDAMENTUS.GET_RESULTADO() ===")
    try:
        df = fundamentus.get_resultado()
        print(f"Total de ações encontradas: {len(df)}")
        print(f"Colunas disponíveis: {list(df.columns)}")
        print("\n=== AMOSTRA DOS DADOS (primeira ação) ===")
        
        if len(df) > 0:
            # Pegar primeira ação
            first_stock = df.iloc[0]
            print(f"Símbolo: {first_stock.name}")
            print("Dados disponíveis:")
            for col, value in first_stock.items():
                print(f"  {col}: {value} (tipo: {type(value)})")
        
        print("\n=== AMOSTRA DE 5 AÇÕES ===")
        print(df.head().to_string())
        
    except Exception as e:
        print(f"Erro ao acessar fundamentus.get_resultado(): {e}")
    
    print("\n" + "="*80)
    print("=== TESTANDO FUNDAMENTUS.GET_PAPEL() ===")
    try:
        # Testar com uma ação específica
        test_symbols = ['PETR4', 'VALE3', 'ITUB4', 'BBDC4', 'ABEV3']
        
        for symbol in test_symbols:
            try:
                papel_data = fundamentus.get_papel(symbol)
                print(f"\n--- Dados de {symbol} ---")
                if isinstance(papel_data, dict):
                    for key, value in papel_data.items():
                        print(f"  {key}: {value}")
                else:
                    print(f"Tipo retornado: {type(papel_data)}")
                    print(papel_data)
                break  # Só testar um para não demorar
            except Exception as e:
                print(f"Erro ao buscar {symbol}: {e}")
                continue
    
    except Exception as e:
        print(f"Erro geral no fundamentus.get_papel(): {e}")

if __name__ == "__main__":
    test_fundamentus_data()

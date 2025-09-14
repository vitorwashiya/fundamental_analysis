#!/bin/bash

# Test runner script for Fundamental Analysis API

echo "🧪 Executando testes da API de Análise Fundamentalista..."
echo ""

# Verificar se o pytest está instalado
if ! command -v pytest &> /dev/null; then
    echo "❌ pytest não encontrado. Instalando dependências..."
    pip install -r requirements.txt
fi

# Criar diretório de logs de teste se não existir
mkdir -p logs/tests

# Executar testes com relatório detalhado
echo "📋 Executando todos os testes..."
pytest tests/ -v --tb=short --maxfail=5 --durations=10 2>&1 | tee logs/tests/test_results.log

# Verificar se os testes passaram
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Todos os testes passaram com sucesso!"
    echo "📊 Relatório salvo em: logs/tests/test_results.log"
else
    echo ""
    echo "❌ Alguns testes falharam. Verifique o relatório em: logs/tests/test_results.log"
    exit 1
fi

# Executar testes de cobertura se coverage estiver instalado
if command -v coverage &> /dev/null; then
    echo ""
    echo "📈 Gerando relatório de cobertura..."
    coverage run -m pytest tests/ 2>/dev/null
    coverage report --skip-covered 2>/dev/null
    coverage html -d logs/tests/coverage_html 2>/dev/null
    echo "📊 Relatório de cobertura HTML salvo em: logs/tests/coverage_html/"
fi

echo ""
echo "🎉 Execução de testes concluída!"

# Makefile para facilitar comandos do projeto

.PHONY: help install run test clean docs lint format

# Configurações
PYTHON := python3
PIP := pip
VENV := venv
PORT := 8000

help: ## Mostra esta mensagem de ajuda
	@echo "Comandos disponíveis:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Instala as dependências do projeto
	$(PIP) install -r requirements.txt

run: ## Executa o servidor de desenvolvimento
	uvicorn main:app --host 0.0.0.0 --port $(PORT) --reload

test: ## Executa todos os testes
	./run_tests.sh

test-unit: ## Executa apenas testes unitários
	pytest tests/test_models.py tests/test_sectors.py tests/test_services.py -v

test-api: ## Executa apenas testes de API
	pytest tests/test_api.py -v

test-integration: ## Executa apenas testes de integração
	pytest tests/test_integration.py -v

lint: ## Executa linting do código
	flake8 app/ main.py --max-line-length=100 --ignore=E203,W503
	black app/ main.py --check

format: ## Formata o código
	black app/ main.py
	isort app/ main.py

clean: ## Remove arquivos temporários
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf logs/tests/

docs: ## Abre a documentação da API
	@echo "Documentação disponível em:"
	@echo "  Swagger UI: http://localhost:$(PORT)/docs"
	@echo "  ReDoc: http://localhost:$(PORT)/redoc"

setup-dev: ## Configura ambiente de desenvolvimento
	$(PIP) install -r requirements.txt
	pre-commit install || echo "pre-commit não instalado"

update-data: ## Atualiza dados das ações (apenas se servidor estiver rodando)
	curl -X POST http://localhost:$(PORT)/api/v1/data/update-stocks

calculate-rankings: ## Calcula rankings (apenas se servidor estiver rodando)
	curl -X POST http://localhost:$(PORT)/api/v1/data/calculate-rankings

health-check: ## Verifica se a API está funcionando
	curl http://localhost:$(PORT)/health

backup-db: ## Faz backup do banco de dados
	cp data/fundamental_analysis.db data/backup_$(shell date +%Y%m%d_%H%M%S).db || echo "Banco não encontrado"

docker-build: ## Constrói imagem Docker
	docker build -t fundamental-analysis-api .

docker-run: ## Executa container Docker
	docker run -p $(PORT):$(PORT) fundamental-analysis-api

quick-start: install ## Início rápido: instala dependências e executa
	@echo "🚀 Iniciando Fundamental Analysis API..."
	@echo "📚 Documentação estará disponível em: http://localhost:$(PORT)/docs"
	$(MAKE) run

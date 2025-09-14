# Fundamental Analysis API

## Visão Geral

A **Fundamental Analysis API** é um sistema robusto para análise fundamentalista do mercado de ações brasileiro. A API oferece análise setorial especializada, rankings automáticos e integração com dados do fundamentus.

### 🚀 Características Principais

- **Análise Setorial Específica**: Cada setor possui sua própria metodologia de análise com pesos específicos
- **Magic Formula**: Implementação do algoritmo do livro "O Pequeno Livro que Ganhou do Mercado"
- **Dados Atualizados**: Integração automática com a biblioteca fundamentus
- **API RESTful**: Interface completa com documentação automática
- **Base de Dados Local**: SQLite para desenvolvimento, facilmente escalável

## 📊 Metodologia de Análise

### Setores Suportados

A API categoriza as ações em 9 categorias principais, cada uma com sua metodologia específica:

#### 1. **Financeiro**
- Intermediários Financeiros (Bancos)
- Previdência e Seguros  
- Serviços Financeiros Diversos
- Holdings Diversificadas

**Foco**: ROE, P/B, eficiência operacional

#### 2. **Utilities**
- Energia Elétrica
- Água e Saneamento
- Gás

**Foco**: Dividend yield, estabilidade, debt management

#### 3. **Consumo Cíclico**
- Construção Civil, Comércio, Automóveis, etc.

**Foco**: Eficiência de capital, margens operacionais

#### 4. **Consumo Não Cíclico**
- Alimentos, Bebidas, Produtos de uso pessoal

**Foco**: Força da marca, ROIC consistente

#### 5. **Materiais Básicos**
- Mineração, Siderurgia, Químicos, etc.

**Foco**: Earnings yield, eficiência de ciclo de commodities

#### 6. **Bens Industriais**
- Máquinas e Equipamentos, Transporte, etc.

**Foco**: ROIC, alavancagem operacional

#### 7. **Saúde**
- Serviços médicos, Medicamentos

**Foco**: Qualidade de serviço, crescimento demográfico

#### 8. **Tecnologia e Telecomunicações**
- Software, Telecomunicações, Equipamentos

**Foco**: Crescimento, escalabilidade, inovação

#### 9. **Outros**
- Setores diversos

### Sistema de Scoring

Cada ação recebe scores de 0-100 em diferentes categorias:

- **Earnings Yield Score**: Baseado em EBIT/EV
- **Return on Capital Score**: Baseado em ROIC
- **Value Score**: P/E, P/B, P/S
- **Quality Score**: Margens, liquidez, ROE
- **Growth Score**: Crescimento de receita
- **Dividend Score**: Dividend yield

O **Final Score** é uma média ponderada específica de cada setor.

## 🛠 Instalação e Configuração

### Pré-requisitos

- Python 3.9+
- pip

### Instalação

```bash
# Clone o repositório
git clone <repository-url>
cd fundamental_analysis

# Instale as dependências
pip install -r requirements.txt

# Configure as variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env conforme necessário

# Execute a aplicação
python main.py
```

### Configuração

Edite o arquivo `.env`:

```env
DATABASE_URL=sqlite:///./fundamental_analysis.db
SECRET_KEY=your-secret-key-here
DEBUG=True
LOG_LEVEL=INFO
API_V1_STR=/api/v1
PROJECT_NAME=Fundamental Analysis API
VERSION=1.0.0
FUNDAMENTUS_CACHE_HOURS=24
UPDATE_ON_STARTUP=False
```

## 📡 Endpoints da API

### Atualização de Dados

#### `POST /api/v1/data/update`
Atualiza os dados financeiros

```json
{
  "update_type": "full",  // "full", "incremental", "rankings"
  "force_update": false
}
```

#### `GET /api/v1/data/update/status`
Verifica o status da última atualização

#### `GET /api/v1/data/update/history`
Histórico de atualizações

### Setores

#### `GET /api/v1/sectors/`
Lista todos os setores

**Parâmetros:**
- `category`: Filtrar por categoria (opcional)

#### `GET /api/v1/sectors/{sector_id}`
Detalhes de um setor específico

#### `GET /api/v1/sectors/{sector_id}/stocks`
Ações de um setor específico

**Parâmetros:**
- `page`: Página (padrão: 1)
- `size`: Tamanho da página (padrão: 20)
- `active_only`: Apenas ações ativas (padrão: true)

### Rankings

#### `GET /api/v1/rankings/sector/{sector_id}`
Top N ações de um setor

**Parâmetros:**
- `limit`: Número de ações (padrão: 10, máx: 100)

#### `GET /api/v1/rankings/sector/{sector_id}/by-score`
Ações ordenadas por tipo de score específico

**Parâmetros:**
- `score_type`: Tipo de score (final_score, earnings_yield_score, etc.)
- `limit`: Número de ações

#### `GET /api/v1/rankings/all-sectors`
Top N ações para cada setor

**Parâmetros:**
- `limit_per_sector`: Ações por setor (padrão: 5, máx: 20)

#### `GET /api/v1/rankings/magic-formula`
Top ações pela Magic Formula

**Parâmetros:**
- `limit`: Número de ações (padrão: 20, máx: 100)

#### `GET /api/v1/rankings/search`
Busca ações com filtros

**Parâmetros:**
- `symbol`: Símbolo da ação
- `sector_name`: Nome do setor
- `min_score`: Score mínimo

## 📈 Exemplos de Uso

### Obter Top 10 Bancos

```bash
curl "http://localhost:8000/api/v1/rankings/sector/1?limit=10"
```

### Atualizar Dados

```bash
curl -X POST "http://localhost:8000/api/v1/data/update" \
  -H "Content-Type: application/json" \
  -d '{"update_type": "full"}'
```

### Magic Formula Top 20

```bash
curl "http://localhost:8000/api/v1/rankings/magic-formula?limit=20"
```

### Buscar Ações

```bash
curl "http://localhost:8000/api/v1/rankings/search?symbol=PETR&min_score=50"
```

## 🏗 Arquitetura

```
fundamental_analysis/
├── app/
│   ├── api/          # Endpoints FastAPI
│   ├── database/     # Configuração do banco
│   ├── models/       # Modelos SQLAlchemy e Pydantic
│   ├── sectors/      # Classes de análise setorial
│   └── services/     # Lógica de negócio
├── config/           # Configurações
├── docs/            # Documentação
├── tests/           # Testes
└── main.py          # Aplicação principal
```

### Padrões Utilizados

- **Repository Pattern**: Separação de dados e lógica
- **Factory Pattern**: Criação de analisadores setoriais
- **Service Layer**: Lógica de negócio centralizada
- **Dependency Injection**: Injeção de dependências via FastAPI

## 🧪 Testes

```bash
# Executar todos os testes
pytest

# Executar com cobertura
pytest --cov=app

# Testes específicos
pytest tests/test_sectors.py
```

## 📊 Monitoramento

### Health Check

```bash
curl "http://localhost:8000/health"
```

### Métricas da API

A API fornece informações sobre:
- Status do banco de dados
- Número de setores e ações
- Última atualização
- Performance dos endpoints

## 🔧 Desenvolvimento

### Adicionando Novos Setores

1. Crie uma nova classe em `app/sectors/`
2. Herde de `BaseSectorAnalyzer`
3. Implemente os métodos abstratos
4. Registre no `SectorAnalyzerFactory`

### Customizando Scores

Cada setor pode ter:
- Pesos diferentes para cada métrica
- Métricas excluídas
- Métricas customizadas específicas

### Estrutura de Banco

- **Sectors**: Setores e categorias
- **Stocks**: Ações e indicadores
- **SectorRankings**: Rankings específicos
- **DataUpdateLogs**: Log de atualizações

## 🚀 Deploy

### Docker (Recomendado)

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "main.py"]
```

### Variáveis de Ambiente para Produção

```env
DEBUG=False
DATABASE_URL=postgresql://user:pass@host:port/db
LOG_LEVEL=WARNING
SECRET_KEY=your-production-secret
```

## 📝 Licença

MIT License

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📞 Suporte

Para suporte e dúvidas:
- Abra uma issue no GitHub
- Consulte a documentação automática em `/docs`
- Verifique os logs da aplicação

---

**Fundamental Analysis API** - Análise fundamentalista inteligente para o mercado brasileiro 🇧🇷

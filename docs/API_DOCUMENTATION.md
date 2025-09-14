# API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
Currently, no authentication is required. Future versions may include API key authentication.

## Response Format

All API responses follow this standard format:

```json
{
  "success": true,
  "message": "Description of the operation",
  "data": {}, // Response data
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## Error Handling

Error responses include:
- HTTP status codes (400, 404, 500, etc.)
- Error messages in the response body
- Detailed error information when in debug mode

Example error response:
```json
{
  "detail": "Sector not found"
}
```

## Rate Limiting

Currently no rate limiting is implemented. Consider implementing rate limiting for production use.

## Data Update Endpoints

### Update Data
**POST** `/api/v1/data/update`

Trigger a data update from fundamentus.

**Request Body:**
```json
{
  "update_type": "full",  // "full", "incremental", "rankings"
  "force_update": false   // optional, default: false
}
```

**Response:**
```json
{
  "success": true,
  "message": "Full data update started in background",
  "data": {
    "update_type": "full",
    "status": "started"
  }
}
```

### Get Update Status
**GET** `/api/v1/data/update/status`

Get the status of the latest data update.

**Response:**
```json
{
  "success": true,
  "message": "Update status retrieved successfully",
  "data": {
    "update_id": 1,
    "update_type": "full",
    "status": "completed",
    "stocks_processed": 450,
    "sectors_processed": 25,
    "start_time": "2024-01-01T10:00:00Z",
    "end_time": "2024-01-01T10:15:00Z",
    "duration_seconds": 900,
    "error_message": null
  }
}
```

### Get Update History
**GET** `/api/v1/data/update/history?limit=10`

Get history of recent data updates.

**Query Parameters:**
- `limit` (optional): Number of records to return (default: 10)

## Sector Endpoints

### Get All Sectors
**GET** `/api/v1/sectors/`

Get all available sectors, optionally filtered by category.

**Query Parameters:**
- `category` (optional): Filter by sector category

**Response:**
```json
{
  "success": true,
  "message": "Retrieved 25 sectors",
  "data": {
    "Financeiro": [
      {
        "id": 1,
        "name": "Intermediários Financeiros",
        "category": "Financeiro",
        "subsectors": ["Bancos"],
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
      }
    ]
  }
}
```

### Get Sector Categories
**GET** `/api/v1/sectors/categories`

Get all sector categories with counts.

**Response:**
```json
{
  "success": true,
  "message": "Retrieved 9 categories",
  "data": {
    "categories": ["Financeiro", "Utilities", "Consumo Cíclico"],
    "counts": {
      "Financeiro": 4,
      "Utilities": 3,
      "Consumo Cíclico": 10
    }
  }
}
```

### Get Specific Sector
**GET** `/api/v1/sectors/{sector_id}`

Get details of a specific sector.

**Path Parameters:**
- `sector_id`: Sector ID

**Response:**
```json
{
  "success": true,
  "message": "Sector retrieved successfully",
  "data": {
    "id": 1,
    "name": "Intermediários Financeiros",
    "category": "Financeiro",
    "subsectors": ["Bancos"],
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "stock_count": 15
  }
}
```

### Get Sector Stocks
**GET** `/api/v1/sectors/{sector_id}/stocks`

Get stocks in a specific sector with pagination.

**Path Parameters:**
- `sector_id`: Sector ID

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `size` (optional): Page size (default: 20, max: 100)
- `active_only` (optional): Show only active stocks (default: true)

**Response:**
```json
{
  "success": true,
  "message": "Retrieved 20 stocks from sector Bancos",
  "data": {
    "sector": {
      "id": 1,
      "name": "Intermediários Financeiros",
      "category": "Financeiro"
    },
    "stocks": [
      {
        "id": 1,
        "symbol": "ITUB4",
        "company_name": "Itaú Unibanco",
        "subsector": "Bancos",
        "sector_rank": 1,
        "magic_formula_rank": 45,
        "cotacao": 32.50,
        "pl": 8.5,
        "pvp": 1.2,
        "div_yield": 6.5,
        "roic": 18.5,
        "roe": 22.0,
        "is_active": true,
        "last_updated": "2024-01-01T10:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "size": 20,
      "total": 15,
      "pages": 1,
      "has_next": false,
      "has_prev": false
    }
  }
}
```

## Ranking Endpoints

### Get Top Stocks by Sector
**GET** `/api/v1/rankings/sector/{sector_id}`

Get top N stocks for a specific sector.

**Path Parameters:**
- `sector_id`: Sector ID

**Query Parameters:**
- `limit` (optional): Number of stocks to return (default: 10, max: 100)

**Response:**
```json
{
  "success": true,
  "message": "Retrieved top 10 stocks for sector Bancos",
  "data": {
    "sector": {
      "id": 1,
      "name": "Intermediários Financeiros",
      "category": "Financeiro"
    },
    "stocks": [
      {
        "rank_position": 1,
        "stock_id": 1,
        "symbol": "ITUB4",
        "company_name": "Itaú Unibanco",
        "subsector": "Bancos",
        "scores": {
          "earnings_yield_score": 85.5,
          "return_on_capital_score": 92.3,
          "value_score": 78.1,
          "quality_score": 88.7,
          "growth_score": 45.2,
          "dividend_score": 82.5,
          "final_score": 85.3
        },
        "key_metrics": {
          "cotacao": 32.50,
          "pl": 8.5,
          "pvp": 1.2,
          "div_yield": 6.5,
          "roic": 18.5,
          "roe": 22.0,
          "ev_ebit": 7.2,
          "ev_ebitda": null
        },
        "calculation_date": "2024-01-01T10:00:00Z"
      }
    ]
  }
}
```

### Get Stocks by Score Type
**GET** `/api/v1/rankings/sector/{sector_id}/by-score`

Get stocks ranked by a specific score type.

**Path Parameters:**
- `sector_id`: Sector ID

**Query Parameters:**
- `score_type`: Score type to rank by
  - `final_score` (default)
  - `earnings_yield_score`
  - `return_on_capital_score`
  - `value_score`
  - `quality_score`
  - `growth_score`
  - `dividend_score`
- `limit` (optional): Number of stocks (default: 10, max: 100)

### Get Top Stocks All Sectors
**GET** `/api/v1/rankings/all-sectors`

Get top N stocks for each sector.

**Query Parameters:**
- `limit_per_sector` (optional): Stocks per sector (default: 5, max: 20)

**Response:**
```json
{
  "success": true,
  "message": "Retrieved top stocks for 9 sectors (45 total stocks)",
  "data": {
    "Intermediários Financeiros": {
      "sector_id": 1,
      "stocks": [
        {
          "rank_position": 1,
          "symbol": "ITUB4",
          "company_name": "Itaú Unibanco",
          "final_score": 85.3,
          "key_metrics": {
            "cotacao": 32.50,
            "pl": 8.5,
            "roic": 18.5,
            "div_yield": 6.5
          }
        }
      ]
    }
  }
}
```

### Get Magic Formula Stocks
**GET** `/api/v1/rankings/magic-formula`

Get top stocks by Magic Formula ranking.

**Query Parameters:**
- `limit` (optional): Number of stocks (default: 20, max: 100)

**Response:**
```json
{
  "success": true,
  "message": "Retrieved top 20 Magic Formula stocks",
  "data": {
    "methodology": "Magic Formula combines Earnings Yield (EBIT/EV) and Return on Capital (ROIC)",
    "stocks": [
      {
        "magic_formula_rank": 1,
        "symbol": "WEGE3",
        "company_name": "WEG S.A.",
        "sector_name": "Máquinas e Equipamentos",
        "key_metrics": {
          "cotacao": 45.30,
          "earnings_yield": 12.5,
          "roic": 25.8,
          "pl": 18.2,
          "pvp": 4.5,
          "ev_ebit": 8.0,
          "div_yield": 2.1
        },
        "last_updated": "2024-01-01T10:00:00Z"
      }
    ]
  }
}
```

### Search Stock Rankings
**GET** `/api/v1/rankings/search`

Search stock rankings with various filters.

**Query Parameters:**
- `symbol` (optional): Stock symbol to search
- `sector_name` (optional): Sector name to filter
- `min_score` (optional): Minimum final score (0-100)

**Response:**
```json
{
  "success": true,
  "message": "Found 5 matching stocks",
  "data": [
    {
      "symbol": "PETR4",
      "company_name": "Petróleo Brasileiro S.A.",
      "sector": {
        "id": 5,
        "name": "Petróleo, Gás e Biocombustíveis",
        "category": "Materiais Básicos"
      },
      "rank_position": 2,
      "final_score": 78.5,
      "key_metrics": {
        "cotacao": 35.20,
        "pl": 4.2,
        "roic": 15.5,
        "div_yield": 12.5
      }
    }
  ]
}
```

## Status Codes

- `200 OK`: Successful request
- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

## Pagination

For endpoints that support pagination:

```json
{
  "pagination": {
    "page": 1,
    "size": 20,
    "total": 150,
    "pages": 8,
    "has_next": true,
    "has_prev": false
  }
}
```

## Data Freshness

- Stock data is updated from fundamentus on demand
- Rankings are calculated after data updates
- Check `/api/v1/data/update/status` for last update time
- Data older than 24 hours may trigger automatic updates

## Performance Tips

- Use pagination for large result sets
- Cache frequently accessed data
- Use specific sector queries instead of all-sectors when possible
- Monitor update status before making data-dependent requests

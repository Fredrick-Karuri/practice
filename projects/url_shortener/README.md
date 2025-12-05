# URL Shortener

A production-ready URL shortening service with analytics, caching, and a modern React frontend.

**Live Demo:** [url-shortener-us.vercel.app](https://url-shortener-us.vercel.app/)


## Architecture Overview

```
┌─────────────┐      ┌─────────────┐      ┌──────────────┐
│   React     │─────▶│   FastAPI   │─────▶│  PostgreSQL  │
│  Frontend   │      │   Backend   │      │   Database   │
└─────────────┘      └──────┬──────┘      └──────────────┘
                            │
                            ▼
                     ┌─────────────┐
                     │    Redis    │
                     │    Cache    │
                     └─────────────┘
```

## Features

- **URL Shortening**: Base62 encoding for compact URLs
- **Analytics**: Click tracking, referrer data, timestamps
- **Caching**: Redis-based caching for high-performance reads
- **Database Migrations**: Alembic for version-controlled schema changes
- **Testing**: Comprehensive test coverage with pytest
- **Containerization**: Docker setup for easy deployment

## Tech Stack

### Backend
- **Framework**: FastAPI (async Python web framework)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Cache**: Redis for distributed caching
- **Migrations**: Alembic
- **Testing**: pytest with test fixtures

### Frontend
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: CSS Modules

## Project Structure

```
url_shortener/
├── backend/
│   ├── api/              # API routes and models
│   ├── models/           # Database models
│   ├── repository/       # Data access layer
│   ├── services/         # Business logic
│   ├── utils/            # Helper functions (Base62, etc.)
│   ├── tests/            # Test suite
│   ├── alembic/          # Database migrations
│   └── main.py           # Application entry point
├── frontend/
│   └── src/
│       ├── components/   # React components
│       ├── api/          # API client
│       └── App.tsx       # Main application
└── pytest.ini            # Test configuration
```

## Key Implementation Details

### Base62 Encoding
Custom implementation for converting database IDs to short codes:
- Compact URL representation
- Case-sensitive encoding (0-9, a-z, A-Z)
- Reversible for efficient lookups

### Caching Strategy
Multi-layer caching approach:
- **Redis**: Distributed cache for URL mappings
- **Cache Invalidation**: Automatic on URL updates
- **TTL Management**: Configurable expiration

### Database Schema
```sql
urls (
  id BIGSERIAL PRIMARY KEY,
  original_url TEXT NOT NULL,
  short_code VARCHAR(10) UNIQUE,
  created_at TIMESTAMP,
  expires_at TIMESTAMP
)

url_stats (
  id BIGSERIAL PRIMARY KEY,
  url_id BIGINT REFERENCES urls(id),
  clicks INTEGER DEFAULT 0,
  last_accessed TIMESTAMP
)
```

## Running Locally

### Prerequisites
- Python 3.9+
- Node.js 16+
- PostgreSQL
- Redis

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Docker Setup
```bash
docker-compose up -d
```

## Testing

```bash
cd backend
pip install -r requirements-test.txt
pytest tests/ -v
```

Test coverage includes:
- URL repository operations
- Service layer business logic
- Cache integration
- Base62 encoding/decoding

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/shorten` | Create shortened URL |
| GET | `/{short_code}` | Redirect to original URL |
| GET | `/stats/{short_code}` | Get URL analytics |
| DELETE | `/{short_code}` | Delete shortened URL |

## Performance Considerations

- **Redis Caching**: 10x faster reads for popular URLs
- **Database Indexing**: Optimized queries on short_code
- **Async Operations**: Non-blocking I/O with FastAPI
- **Connection Pooling**: Efficient database connections

## Future Enhancements

- [ ] Custom short codes
- [ ] Rate limiting
- [ ] User authentication
- [ ] Bulk URL shortening
- [ ] Analytics dashboard
- [ ] Geographic tracking

## Learning Outcomes

This project demonstrates:
- Full-stack development with modern tools
- Database design and optimization
- Caching strategies for scalability
- API design and documentation
- Test-driven development
- Containerization and deployment

---

**Related System Design**: [Caching Strategies](../../caching&scaling/01-caching-strategies.md)
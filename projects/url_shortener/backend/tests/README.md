# Test Suite

## Setup

```bash
pip install -r requirements-test.txt
```

## Run All Tests

```bash
pytest
```

## Run Specific Test Categories

```bash
# Unit tests only
pytest tests/test_url_service.py tests/test_repository.py -v

# Integration tests only
pytest tests/test_integration.py -v
```

## Run with Coverage

```bash
pytest --cov=backend --cov-report=html
open htmlcov/index.html
```

## Test Structure

```
tests/
├── test_url_service.py      # Service layer unit tests (mocked)
├── test_repository.py        # Repository tests (in-memory DB)
└── test_integration.py       # Full API integration tests
```

## What's Tested

**Unit Tests (Service)**
- URL shortening logic
- Custom code validation
- Cache hit/miss scenarios
- Error handling

**Unit Tests (Repository)**
- Database CRUD operations
- Query accuracy
- Stats tracking

**Integration Tests**
- Full API endpoints
- End-to-end flows
- Error responses
- Edge cases

## Quick Test

```bash
# Fastest: Unit tests only
pytest tests/test_url_service.py -v

# Most comprehensive: All tests with coverage
pytest --cov=backend --cov-report=term-missing
```
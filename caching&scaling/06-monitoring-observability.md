# Monitoring & Observability

**Golden Rule:** You can't improve what you don't measure.

---

## Key Metrics (The Four Golden Signals)

### 1. Latency
How long requests take to complete.

**Metrics to track:**
- **p50 (median):** 50% of requests complete in this time
- **p95:** 95% of requests (filters out outliers)
- **p99:** 99% of requests (catches tail latency)

**Example:**
```
p50: 100ms  ← Most requests are fast
p95: 500ms  ← Some are slower
p99: 2000ms ← Few outliers are very slow
```

**Alert threshold:** p99 > 1 second

---

### 2. Traffic
Request volume over time.

**Metrics:**
- Requests per second (RPS)
- Requests per minute (RPM)
- Bandwidth usage

**Alert thresholds:**
- Traffic spike > 300% normal (possible DDoS)
- Traffic drop > 50% normal (possible outage)

---

### 3. Errors
Failed requests as percentage of total.

**Metrics:**
- **4xx errors:** Client errors (bad requests)
- **5xx errors:** Server errors (your bugs)
- Error rate percentage

**Alert threshold:** Error rate > 1%

---

### 4. Saturation
How "full" your service is.

**Metrics:**
- CPU utilization (target: < 70%)
- Memory usage (target: < 80%)
- Disk I/O usage
- Database connection pool usage
- Queue depth

**Alert thresholds:**
- CPU > 80%
- Memory > 90%
- Disk > 85%

---

## Implementation

### Application Metrics

```python
from prometheus_client import Counter, Histogram, Gauge
import time

# Define metrics
request_count = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
request_duration = Histogram('http_request_duration_seconds', 'HTTP request latency', ['endpoint'])
active_users = Gauge('active_users', 'Currently active users')

@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    # Record request
    request_count.labels(
        method=request.method,
        endpoint=request.endpoint,
        status=response.status_code
    ).inc()
    
    # Record duration
    duration = time.time() - request.start_time
    request_duration.labels(endpoint=request.endpoint).observe(duration)
    
    return response

@app.route('/metrics')
def metrics():
    """Prometheus scrapes this endpoint"""
    return generate_latest()
```

---

### Database Metrics

```python
import psycopg2
from prometheus_client import Gauge

db_connections = Gauge('db_connections_active', 'Active database connections')
db_query_duration = Histogram('db_query_duration_seconds', 'Database query duration', ['query_type'])

def execute_query(query):
    """Instrumented database query"""
    start = time.time()
    
    try:
        with db.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
            
        # Record successful query
        duration = time.time() - start
        db_query_duration.labels(query_type='select').observe(duration)
        
        return result
    except Exception as e:
        # Record error
        db_errors.labels(error_type=type(e).__name__).inc()
        raise

# Monitor connection pool
def update_connection_pool_metrics():
    db_connections.set(db.pool.size - db.pool.available)
```

---

### Cache Metrics

```python
cache_hits = Counter('cache_hits_total', 'Cache hits', ['cache_type'])
cache_misses = Counter('cache_misses_total', 'Cache misses', ['cache_type'])

def get_from_cache(key):
    """Instrumented cache get"""
    value = redis_client.get(key)
    
    if value:
        cache_hits.labels(cache_type='redis').inc()
    else:
        cache_misses.labels(cache_type='redis').inc()
    
    return value

# Calculate hit rate
def get_cache_hit_rate():
    hits = redis_client.info('stats')['keyspace_hits']
    misses = redis_client.info('stats')['keyspace_misses']
    
    if hits + misses == 0:
        return 0
    
    hit_rate = hits / (hits + misses)
    return hit_rate * 100  # Percentage
```

**Target:** > 80% hit rate for hot data

---

## Logging

### Structured Logging

**Bad:**
```python
print(f"User {user_id} logged in from {ip_address}")
# Hard to parse and search
```

**Good:**
```python
import logging
import json

logger = logging.getLogger(__name__)

logger.info("user_login", extra={
    "user_id": user_id,
    "ip_address": ip_address,
    "timestamp": datetime.now().isoformat(),
    "user_agent": request.headers.get('User-Agent')
})

# Output (JSON):
# {"level": "info", "event": "user_login", "user_id": 123, "ip_address": "1.2.3.4", ...}
```

**Benefits:**
- Easy to search: `user_id:123`
- Easy to aggregate: Count logins per IP
- Machine-readable

---

### Log Levels

```python
logger.debug("Cache key: user:123")        # Development only
logger.info("User logged in")               # Normal operations
logger.warning("Cache hit rate below 50%")  # Potential issues
logger.error("Database connection failed")  # Definite problems
logger.critical("Payment gateway down")     # System failure
```

**Production:** Only log INFO and above (too many DEBUG logs)

---

### Centralized Logging

```python
import logging
from pythonjsonlogger import jsonlogger

# Configure JSON logging
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)

# All logs go to stdout → collected by logging agent (Fluentd, Logstash)
logger.info("request_completed", extra={
    "request_id": "abc123",
    "duration_ms": 245,
    "status_code": 200,
    "user_id": 789
})
```

**Flow:**
```
Application → stdout → Log aggregator → Elasticsearch → Kibana
```

---

## Distributed Tracing

Track requests across microservices.

```python
from opentelemetry import trace
from opentelemetry.instrumentation.requests import RequestsInstrumentor

tracer = trace.get_tracer(__name__)

@app.route('/api/order')
def create_order():
    with tracer.start_as_current_span("create_order") as span:
        # Add context
        span.set_attribute("user_id", user_id)
        span.set_attribute("order_total", 99.99)
        
        # Call other services
        with tracer.start_as_current_span("check_inventory"):
            inventory = check_inventory_service(product_id)
        
        with tracer.start_as_current_span("process_payment"):
            payment = process_payment_service(amount)
        
        with tracer.start_as_current_span("send_confirmation"):
            send_email_service(user_email)
        
        return {"order_id": order_id}
```

**Visualization:**
```
create_order [1200ms]
├── check_inventory [300ms]
├── process_payment [800ms] ← SLOW!
└── send_confirmation [100ms]
```

**Identifies bottlenecks** across distributed systems.

---

## Alerting

### Alert Fatigue Prevention

**Bad alerts:**
- Too sensitive (fires constantly)
- Not actionable ("something is wrong")
- Alerts on symptoms, not causes

**Good alerts:**
- Clear threshold: "p99 latency > 1s for 5 minutes"
- Actionable: Includes runbook link
- Grouped: Multiple related alerts → single notification

---

### Alert Rules

```python
# Prometheus alert rules
groups:
  - name: api_alerts
    rules:
      # High error rate
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.01
        for: 5m
        annotations:
          summary: "Error rate above 1%"
          description: "{{ $value }}% of requests failing"
          runbook: "https://wiki.example.com/runbooks/high-error-rate"
      
      # Slow responses
      - alert: SlowResponses
        expr: histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m])) > 1
        for: 5m
        annotations:
          summary: "p99 latency above 1 second"
          runbook: "https://wiki.example.com/runbooks/slow-api"
      
      # Low cache hit rate
      - alert: LowCacheHitRate
        expr: (cache_hits_total / (cache_hits_total + cache_misses_total)) < 0.8
        for: 10m
        annotations:
          summary: "Cache hit rate below 80%"
          runbook: "https://wiki.example.com/runbooks/cache-tuning"
      
      # Queue backing up
      - alert: QueueBacklog
        expr: queue_depth > 10000
        for: 5m
        annotations:
          summary: "Queue has {{ $value }} pending jobs"
          runbook: "https://wiki.example.com/runbooks/queue-backlog"
```

---

### On-Call Runbooks

Each alert should link to a runbook:

**Example: High Error Rate Runbook**

```markdown
# High Error Rate

## Symptoms
- 5xx error rate above 1%
- Users reporting "service unavailable"

## Diagnosis
1. Check error logs: `tail -f /var/log/app.log | grep ERROR`
2. Check database status: `systemctl status postgresql`
3. Check Redis: `redis-cli ping`
4. Check disk space: `df -h`

## Resolution
- Database down → Restart: `systemctl restart postgresql`
- Redis down → Restart: `systemctl restart redis`
- Disk full → Clear old logs: `journalctl --vacuum-time=7d`
- Code bug → Rollback deployment

## Escalation
If unresolved in 15 minutes, escalate to:
- @tech-lead (Slack)
- engineering@example.com
```

---

## Dashboard Examples

### System Health Dashboard

```python
# Grafana dashboard config (JSON)
{
  "dashboard": {
    "title": "System Health",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [{"expr": "rate(http_requests_total[5m])"}],
        "type": "graph"
      },
      {
        "title": "Error Rate",
        "targets": [{"expr": "rate(http_requests_total{status=~\"5..\"}[5m])"}],
        "type": "graph",
        "alert": {"threshold": 0.01}
      },
      {
        "title": "Latency (p50, p95, p99)",
        "targets": [
          {"expr": "histogram_quantile(0.50, rate(http_request_duration_seconds_bucket[5m]))"},
          {"expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))"},
          {"expr": "histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))"}
        ],
        "type": "graph"
      },
      {
        "title": "Cache Hit Rate",
        "targets": [{"expr": "cache_hits_total / (cache_hits_total + cache_misses_total)"}],
        "type": "gauge"
      }
    ]
  }
}
```

---

### Database Dashboard

**Key Metrics:**
- Active connections vs pool size
- Query duration (p50, p95, p99)
- Slow query count (> 1 second)
- Deadlock count
- Replication lag (for replicas)

---

### Application Dashboard

**Key Metrics:**
- Requests per second
- Response time by endpoint
- Error rate by endpoint
- Active users
- Queue depth

---

## Tools

### Application Monitoring

**New Relic**
- Full-stack observability
- Auto-instrumentation
- Transaction tracing
- Cost: ~$100-500/month

**Datadog**
- Infrastructure + APM
- Log aggregation
- Custom dashboards
- Cost: ~$15-50/host/month

**Prometheus + Grafana (Open Source)**
- Self-hosted
- Highly customizable
- Cost: Infrastructure only (~$50-200/month)

---

### Log Management

**ELK Stack (Elasticsearch, Logstash, Kibana)**
- Open source
- Powerful search
- Self-hosted
- Cost: Infrastructure (~$200-1000/month)

**Splunk**
- Enterprise-grade
- Advanced analytics
- Cost: ~$150/GB/month (expensive!)

**CloudWatch Logs (AWS)**
- Managed service
- AWS integration
- Cost: ~$0.50/GB ingested

---

### Tracing

**Jaeger (Open Source)**
- Distributed tracing
- Self-hosted
- OpenTelemetry compatible

**Datadog APM**
- Traces + metrics + logs
- Managed service
- Cost: ~$31/host/month

**AWS X-Ray**
- AWS-native
- Serverless-friendly
- Cost: ~$5/million traces

---

## Performance Profiling

### CPU Profiling

```python
import cProfile
import pstats

def profile_function():
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Code to profile
    result = expensive_operation()
    
    profiler.disable()
    
    # Print stats
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)  # Top 10 functions
    
    return result
```

**Identifies CPU-intensive functions.**

---

### Memory Profiling

```python
import tracemalloc

tracemalloc.start()

# Code to profile
large_data = load_large_dataset()
process_data(large_data)

# Get memory usage
current, peak = tracemalloc.get_traced_memory()
print(f"Current: {current / 1024 / 1024:.2f} MB")
print(f"Peak: {peak / 1024 / 1024:.2f} MB")

tracemalloc.stop()
```

**Identifies memory leaks.**

---

### Query Profiling

```sql
-- PostgreSQL
EXPLAIN ANALYZE SELECT * FROM posts WHERE user_id = 123;

-- Output shows:
-- Seq Scan vs Index Scan
-- Rows examined
-- Actual execution time
```

**Identifies slow queries.**

---

## Slow Query Detection

```python
import time
from functools import wraps

def log_slow_queries(threshold_seconds=1.0):
    """Decorator to log slow database queries"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start
            
            if duration > threshold_seconds:
                logger.warning("slow_query", extra={
                    "query": func.__name__,
                    "duration_seconds": duration,
                    "args": str(args)[:100],  # Truncate for logging
                })
            
            return result
        return wrapper
    return decorator

@log_slow_queries(threshold_seconds=0.5)
def get_user_posts(user_id):
    return db.execute("SELECT * FROM posts WHERE user_id = ?", user_id)
```

---

## Error Tracking

### Sentry Integration

```python
import sentry_sdk

sentry_sdk.init(
    dsn="https://...@sentry.io/...",
    traces_sample_rate=0.1,  # Sample 10% of transactions
    environment="production",
)

@app.route('/api/process')
def process_data():
    try:
        result = process()
        return {"result": result}
    except Exception as e:
        # Auto-reported to Sentry with full context
        sentry_sdk.capture_exception(e)
        
        # Add custom context
        sentry_sdk.set_context("business_data", {
            "user_id": user_id,
            "order_id": order_id,
        })
        
        raise
```

**Benefits:**
- Stack traces
- Breadcrumbs (what led to error)
- User context
- Error grouping
- Release tracking

---

## Real User Monitoring (RUM)

Track performance as users experience it.

```html
<script>
// Measure page load time
window.addEventListener('load', function() {
  const perfData = performance.timing;
  const pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;
  
  // Send to analytics
  fetch('/api/metrics', {
    method: 'POST',
    body: JSON.stringify({
      metric: 'page_load_time',
      value: pageLoadTime,
      page: window.location.pathname
    })
  });
});

// Measure API call duration
async function fetchData() {
  const start = performance.now();
  const response = await fetch('/api/data');
  const duration = performance.now() - start;
  
  // Track API latency from user's perspective
  trackMetric('api_call_duration', duration);
}
</script>
```

---

## Health Check Endpoints

```python
@app.route('/health')
def health_check():
    """Basic health check"""
    return {"status": "healthy"}, 200

@app.route('/health/detailed')
def detailed_health():
    """Detailed health with dependencies"""
    health = {
        "status": "healthy",
        "checks": {}
    }
    
    # Check database
    try:
        db.execute("SELECT 1")
        health["checks"]["database"] = "healthy"
    except Exception as e:
        health["checks"]["database"] = f"unhealthy: {str(e)}"
        health["status"] = "unhealthy"
    
    # Check Redis
    try:
        redis_client.ping()
        health["checks"]["redis"] = "healthy"
    except Exception as e:
        health["checks"]["redis"] = f"unhealthy: {str(e)}"
        health["status"] = "unhealthy"
    
    # Check external API
    try:
        response = requests.get('https://api.partner.com/health', timeout=2)
        response.raise_for_status()
        health["checks"]["partner_api"] = "healthy"
    except Exception as e:
        health["checks"]["partner_api"] = f"unhealthy: {str(e)}"
        health["status"] = "degraded"  # Not critical
    
    status_code = 200 if health["status"] == "healthy" else 503
    return health, status_code
```

---

## SLIs, SLOs, and SLAs

### SLI (Service Level Indicator)
Metric that measures service quality.

**Examples:**
- Request success rate
- Latency (p99)
- Availability

---

### SLO (Service Level Objective)
Target value for SLI.

**Examples:**
- 99.9% of requests succeed (3 nines)
- p99 latency < 500ms
- 99.95% uptime per month

---

### SLA (Service Level Agreement)
Contract with users, penalties if violated.

**Example:**
- Promise 99.9% uptime
- If below 99%, refund 10% of fees
- If below 95%, refund 25% of fees

---

## Rule of Thumb

- **Monitor the four golden signals:** Latency, traffic, errors, saturation
- **Use structured logging** (JSON) for easy searching
- **Set meaningful alerts:** Actionable, not noisy (target: < 5 alerts/week)
- **Target metrics:**
  - p99 latency < 1 second
  - Error rate < 1%
  - Cache hit rate > 80%
  - CPU utilization < 70%
- **Always have runbooks** for common issues
- **Track real user experience** (RUM), not just server metrics
- **Profile before optimizing** - measure, don't guess
# Scaling Architectures

## Vertical Scaling (Scale Up)

Add more resources to a single server:
- More CPU cores
- More RAM
- Faster disk (SSD → NVMe)

### Pros
- Simple (no code changes)
- No distributed system complexity
- No network latency between components
- Easier to debug and monitor

### Cons
- Physical limits (can't add infinite RAM)
- Single point of failure
- Expensive at high end
- Downtime during upgrades

### When to Use
- Early stage (< 10k users)
- Database is bottleneck
- Quick fix needed
- Application isn't easily parallelizable

---

## Horizontal Scaling (Scale Out)

Add more servers:
- Load balancer distributes requests
- Stateless application servers
- Shared database or distributed data

### Pros
- Unlimited scaling potential
- Redundancy (no single point of failure)
- Cost effective (commodity hardware)
- Rolling deployments with zero downtime

### Cons
- Code must be stateless
- Distributed system complexity
- Data consistency challenges
- Network latency between components

### When to Use
- Growing past single server capacity
- Need high availability (99.99%+)
- Long-term scalability required
- Traffic is unpredictable

---

## Stateless Application Design

**Critical for horizontal scaling**

### What Makes an App Stateless?

❌ **Stateful (Bad):**
```python
# Session stored in memory
sessions = {}

@app.route('/login')
def login():
    sessions[user_id] = {"logged_in": True}
    # Problem: Only exists on THIS server
```

✅ **Stateless (Good):**
```python
# Session in Redis (shared across all servers)
@app.route('/login')
def login():
    redis_client.setex(f"session:{user_id}", 3600, json.dumps({"logged_in": True}))
    # Works on ANY server
```

### Rules for Stateless Apps

1. **No in-memory state:** Use Redis/database for session data
2. **No local file storage:** Use S3/CDN for uploads
3. **No server affinity:** Any server can handle any request
4. **Idempotent operations:** Same request = same result
5. **Externalize config:** Use environment variables/config service

---

## Load Balancing Strategies

### Round Robin
Routes requests sequentially across servers

```
Request 1 → Server A
Request 2 → Server B
Request 3 → Server C
Request 4 → Server A (repeat)
```

✅ Simple, fair distribution  
❌ Doesn't account for server load or request complexity

**Use when:** All servers identical, requests similar duration

---

### Least Connections
Routes to server with fewest active connections

✅ Adapts to varying request durations  
✅ Better utilization of resources  
❌ More complex to implement

**Use when:** Requests have variable duration (some fast, some slow)

---

### IP Hash (Sticky Sessions)
Hash user IP → always route to same server

```python
server_index = hash(user_ip) % num_servers
```

✅ Useful for stateful apps (during migration)  
✅ Cache locality (same user hits same server)  
❌ Uneven distribution if users clustered  
❌ Server failure loses sessions

**Use when:** 
- Migrating to stateless architecture
- Local caching benefits (temporary)

**Avoid for:** New systems (use stateless instead)

---

### Weighted Load Balancing
Distribute traffic based on server capacity

```
Server A (8 CPU cores) → 50% traffic
Server B (4 CPU cores) → 30% traffic
Server C (4 CPU cores) → 20% traffic
```

✅ Useful during deployments (gradual rollout)  
✅ Handle heterogeneous hardware  

**Use for:** Canary deployments, A/B testing

---

## Scaling Timeline

### < 10k Users
**Single server (vertical scaling)**
- 1 application server
- 1 database
- No load balancer needed

**Cost:** ~$50-200/month

---

### 10k - 100k Users
**Add caching and read replicas**
- 1 application server (or 2-3 for redundancy)
- Load balancer
- Redis cache
- Database with read replicas
- CDN for static assets

**Cost:** ~$500-1500/month

---

### 100k - 1M Users
**Horizontal scaling**
- 5-10 application servers (auto-scaling)
- Load balancer with health checks
- Redis cluster (primary + replicas)
- Database with multiple read replicas
- CDN + edge caching
- Monitoring and alerting

**Cost:** ~$3k-10k/month

---

### 1M+ Users
**Distributed architecture**
- Auto-scaling (10-100+ servers)
- Multiple availability zones
- Database sharding
- Microservices architecture
- Message queues
- Distributed caching
- Full observability stack

**Cost:** $20k-100k+/month

---

## Health Checks & Auto-Scaling

### Load Balancer Health Checks

```python
@app.route('/health')
def health_check():
    """Called by load balancer every 10s"""
    
    # Check dependencies
    try:
        # Database connection
        db.execute("SELECT 1")
        
        # Redis connection
        redis_client.ping()
        
        return {"status": "healthy"}, 200
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}, 503
```

**Load balancer behavior:**
- Healthy server → receives traffic
- Unhealthy server → removed from pool
- Repeated failures → alert operations team

---

### Auto-Scaling Rules

**Scale up when:**
- CPU utilization > 70% for 5 minutes
- Request queue depth > 100
- Response time p95 > 1 second

**Scale down when:**
- CPU utilization < 30% for 10 minutes
- Minimum 2 servers always running

**Example AWS Auto Scaling config:**
```yaml
min_instances: 2
max_instances: 20
target_cpu: 60%
scale_up: +2 instances when CPU > 70%
scale_down: -1 instance when CPU < 30%
cooldown: 5 minutes
```

---

## Geographic Distribution

### Multi-Region Deployment

**Benefits:**
- Lower latency (users hit nearest region)
- Disaster recovery
- Compliance (data residency laws)

**Challenges:**
- Data synchronization across regions
- Increased cost (duplicate infrastructure)
- Complex deployments

**Pattern:**
```
US East:    Load Balancer → App Servers → Database (Primary)
EU West:    Load Balancer → App Servers → Database (Read Replica)
Asia Pacific: Load Balancer → App Servers → Database (Read Replica)
```

**Route users by:**
- GeoDNS (route to closest region)
- Latency-based routing
- Manual region selection

---

## Deployment Strategies

### Blue-Green Deployment
- Blue: Current production (v1.0)
- Green: New version (v1.1)
- Switch traffic from Blue → Green instantly
- Rollback: Switch back to Blue

✅ Zero downtime  
✅ Easy rollback  
❌ 2x infrastructure cost (temporarily)

---

### Rolling Deployment
- Update servers one-by-one
- 10 servers: Update 2, test, update 2 more...
- Always have healthy servers

✅ No extra infrastructure  
❌ Slower deployment  
❌ Mixed versions running temporarily

---

### Canary Deployment
- Route 5% traffic to new version
- Monitor errors/performance
- Gradually increase to 100%

✅ Catch issues early  
✅ Minimal impact  
❌ Complex to implement

---

## Rule of Thumb

- **Start vertical, scale horizontal:** Vertical is easier initially
- **Stateless is non-negotiable:** Design for horizontal scaling from day 1
- **Monitor before scaling:** Identify actual bottleneck (CPU? DB? Network?)
- **Scale gradually:** Don't jump from 1 to 100 servers
- **Automate everything:** Manual scaling doesn't work at scale
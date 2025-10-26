# Async Processing & Queues

**Key Principle:** Don't make users wait for slow operations.

---

## When to Use Async

Use async for operations taking > 500ms:
- Image/video processing
- Email sending
- PDF generation
- Push notifications
- Analytics/logging
- Feed updates
- Third-party API calls

**Don't use for:** Critical operations users need immediately (payment confirmation, login)

---

## Message Queues

### Architecture

```
┌──────────┐      ┌───────┐      ┌──────────┐
│   API    │─────▶│ Queue │─────▶│  Worker  │
│  Server  │      │       │      │  Process │
└──────────┘      └───────┘      └──────────┘
  Returns 202                    Does actual work
  immediately
```

### Popular Queue Systems

- **RabbitMQ:** Feature-rich, complex
- **AWS SQS:** Simple, managed, pay-per-use
- **Redis (Lists):** Lightweight, good for simple jobs
- **Kafka:** High-throughput, event streaming

---

## Implementation Example

### 1. Image Upload with Queue

```python
from celery import Celery
import boto3

app = Celery('tasks', broker='redis://localhost:6379')

@app.route('/upload', methods=['POST'])
def upload_image():
    """API endpoint - returns immediately"""
    file = request.files['image']
    
    # Save to temp storage
    temp_path = f"/tmp/{file.filename}"
    file.save(temp_path)
    
    # Queue background job
    process_image_task.delay(temp_path)
    
    return {"status": "processing", "job_id": "abc123"}, 202

@app.task
def process_image_task(image_path):
    """Background worker - runs async"""
    # Resize image
    img = Image.open(image_path)
    img.thumbnail((800, 800))
    
    # Upload to S3
    s3 = boto3.client('s3')
    s3.upload_file(image_path, 'my-bucket', 'resized.jpg')
    
    # Update database
    db.execute("UPDATE posts SET image_url = ? WHERE id = ?", url, post_id)
    
    # Notify user (webhook or websocket)
    notify_user(user_id, "Image processed!")
```

---

### 2. Email Sending

```python
@app.route('/register', methods=['POST'])
def register():
    """User registration"""
    user = create_user(request.json)
    
    # Don't wait for email to send!
    send_welcome_email.delay(user.email)
    
    return {"status": "registered"}, 201

@app.task(retry_backoff=True, max_retries=3)
def send_welcome_email(email):
    """Send email in background"""
    try:
        smtp.send(
            to=email,
            subject="Welcome!",
            body="Thanks for signing up"
        )
    except SMTPException:
        # Retry automatically
        raise
```

---

## Queue Patterns

### 1. Single Queue, Multiple Workers

```
      ┌─────────┐
      │  Queue  │
      └────┬────┘
      ┌────┴────┬────────┬────────┐
      ▼         ▼        ▼        ▼
  Worker 1  Worker 2  Worker 3  Worker 4
```

✅ Simple  
✅ Auto-scales (add more workers under load)  
❌ All workers must handle all job types

---

### 2. Multiple Queues by Priority

```
┌──────────────┐     ┌─────────────┐
│ High Priority│────▶│  Fast Worker│
└──────────────┘     └─────────────┘

┌──────────────┐     ┌─────────────┐
│ Low Priority │────▶│  Slow Worker│
└──────────────┘     └─────────────┘
```

**Example:**
- High: Password reset emails
- Low: Marketing emails, analytics

---

### 3. Topic-Based Queues

```
┌─────────────┐     ┌──────────────┐
│ image_queue │────▶│ Image Worker │
└─────────────┘     └──────────────┘

┌─────────────┐     ┌──────────────┐
│ email_queue │────▶│ Email Worker │
└─────────────┘     └──────────────┘

┌─────────────┐     ┌──────────────┐
│ video_queue │────▶│ Video Worker │
└─────────────┘     └──────────────┘
```

✅ Workers specialized for job type  
✅ Scale each queue independently  
❌ More complex infrastructure

---

## Retry Strategies

### Exponential Backoff

```python
@app.task(
    autoretry_for=(Exception,),
    retry_backoff=True,  # Exponential backoff
    retry_backoff_max=600,  # Max 10 minutes
    max_retries=5
)
def call_external_api(data):
    """Retry with exponential backoff"""
    # Attempt 1: immediate
    # Attempt 2: wait 2 seconds
    # Attempt 3: wait 4 seconds
    # Attempt 4: wait 8 seconds
    # Attempt 5: wait 16 seconds
    response = requests.post('https://api.example.com', json=data)
    return response.json()
```

---

### Dead Letter Queue (DLQ)

Jobs that fail repeatedly go to DLQ for manual inspection.

```python
@app.task(max_retries=3)
def risky_task(data):
    try:
        # Attempt processing
        process(data)
    except Exception as e:
        if self.request.retries >= 3:
            # Send to DLQ after 3 failures
            dead_letter_queue.send({
                'task': 'risky_task',
                'data': data,
                'error': str(e),
                'timestamp': datetime.now()
            })
        raise
```

---

## Fan-Out Patterns

### Problem: Notify All Followers

User posts → need to notify 10,000 followers

**Bad:** Loop in API request
```python
@app.route('/post', methods=['POST'])
def create_post():
    post = save_post(request.json)
    
    # This takes 10+ seconds! ❌
    followers = get_followers(user_id)
    for follower in followers:
        send_notification(follower.id, post.id)
    
    return {"status": "created"}
```

---

### Solution 1: Fan-Out on Write (Push Model)

**Pre-compute user feeds when post is created**

```python
@app.route('/post', methods=['POST'])
def create_post():
    post = save_post(request.json)
    
    # Queue single job
    fanout_to_followers.delay(post.id, user_id)
    
    return {"status": "created"}, 201

@app.task
def fanout_to_followers(post_id, author_id):
    """Background: Copy post to all followers' feeds"""
    followers = get_followers(author_id)
    
    for follower in followers:
        # Add to each follower's pre-computed feed
        redis_client.lpush(f"feed:{follower.id}", post_id)
        redis_client.ltrim(f"feed:{follower.id}", 0, 999)  # Keep latest 1000
```

**Read feed (FAST):**
```python
@app.route('/feed')
def get_feed():
    user_id = get_current_user()
    # Just read from Redis - O(1)
    post_ids = redis_client.lrange(f"feed:{user_id}", 0, 49)
    posts = get_posts_by_ids(post_ids)
    return {"posts": posts}
```

✅ Reads are instant  
❌ Writes expensive for popular users  

**Use when:** Most users have < 10k followers

---

### Solution 2: Fan-Out on Read (Pull Model)

**Compute feed when user requests it**

```python
@app.route('/post', methods=['POST'])
def create_post():
    post = save_post(request.json)
    # That's it! No fan-out
    return {"status": "created"}, 201

@app.route('/feed')
def get_feed():
    user_id = get_current_user()
    
    # Fetch on demand
    following = get_following(user_id)
    
    # Get recent posts from each
    all_posts = []
    for user in following:
        posts = get_recent_posts(user.id, limit=10)  # Cached
        all_posts.extend(posts)
    
    # Merge and sort
    all_posts.sort(key=lambda p: p.created_at, reverse=True)
    
    # Cache result
    redis_client.setex(f"feed:{user_id}", 30, json.dumps(all_posts[:50]))
    
    return {"posts": all_posts[:50]}
```

✅ Writes are fast  
❌ Reads require work  

**Use when:** Users follow many people (> 1000)

---

### Solution 3: Hybrid (Twitter/Instagram Approach)

Combine both strategies:

```python
def get_feed_strategy(user_id):
    """Decide strategy per user"""
    follower_count = get_follower_count(user_id)
    
    if follower_count > 10_000:
        return "pull"  # Celebrity - fan-out on read
    else:
        return "push"  # Regular user - fan-out on write

@app.task
def fanout_to_followers(post_id, author_id):
    """Smart fan-out"""
    strategy = get_feed_strategy(author_id)
    
    if strategy == "push":
        # Copy to all followers' feeds
        followers = get_followers(author_id)
        for follower in followers:
            redis_client.lpush(f"feed:{follower.id}", post_id)
    else:
        # Do nothing - will be fetched on read
        pass

@app.route('/feed')
def get_feed():
    user_id = get_current_user()
    following = get_following(user_id)
    
    # Separate into push vs pull users
    push_users = [u for u in following if u.follower_count < 10_000]
    pull_users = [u for u in following if u.follower_count >= 10_000]
    
    # Get pre-computed posts (push users)
    feed_posts = redis_client.lrange(f"feed:{user_id}", 0, 49)
    
    # Fetch celebrity posts on-demand (pull users)
    for celebrity in pull_users:
        recent = get_recent_posts(celebrity.id, limit=10)
        feed_posts.extend(recent)
    
    # Merge and sort
    feed_posts.sort(key=lambda p: p.created_at, reverse=True)
    return {"posts": feed_posts[:50]}
```

**Best of both worlds!**

---

## Webhooks

External service calls your endpoint when event occurs.

### Incoming Webhooks

```python
@app.route('/webhooks/payment', methods=['POST'])
def payment_webhook():
    """Stripe calls this when payment succeeds"""
    payload = request.json
    
    # Verify signature
    verify_webhook_signature(request.headers['Stripe-Signature'])
    
    # Queue processing (don't block webhook response)
    process_payment.delay(payload)
    
    # Respond quickly (< 5 seconds or Stripe retries)
    return {"status": "received"}, 200

@app.task
def process_payment(payload):
    """Process payment in background"""
    payment_id = payload['id']
    
    # Update order status
    db.execute("UPDATE orders SET status = 'paid' WHERE payment_id = ?", payment_id)
    
    # Send confirmation email
    send_email.delay(user_email, "Payment received!")
    
    # Update analytics
    track_event('payment_success', payment_id)
```

---

### Outgoing Webhooks

Notify external services of events in your system.

```python
@app.task(retry_backoff=True, max_retries=5)
def send_webhook(url, event_type, data):
    """Send webhook with retries"""
    payload = {
        "event": event_type,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }
    
    response = requests.post(
        url,
        json=payload,
        headers={"X-Webhook-Signature": generate_signature(payload)},
        timeout=10
    )
    
    response.raise_for_status()  # Retry on failure

# Usage
@app.route('/user/update', methods=['POST'])
def update_user():
    user = update_user_data(request.json)
    
    # Notify subscribers
    send_webhook.delay(
        'https://partner.com/webhooks',
        'user.updated',
        user.to_dict()
    )
    
    return {"status": "updated"}
```

---

## Scheduled Jobs (Cron)

Periodic background tasks.

```python
from celery.schedules import crontab

# Celery Beat scheduler
app.conf.beat_schedule = {
    'cleanup-old-sessions': {
        'task': 'cleanup_sessions',
        'schedule': crontab(hour=2, minute=0),  # 2 AM daily
    },
    'send-digest-emails': {
        'task': 'send_digests',
        'schedule': crontab(hour=9, minute=0, day_of_week=1),  # Monday 9 AM
    },
    'refresh-hot-cache': {
        'task': 'refresh_cache',
        'schedule': 300.0,  # Every 5 minutes
    },
}

@app.task
def cleanup_sessions():
    """Remove expired sessions"""
    cutoff = datetime.now() - timedelta(days=30)
    db.execute("DELETE FROM sessions WHERE updated_at < ?", cutoff)

@app.task
def send_digests():
    """Weekly email digest"""
    users = get_active_users()
    for user in users:
        send_digest_email.delay(user.id)

@app.task
def refresh_cache():
    """Proactively refresh hot data"""
    hot_users = get_popular_users(limit=100)
    for user in hot_users:
        cache_user_profile(user.id)
```

---

## Monitoring Queue Health

```python
@app.route('/queue/stats')
def queue_stats():
    """Monitor queue depth"""
    stats = {
        'pending': redis_client.llen('celery'),
        'failed': redis_client.llen('celery_dlq'),
        'workers': get_active_workers(),
    }
    
    # Alert if queue backing up
    if stats['pending'] > 10000:
        alert_operations("Queue depth critical!")
    
    return stats
```

---

## Rule of Thumb

- Use async for **anything > 500ms**
- **Return immediately** from API (202 Accepted)
- Use **retry with exponential backoff** for external calls
- Implement **dead letter queue** for failed jobs
- **Fan-out on write** for small audiences (< 10k)
- **Fan-out on read** for large audiences (> 10k)
- Use **hybrid approach** for mixed scenarios
- Always **verify webhook signatures**
- Monitor **queue depth** and worker health
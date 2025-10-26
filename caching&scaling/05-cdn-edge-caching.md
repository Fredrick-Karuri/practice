# CDN & Edge Caching

## What is a CDN?

**Content Delivery Network**: Distributed servers that cache content close to users.

```
User in Tokyo → CDN Edge (Tokyo) → Origin Server (US)
               ↑ Cache HIT: 50ms
               ↓ Cache MISS: 300ms
```

---

## How CDN Works

1. User requests `https://cdn.example.com/logo.png`
2. DNS routes to nearest CDN edge location
3. Edge checks: Do I have this cached?
   - **Cache HIT:** Return cached version (FAST - 10-50ms)
   - **Cache MISS:** Fetch from origin, cache it, return (300-1000ms)
4. Subsequent requests served from cache

---

## What to Put on CDN

### ✅ Should Be on CDN

**Static Assets:**
- JavaScript files
- CSS files
- Images (logos, icons, backgrounds)
- Fonts
- Videos

**User-Generated Content:**
- Profile pictures
- Uploaded photos
- Documents (PDFs)

**API Responses (selective):**
- Public data (product catalogs, blog posts)
- Rarely changing data

### ❌ Should NOT Be on CDN

- Personalized content (user dashboard)
- Frequently changing data (live scores)
- Private data (payment info, personal messages)
- Content requiring authentication

---

## Cache-Control Headers

Control how browsers and CDNs cache your content.

### Immutable Static Assets

```python
@app.route('/assets/<path:filename>')
def serve_asset(filename):
    """Static assets that never change"""
    response = send_file(filename)
    
    # Cache forever (versioned URLs)
    response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
    # max-age=31536000 = 1 year
    # immutable = don't revalidate even on refresh
    
    return response

# Use versioned URLs:
# /assets/app.v123.js  ← Version in URL
# /assets/logo.abc456.png
```

**Strategy:** 
- Cache forever
- Change URL when content changes
- Example: `app.v1.js` → `app.v2.js`

---

### Semi-Static Content

```python
@app.route('/blog/<post_id>')
def blog_post(post_id):
    """Content that rarely changes"""
    post = get_blog_post(post_id)
    
    response = jsonify(post)
    response.headers['Cache-Control'] = 'public, max-age=3600'  # 1 hour
    
    return response
```

**Strategy:**
- Cache for reasonable time
- CDN revalidates after expiry

---

### Dynamic/Personalized Content

```python
@app.route('/dashboard')
def dashboard():
    """User-specific data"""
    user_id = get_current_user()
    data = get_user_dashboard(user_id)
    
    response = jsonify(data)
    response.headers['Cache-Control'] = 'private, no-cache'
    # private = only browser can cache (not CDN)
    # no-cache = always revalidate
    
    return response
```

---

### No Caching

```python
@app.route('/api/balance')
def get_balance():
    """Sensitive, real-time data"""
    balance = get_user_balance()
    
    response = jsonify(balance)
    response.headers['Cache-Control'] = 'no-store'
    # no-store = don't cache anywhere
    
    return response
```

---

## Cache-Control Directives

| Directive | Meaning | Use Case |
|-----------|---------|----------|
| `public` | CDN + browser can cache | Static assets, public content |
| `private` | Only browser can cache | Personalized content |
| `max-age=3600` | Cache for 3600 seconds | Semi-static content |
| `s-maxage=3600` | CDN cache time (overrides max-age) | Different TTLs for CDN vs browser |
| `no-cache` | Must revalidate before use | Ensure freshness |
| `no-store` | Don't cache at all | Sensitive data |
| `immutable` | Never revalidate | Versioned assets |

---

## ETags & Conditional Requests

Reduce bandwidth with 304 Not Modified responses.

### How It Works

```
1. Initial request:
   GET /api/posts/123
   
2. Server responds:
   200 OK
   ETag: "abc123xyz"
   Body: {...}

3. Subsequent request:
   GET /api/posts/123
   If-None-Match: "abc123xyz"
   
4. Server responds:
   304 Not Modified  ← No body sent!
   (Client uses cached version)
```

### Implementation

```python
import hashlib

@app.route('/api/posts/<post_id>')
def get_post(post_id):
    post = get_post_from_db(post_id)
    
    # Generate ETag from content
    content = json.dumps(post)
    etag = hashlib.md5(content.encode()).hexdigest()
    
    # Check if client has current version
    if request.headers.get('If-None-Match') == etag:
        return '', 304  # Not Modified
    
    response = jsonify(post)
    response.headers['ETag'] = etag
    response.headers['Cache-Control'] = 'public, max-age=300'
    
    return response
```

**Benefits:**
- Reduces bandwidth (no body sent on 304)
- Faster for client (smaller response)
- Still validates freshness

---

## Asset Versioning Strategies

### 1. Query String Versioning

```html
<script src="/app.js?v=123"></script>
<link rel="stylesheet" href="/style.css?v=456">
```

❌ Some CDNs ignore query strings  
❌ Not truly immutable

---

### 2. Content Hash in Filename (Best)

```html
<script src="/app.a3f2b1.js"></script>
<link rel="stylesheet" href="/style.9c4e7d.css">
```

✅ Truly immutable  
✅ Works with all CDNs  
✅ Automatic cache busting

**Build tool generates hashed filenames:**
```bash
# Before
app.js  style.css

# After
app.a3f2b1.js  style.9c4e7d.css
```

---

### 3. Path-Based Versioning

```html
<script src="/v123/app.js"></script>
<link rel="stylesheet" href="/v123/style.css">
```

✅ Easy to implement  
❌ Must update all references

---

## CDN Cache Invalidation

### 1. Time-Based (TTL)

Wait for cache to expire naturally.

```python
response.headers['Cache-Control'] = 'public, max-age=3600'
# CDN cache expires after 1 hour
```

✅ Simple  
❌ Can't force immediate update

---

### 2. Cache Purge

Manually clear CDN cache.

```python
import requests

def purge_cdn_cache(url):
    """Cloudflare cache purge example"""
    requests.post(
        'https://api.cloudflare.com/client/v4/zones/{zone_id}/purge_cache',
        headers={'Authorization': 'Bearer {api_token}'},
        json={'files': [url]}
    )

# When blog post updated
@app.route('/admin/posts/<post_id>', methods=['PUT'])
def update_post(post_id):
    update_post_in_db(post_id, request.json)
    
    # Purge CDN cache
    purge_cdn_cache(f'https://cdn.example.com/posts/{post_id}')
    
    return {"status": "updated"}
```

✅ Immediate update  
❌ API rate limits  
❌ Costs money (some CDNs)

---

### 3. Versioned URLs (Best)

Never need to purge - just change URL.

```python
# Old version cached forever
# <img src="/images/logo.v1.png">

# New version - different URL
# <img src="/images/logo.v2.png">
```

✅ Instant updates  
✅ No purge API needed  
✅ Free

---

## CDN Configuration Examples

### Cloudflare

```javascript
// cloudflare-worker.js
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  const url = new URL(request.url)
  
  // Cache static assets for 1 year
  if (url.pathname.match(/\.(js|css|png|jpg|woff2)$/)) {
    const response = await fetch(request)
    const newResponse = new Response(response.body, response)
    newResponse.headers.set('Cache-Control', 'public, max-age=31536000')
    return newResponse
  }
  
  // Don't cache API
  if (url.pathname.startsWith('/api/')) {
    return fetch(request)
  }
  
  return fetch(request)
}
```

---

### AWS CloudFront

```json
{
  "CacheBehaviors": [
    {
      "PathPattern": "/static/*",
      "TargetOriginId": "S3-static-assets",
      "CachePolicyId": "cache-optimized",
      "MinTTL": 31536000,
      "DefaultTTL": 31536000
    },
    {
      "PathPattern": "/api/*",
      "TargetOriginId": "API-origin",
      "CachePolicyId": "caching-disabled"
    }
  ]
}
```

---

## Costs & Savings

### Without CDN

```
Traffic: 1TB/month
Origin bandwidth: $0.09/GB
Cost: 1000 GB × $0.09 = $90/month

Origin server load:
- 1M requests/day
- Average 200ms response time
```

### With CDN

```
Traffic: 1TB/month
CDN hit rate: 90%
CDN bandwidth: $0.02/GB
Origin bandwidth: $0.09/GB

Costs:
- CDN: 900 GB × $0.02 = $18
- Origin: 100 GB × $0.09 = $9
Total: $27/month

Savings: $63/month (70% reduction)

Origin server load:
- 100k requests/day (90% reduction)
- Average 50ms response time (CDN-served)
```

---

## Best Practices

### 1. Use Separate Domains

```
www.example.com     ← Dynamic content (no CDN)
cdn.example.com     ← Static assets (CDN)
images.example.com  ← User uploads (CDN)
```

**Why:** Fine-grained cache control per domain

---

### 2. Enable Compression

```python
@app.route('/app.js')
def serve_js():
    response = send_file('app.js')
    response.headers['Content-Encoding'] = 'gzip'
    return response
```

**Savings:** 70-90% smaller files

---

### 3. Use WebP for Images

```html
<picture>
  <source srcset="image.webp" type="image/webp">
  <img src="image.jpg" alt="fallback">
</picture>
```

**Savings:** 25-35% smaller than JPEG

---

### 4. Lazy Load Images

```html
<img src="placeholder.jpg" data-src="actual-image.jpg" loading="lazy">
```

**Savings:** Don't load images until visible

---

## Rule of Thumb

- **Static assets:** CDN with 1-year cache + versioned URLs
- **User uploads:** CDN with long cache (1 month+)
- **API responses:** CDN for public data only (5-60 min cache)
- **Personalized content:** No CDN caching
- Use **content hashing** for true immutability
- Enable **compression** (gzip/brotli)
- Monitor **CDN hit rates** (target: > 80%)
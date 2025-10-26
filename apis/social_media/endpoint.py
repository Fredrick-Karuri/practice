
"""
Social Media Platform REST API Design

Pattern: RESTful design with clear resource hierarchies
Key Insights: 
- Nested resources for relationships (users/:id/posts)
- Pagination on all list endpoints
- Denormalized data in responses for performance
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

# ============================================
# REQUEST/RESPONSE MODELS
# ============================================

class UserResponse(BaseModel):
    "What we send to clients"
    id : int
    username:str
    display_name:str
    bio:Optional[str]
    profile_image_url:Optional[str]
    follower_count: int #denormalized for performance
    following_count:int
    created_at :datetime

class PostResponse(BaseModel):
    "What we send to clients"
    id : int
    content:str
    image_url : Optional[str]
    author:UserResponse # Nested user data (avoid extra request)
    like_count:int
    comment_count:int
    user_has_liked:bool #for current user
    created_at : datetime


class CreatePostRequest(BaseModel):
    "What clients send to create a post"
    content:str
    image_url:Optional[str]

class CommentResponse(BaseModel):
    id:str
    content:str
    author:UserResponse
    created_at:datetime

class PaginatedResponse(BaseModel):
    "Standard pagination wrapper"
    data:List[dict]
    page:int
    page_size:int
    total_count:int
    has_next:bool



# ============================================
# API ENDPOINTS SPECIFICATION
# ============================================

"""
BASE URL: https://api.socialapp.com/v1

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
USER ENDPOINTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

GET /users/:id
Description: Get user profile
Response: UserResponse
Status: 200 OK / 404 Not found
Caching: Cache for 5 minutes (user data changes rarely)

Example Response:
{
  "id": 123,
  "username": "johndoe",
  "display_name": "John Doe",
  "bio": "Software engineer",
  "profile_image_url": "https://...",
  "follower_count": 1500,
  "following_count": 300,
  "created_at": "2024-01-15T10:30:00Z"
}

---

GET /users/:id/posts
Description: Get user's posts (paginated)
Query Params:
    -page:int (default:1)
    -page_size: int (default:20,max:100)
Response:PaginatedResponse<PostResponse>
Status: 200 OK
Caching: cache for 1 minute

Example Response:
{
  "data": [
    {
      "id": 456,
      "content": "Hello world!",
      "author": { UserResponse },
      "like_count": 42,
      "comment_count": 5,
      "user_has_liked": false,
      "created_at": "2024-10-26T09:15:00Z"
    }
  ],
  "page": 1,
  "page_size": 20,
  "total_count": 150,
  "has_next": true
}

---

GET /users/:id/followers
Description: Get user's followers
Query Params:page,page_size
Response:PaginatedResponse<UserResponse>
Status: 200 Ok
Caching: Cache for 5 minutes

---

GET /users/:id/following
Description: Get users that this user follows
Query Params:page,page_size
Response:PaginatedResponse<UserResponse>
Status: 200 Ok
Caching: Cache for 5 minutes

---

GET /users/:id/follow
Description: Follow a user
Request Body: none
Response: {"Success":true}
Status: 201 created / 400 Bad request (already following)
Side Effects:
    -create follow relationship
    -invalidate follower_count caches
    -could trigger notifications (async job)

---

DELETE /users/:id/follow
Description: Unfollow a user
Response:{"Success":true}
Status: 200 OK / 404 Not Found
Side Effects:
    -delete follow relationship
    -invalidate follower_count caches

---


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
POST ENDPOINTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

POSTS /posts
Description:Create a new post
Request Body:CreatePostRequest
Response : Post Response
Status: 201 created/ 400 Bad Request (validation error)
Headers Required : Authorization : Bearer <token>
Side Effects:
    -Insert post into database
    -Invalidate author's post list cache
    -could trigger fan-out to follower's feed (async)

Example Request:
{
  "content": "Just deployed my new app!",
  "image_url": "https://cdn.example.com/image.jpg"
}

---

POSTS /posts/:id
Description: delete a post (author only)
Response : {"success":true} 
Status: 200 OK / 403 forbidden / 404 not found
Side Effects:
    -Delete post and all comments/likes (CASCADE)
    -invalidate caches

---

POST /posts/:id/like
Description: Like a post
Response: { "success": true, "like_count": 43 }
Status: 201 Created / 400 Bad Request (already liked)
Headers Required: Authorization: Bearer <token>
Side Effects:
  - Insert like record
  - Increment post.like_count (denormalized)
  - Invalidate post cache
  - Could trigger notification (async)


---

DELETE /posts/:id/like
Description: Unlike a post
Response: { "success": true, "like_count": 42 }
Status: 200 OK
Side Effects:
  - Delete like record
  - Decrement post.like_count
  - Invalidate post cache

---

GET /posts/:id/comments
Description: Get comments on a post
Query Params: page, page_size
Response: PaginatedResponse<CommentResponse>
Status: 200 OK
Caching: Cache for 30 seconds

---

POST /posts/:id/comments
Description: Add comment to post
Request Body: { "content": "Great post!" }
Response: CommentResponse
Status: 201 Created / 400 Bad Request
Side Effects:
  - Insert comment
  - Increment post.comment_count
  - Invalidate post and comments cache
  - Could trigger notification (async)

  
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FEED ENDPOINTS (Most Complex!)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

GET /feed
Description: Get authenticated user's personalized feed
Query Params:
  - page: int
  - page_size: int (max 50 for performance)
Response: PaginatedResponse<PostResponse>
Status: 200 OK
Headers Required: Authorization: Bearer <token>

This is THE critical endpoint for the app!

Query Strategy:
1. Get list of users current user follows
2. Fetch recent posts from those users
3. Sort by recency (or algorithm score)
4. Return paginated results

Performance Considerations:
- Cache aggressively (30-60 seconds)
- Pre-compute feeds for active users (fan-out on write)
- Use Redis for hot feed data
- Limit to recent posts (last 7 days) for performance

Example Response:
{
  "data": [
    { PostResponse with all nested data },
    { PostResponse with all nested data }
  ],
  "page": 1,
  "page_size": 20,
  "total_count": null,  // Don't calculate total (expensive!)
  "has_next": true
}

"""


# ============================================
# API DESIGN DECISIONS & TRADE-OFFS
# ============================================

"""
DECISION 1: Nested user data in PostResponse
WHY:
- Avoid N+1 query problem (fetching user for each post)
- Feed endpoint returns 20 posts = would need 20 extra requests without nesting
- Trade-off: Larger response size, but much fewer requests
ALTERNATIVE: Separate /users/:id endpoint, but requires client to make many requests

DECISION 2: Denormalized counts (like_count, follower_count)
WHY:
- Displayed on every post/profile view
- Calculating COUNT(*) on large tables is slow
- Trade-off: More complex write logic, eventual consistency
ALTERNATIVE: Calculate on read (too slow at scale)

DECISION 3: Pagination on all list endpoints
WHY:
- Prevent returning 1M+ records
- Predictable response times
- Standard pattern: page + page_size
ALTERNATIVE: Cursor-based pagination (better for real-time feeds)

DECISION 4: POST /users/:id/follow (not PUT)
WHY:
- POST for creating relationship (more semantic)
- Idempotent behavior: return 400 if already following
- Could use PUT, but POST is more common for this pattern
ALTERNATIVE: PUT /users/:id/relationships with body { "type": "follow" }

DECISION 5: Separate like/unlike endpoints (not toggle)
WHY:
- Explicit intent (client knows current state)
- Avoid race conditions (two clicks = two likes without careful logic)
- Trade-off: Client needs to track state
ALTERNATIVE: POST /posts/:id/like with toggle logic (simpler client, more complex server)

DECISION 6: No total_count in feed pagination
WHY:
- Calculating total for complex feed query is expensive
- User doesn't need exact count (just "has more")
- Trade-off: Can't show "page X of Y"
ALTERNATIVE: Estimate total or calculate async

DECISION 7: Version in URL (/v1/)
WHY:
- Breaking changes inevitable (add v2 later)
- Clients can migrate gradually
- Trade-off: Maintaining multiple versions
ALTERNATIVE: Version in header (less visible to developers)

DECISION 8: Bearer token authentication
WHY:
- Stateless (server doesn't store sessions)
- Works with mobile apps and SPAs
- Standard: JWT tokens with expiry
ALTERNATIVE: Session cookies (stateful, harder to scale)

WHAT WOULD BREAK AT SCALE:
- Feed generation (100M users following 1000 people each)
  → Solution: Pre-compute feeds, use Redis, fan-out on write
- Like counts (race conditions on high-traffic posts)
  → Solution: Queue-based counter updates, eventual consistency
- Deep pagination (page 1000 of results)
  → Solution: Cursor-based pagination instead
- Real-time updates (feed should update live)
  → Solution: WebSockets for real-time, polling for fallback

CACHING STRATEGY:
- User profiles: 5 minutes (change rarely)
- Posts: 30 seconds (likes/comments change often)
- Feeds: 1 minute (balance freshness vs load)
- Use ETags for conditional requests (304 Not Modified)
- Cache-Control headers for CDN caching
"""
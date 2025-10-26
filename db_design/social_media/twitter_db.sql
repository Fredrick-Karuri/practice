-- Social Media Platform Database Schema
-- Design Goal: Support posts, follows, likes, comments, and feed generation

-- ============================================
-- USERS TABLE
-- ============================================
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    display_name VARCHAR(100),
    bio TEXT,
    profile_image_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for username lookups
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);


-- ============================================
-- POSTS TABLE
-- ============================================
CREATE TABLE posts (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    image_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Denormalized counts for performance
    like_count INTEGER DEFAULT 0,
    comment_count INTEGER DEFAULT 0,
    
    CONSTRAINT content_length CHECK (LENGTH(content) <= 280)
);

-- Index for finding user's posts
CREATE INDEX idx_posts_user_id ON posts(user_id);
-- Index for chronological ordering
CREATE INDEX idx_posts_created_at ON posts(created_at DESC);


-- ============================================
-- FOLLOWS TABLE (Many-to-Many: Users follow Users)
-- ============================================
CREATE TABLE follows (
    id BIGSERIAL PRIMARY KEY,
    follower_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    following_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Prevent following yourself
    CONSTRAINT no_self_follow CHECK (follower_id != following_id),
    -- Prevent duplicate follows
    CONSTRAINT unique_follow UNIQUE (follower_id, following_id)
);

-- Index for "who does user X follow?"
CREATE INDEX idx_follows_follower ON follows(follower_id);
-- Index for "who follows user X?"
CREATE INDEX idx_follows_following ON follows(following_id);


-- ============================================
-- LIKES TABLE (Many-to-Many: Users like Posts)
-- ============================================
CREATE TABLE likes (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    post_id BIGINT NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Prevent duplicate likes
    CONSTRAINT unique_like UNIQUE (user_id, post_id)
);

-- Index for "did user X like post Y?"
CREATE INDEX idx_likes_user_post ON likes(user_id, post_id);
-- Index for "who liked post X?"
CREATE INDEX idx_likes_post ON likes(post_id);


-- ============================================
-- COMMENTS TABLE
-- ============================================
CREATE TABLE comments (
    id BIGSERIAL PRIMARY KEY,
    post_id BIGINT NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT comment_length CHECK (LENGTH(content) <= 500)
);

-- Index for finding comments on a post
CREATE INDEX idx_comments_post_id ON comments(post_id);
-- Index for chronological ordering
CREATE INDEX idx_comments_created_at ON comments(created_at);


-- ============================================
-- EXAMPLE QUERIES
-- ============================================

-- Get a user's feed (posts from people they follow)
-- This is the most important query for this system!
SELECT 
    p.id,
    p.content,
    p.created_at,
    u.username,
    u.display_name,
    p.like_count,
    p.comment_count
FROM posts p
JOIN users u ON p.user_id = u.id
WHERE p.user_id IN (
    SELECT following_id 
    FROM follows 
    WHERE follower_id = ? -- Current user's ID
)
ORDER BY p.created_at DESC
LIMIT 50;


-- Check if user has liked a specific post
SELECT EXISTS (
    SELECT 1 
    FROM likes 
    WHERE user_id = ? AND post_id = ?
);


-- Get post with like status for current user
SELECT 
    p.*,
    u.username,
    u.display_name,
    EXISTS (
        SELECT 1 FROM likes 
        WHERE user_id = ? AND post_id = p.id
    ) as user_has_liked
FROM posts p
JOIN users u ON p.user_id = u.id
WHERE p.id = ?;


-- ============================================
-- DESIGN DECISIONS & TRADE-OFFS
-- ============================================

/*
DECISION 1: Denormalized like_count and comment_count in posts table
WHY: 
- Displaying feed requires showing these counts for every post
- Calculating COUNT(*) for each post on every feed load is expensive
- Trade-off: Slightly more complex write logic (update counts on like/comment)
- Benefit: Much faster feed loading

DECISION 2: Separate follows table (not storing followers in user table)
WHY:
- Supports efficient queries in both directions (followers & following)
- Easier to paginate large follower lists
- Simpler to query feed (just JOIN on follows table)

DECISION 3: Indexes on user_id + created_at for posts
WHY:
- Feed query filters by user_id AND sorts by created_at
- Composite index makes this query very fast
- Trade-off: More storage, slower inserts (minimal impact)

DECISION 4: CASCADE deletes
WHY:
- If user deletes account, their posts/likes/follows should be removed
- Maintains referential integrity automatically
- Alternative: Soft deletes (set deleted_at timestamp) for audit trail

DECISION 5: Content length constraints
WHY:
- Prevents abuse and storage issues
- Enforces business rules at database level
- Alternative: Validate only in application (riskier)

WHAT COULD BE IMPROVED:
- Add full-text search indexes for content search
- Partition posts table by date for better performance at scale
- Add read replicas for feed generation (read-heavy workload)
- Consider caching layer (Redis) for hot posts/feeds
- Add soft deletes for user recovery
*/
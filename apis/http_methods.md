GET    - Read data (idempotent - safe to repeat)
POST   - Create new resource
PUT    - Replace entire resource
PATCH  - Partially update resource
DELETE - Remove resource
```

**URL Design Patterns:**
```
✅ Good:
GET    /users                    (list users)
GET    /users/:id                (get specific user)
POST   /users                    (create user)
GET    /users/:id/posts          (user's posts)
POST   /posts                    (create post)
GET    /posts/:id/comments       (post's comments)

❌ Bad:
GET    /getUserById?id=123       (not RESTful)
POST   /createPost               (verb in URL)
GET    /posts/get                (redundant)
```

**Status Codes You'll Use:**
```
200 OK           - Success
201 Created      - Resource created
400 Bad Request  - Client error (validation failed)
401 Unauthorized - Not authenticated
403 Forbidden    - Authenticated but not allowed
404 Not Found    - Resource doesn't exist
500 Server Error - Something broke on server

## Api design principles
1.Consistent naming - plural nouns for collections
2.Predictable structure - similar endpoints work similarly
3.Versioning - /v1/users (plan for change)
4.Pagination - never return unlimited resources
5.Filtering - Get /posts?user_id=123&limit=20

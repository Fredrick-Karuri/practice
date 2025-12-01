# Software Engineering Learning Portfolio

A comprehensive monorepo documenting my 30-day interview preparation journey, featuring practical implementations, system design studies, and algorithmic problem-solving.

## 📋 Repository Structure

```
learning-portfolio/
├── caching&scaling/          # System design deep-dives
├── projects/                 # Full-stack implementations
│   ├── url_shortener/       # Production-ready URL shortener
│   └── social_media/        # Social media backend architecture
├── ds_algorithms/           # LeetCode solutions & patterns
└── materials/               # Study resources & notes
```

## 🎯 Purpose

This repository serves as:
- **Learning Journal**: Documenting my software engineering learning journey
- **Interview Preparation**: 30-day intensive prep covering system design, algorithms, and full-stack development
- **Portfolio**: Demonstrating practical skills through real-world projects
- **Reference Material**: Personal knowledge base for system design patterns and best practices

## 🏗️ Projects

### URL Shortener
Full-stack application with production-ready features:
- **Backend**: FastAPI, PostgreSQL, Redis caching, Alembic migrations
- **Frontend**: React + TypeScript, Vite
- **Features**: Base62 encoding, analytics tracking, distributed caching
- **Testing**: Comprehensive test suite with pytest
- [View Project Details](./projects/url_shortener/README.md)

### Social Media Backend
API design and implementation for social media features:
- RESTful API architecture
- Scalable feed generation
- [View Design Document](./projects/social_media/design.md)

## 📚 System Design Studies

Comprehensive notes covering production system architecture:

1. **[Caching Strategies](./caching&scaling/01-caching-strategies.md)** - Cache-aside, write-through, write-behind patterns
2. **[Scaling Architectures](./caching&scaling/02-scaling-architectures.md)** - Horizontal/vertical scaling, load balancing
3. **[Database Scaling](./caching&scaling/03-database-scaling.md)** - Replication, sharding, partitioning
4. **[Async Processing & Queues](./caching&scaling/04-async-processing-queues.md)** - Message queues, event-driven architecture
5. **[CDN & Edge Caching](./caching&scaling/05-cdn-edge-caching.md)** - Content delivery optimization
6. **[Monitoring & Observability](./caching&scaling/06-monitoring-observability.md)** - Metrics, logging, tracing
7. **[Case Study: Social Feed](./caching&scaling/07-social-feed-case-study.md)** - Real-world application

[View All System Design Notes](./caching&scaling/Index.md)

## 💻 Technical Stack

**Languages**: Python, TypeScript, JavaScript  
**Backend**: FastAPI, SQLAlchemy, Alembic  
**Frontend**: React, Vite  
**Databases**: PostgreSQL, Redis  
**Tools**: Docker, Git, pytest  

## 🎓 Skills Demonstrated

- **System Design**: Scalability patterns, caching strategies, distributed systems
- **Backend Development**: RESTful APIs, database design, ORM, migrations
- **Frontend Development**: Modern React, TypeScript, component architecture
- **Testing**: Unit tests, integration tests, TDD practices
- **DevOps**: Docker containerization, database migrations
- **Algorithms**: Problem-solving, data structures, optimization

## 📈 Learning Approach

This portfolio follows a structured 30-day learning path:
- **Days 1-10**: System design fundamentals and caching
- **Days 11-20**: Full-stack project implementation (URL shortener)
- **Days 21-30**: Advanced topics and social media architecture

## 🔗 Navigation

- [System Design Index](./caching&scaling/Index.md)
- [Project Documentation](./projects/)
- [Algorithms & Data Structures](./ds_algorithms/)

## 📝 Notes

This is an active learning repository, continuously updated with new concepts, projects, and solutions as I progress through my interview preparation.

---

**Contact**: [Your Email] | [LinkedIn] | [GitHub]  
**Last Updated**: December 2025
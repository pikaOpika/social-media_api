# Social Media API

A REST API for a small social network: users publish posts, follow each other,
like and comment. Posts can be scheduled — a background worker publishes them
when their time comes.

Built with Django REST Framework, PostgreSQL, Celery and Redis. Runs entirely in Docker.

## Features

- **Authentication** — JWT with refresh-token rotation and blacklisting on logout
- **Users** — registration, profile with avatar and bio, search by username
- **Follows** — follow/unfollow, follower and following lists
- **Posts** — CRUD with author-only editing, image upload, hashtags created on the fly
- **Feed** — posts from the people you follow, plus your own
- **Likes** — like/unlike, list of posts you liked
- **Comments** — nested under their post: `/api/posts/{post_id}/comments/`
- **Scheduled publishing** — a Celery beat task publishes due posts every minute
- **Documentation** — OpenAPI schema with Swagger UI and ReDoc

## Tech stack

| Layer | Choice |
|---|---|
| Framework | Django 6, Django REST Framework |
| Database | PostgreSQL 16 |
| Task queue | Celery 5 with Redis as broker |
| Auth | djangorestframework-simplejwt |
| Docs | drf-spectacular |
| Runtime | Docker Compose |

## Getting started

Requires Docker and Docker Compose.

```bash
git clone <repository-url>
cd social-media-api

cp .env.sample .env
# fill in the values — see the table below
```

Generate a secret key:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Start everything:

```bash
docker compose up --build
```

Five services come up: `db`, `redis`, `app`, `worker`, `beat`. The app waits for
Postgres and Redis to report healthy before running migrations, so the first
start needs no retry.

Create an administrator:

```bash
docker compose exec app python manage.py createsuperuser
```

The API is then available at `http://localhost:8000/`.

## Environment variables

| Variable | Description | Example |
|---|---|---|
| `SECRET_KEY` | Django secret key | `django-insecure-...` |
| `DEBUG` | Debug mode; `True` or `False` | `True` |
| `ALLOWED_HOSTS` | Comma-separated host list | `localhost,127.0.0.1` |
| `POSTGRES_DB` | Database name | `social_media` |
| `POSTGRES_USER` | Database user | `postgres` |
| `POSTGRES_PASSWORD` | Database password | `postgres` |
| `POSTGRES_HOST` | Database host — the compose service name | `db` |
| `POSTGRES_PORT` | Database port inside the network | `5432` |
| `CELERY_BROKER_URL` | Redis URL for the broker | `redis://redis:6379/0` |

`POSTGRES_HOST` and the broker URL use service names, not `localhost`: containers
reach each other over the internal Docker network, where the service name resolves
as a hostname.

## Documentation

| URL | What it is |
|---|---|
| `/doc/schema/` | Raw OpenAPI schema |
| `/doc/schema/swagger-ui/` | Swagger UI |
| `/doc/schema/redoc/` | ReDoc |

Endpoints are grouped into `auth`, `users`, `posts` and `comments`.

## Main endpoints

### Auth

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/register/` | Create an account |
| POST | `/api/token/` | Obtain access and refresh tokens |
| POST | `/api/token/refresh/` | Refresh the access token |
| POST | `/api/logout/` | Blacklist the refresh token |

### Users

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/users/` | List users, `?search=` by username |
| GET | `/api/users/{id}/` | User detail with counters |
| GET/PUT/PATCH | `/api/users/me/` | Own profile |
| POST | `/api/users/{id}/follow/` | Follow |
| POST | `/api/users/{id}/unfollow/` | Unfollow |
| GET | `/api/users/{id}/followers/` | Followers |
| GET | `/api/users/{id}/following/` | Following |

### Posts

| Method | Endpoint | Description |
|---|---|---|
| GET/POST | `/api/posts/` | List and create, `?search=` by title or hashtag |
| GET/PUT/PATCH/DELETE | `/api/posts/{id}/` | Detail; only the author may modify |
| GET | `/api/posts/feed/` | Posts from followed users and your own |
| POST | `/api/posts/{id}/like/` | Like |
| POST | `/api/posts/{id}/unlike/` | Unlike |
| GET | `/api/posts/liked_posts/` | Posts you liked |

### Comments

| Method | Endpoint | Description |
|---|---|---|
| GET/POST | `/api/posts/{post_id}/comments/` | List and create |
| GET/PUT/PATCH/DELETE | `/api/posts/{post_id}/comments/{id}/` | Detail; only the author may modify |

## Scheduled publishing

A post carries two separate fields:

- `publish_at` — the intent: when it should go live
- `is_published` — the fact: whether it is live

Creating a post without `publish_at` publishes it immediately. With `publish_at`
set, the post stays invisible to everyone except its author until a Celery beat
task — running once a minute — finds it overdue and flips `is_published`.

The task re-reads the database on every run rather than scheduling one job per
post. That keeps the intent in a single place: editing or deleting a scheduled
post needs no bookkeeping in the queue, and a worker that was down for an hour
simply catches up on its next run.

## Running tests

```bash
docker compose exec app python manage.py test
```

Coverage focuses on custom logic rather than framework behaviour: object-level
permissions, likes, follows in both directions, feed composition, visibility of
unpublished posts, and the publishing task itself.

# Deploying GamerZone

Five pieces have to live somewhere: the frontend, the API, PostgreSQL, Redis, and an
SMTP server. This describes deploying all five on free tiers.

No application code changes between local and production — only environment variables.

> Free-tier terms change. Check each provider's current limits before relying on them.

| Piece | Where | Why |
|---|---|---|
| Frontend | **Vercel** | Built by the Next.js team; zero configuration |
| API | **Render** | Still offers a genuinely permanent free tier |
| PostgreSQL | **Neon** | Wakes in well under a second when idle |
| Redis | **Upstash** | Serverless; this app's usage is tiny |
| Email | **Brevo** | Sends from a verified address without owning a domain |

---

## Order matters

Each step produces a value the next one needs, and the last step closes a loop:

```
1. Neon      →  DATABASE_URL
2. Upstash   →  REDIS_URL
3. Brevo     →  MAIL_* credentials
        ↓
4. Render    →  deploy the API with all of the above
             →  https://<your-api>.onrender.com
        ↓
5. Vercel    →  deploy the frontend with API_URL set to that
             →  https://<your-site>.vercel.app
        ↓
6. Render    →  go back and set the three variables that need the frontend's address
```

**Step 6 is the one people forget.** The API needs to know the frontend's address, but
that address doesn't exist until step 5.

---

## 1. PostgreSQL — Neon

Create a project at [neon.tech](https://neon.tech). Enable only **Postgres** — not Neon
Auth, which would duplicate the authentication this project implements itself.

Pick the region closest to your users, and **use the same region for Render**. Every
request makes several database round trips, so a database on another continent from the
API is the costliest latency mistake available.

Copy the **pooled** connection string (its host contains `-pooler`), then rewrite it:

```
# what Neon gives you
postgresql://user:pass@ep-xxx-pooler.region.aws.neon.tech/neondb?sslmode=require&channel_binding=require

# what this app needs
postgresql+asyncpg://user:pass@ep-xxx-pooler.region.aws.neon.tech/neondb?ssl=require
```

Three changes, and all three matter:

1. `postgresql://` → `postgresql+asyncpg://`, so SQLAlchemy loads the right driver.
2. Drop `sslmode` and `channel_binding`. Those are **libpq** parameters; asyncpg does
   not accept them and raises `TypeError: connect() got an unexpected keyword argument
   'sslmode'` before it ever reaches the network.
3. Add `?ssl=require` — Neon requires TLS, and `ssl` is the name asyncpg understands.

## 2. Redis — Upstash

Create a database at [upstash.com](https://upstash.com) and copy the Redis URL. It
starts with `rediss://` — two s's, meaning TLS. Keep it exactly as given.

## 3. Email — Brevo

Sign up at [brevo.com](https://brevo.com), verify the address you'll send from, and
create SMTP credentials (an *SMTP key*, not your account password).

> Most transactional providers require you to own and verify a **domain** before
> sending to arbitrary recipients. Brevo lets a verified individual address send,
> which is why it's the choice here. If you buy a domain later, any provider works.

## 4. The API — Render

Create a **Web Service** from your GitHub repo at [render.com](https://render.com).

| Setting | Value |
|---|---|
| Root directory | `backend` |
| Environment | Docker (it will find `backend/Dockerfile`) |
| Pre-deploy command | `alembic upgrade head` |
| Health check path | `/api/v1/health` |

The pre-deploy command is what applies migrations. Without it the tables never get
created, and every request fails on a missing table.

Environment variables:

| Variable | Value |
|---|---|
| `SECRET_KEY` | **Generate a new one.** Never reuse the development key |
| `DATABASE_URL` | From step 1 |
| `REDIS_URL` | From step 2 |
| `MAIL_HOST` | `smtp-relay.brevo.com` |
| `MAIL_PORT` | `587` |
| `MAIL_USERNAME` / `MAIL_PASSWORD` | From step 3 |
| `MAIL_USE_TLS` | `true` |
| `MAIL_FROM` | Your verified sender address |
| `MAIL_FROM_NAME` | `GamerZone` |
| `DEBUG` | `false` — leaving it on logs every SQL statement |
| `CORS_ORIGINS` | Placeholder for now; fixed in step 6 |
| `VERIFICATION_URL_BASE` | Placeholder for now |
| `PASSWORD_RESET_URL_BASE` | Placeholder for now |

Generate the secret with:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Do not set `PORT` — Render assigns it, and the Dockerfile reads it.

## 5. The frontend — Vercel

Import the repo at [vercel.com](https://vercel.com).

| Setting | Value |
|---|---|
| Root directory | `frontend` |
| Framework | Next.js (detected) |

One environment variable:

| Variable | Value |
|---|---|
| `API_URL` | `https://<your-api>.onrender.com` |

**No `NEXT_PUBLIC_` prefix.** Only prefixed variables are bundled into browser code,
and the browser must never hold the API address or the session token.

## 6. Close the loop on Render

With the Vercel URL in hand, update three variables and redeploy:

| Variable | Value |
|---|---|
| `CORS_ORIGINS` | `https://<your-site>.vercel.app` |
| `VERIFICATION_URL_BASE` | `https://<your-site>.vercel.app/verify` |
| `PASSWORD_RESET_URL_BASE` | `https://<your-site>.vercel.app/reset-password` |

## 7. Make yourself an administrator

The first account has to be promoted by hand — signup deliberately cannot grant it.
Register on the live site, confirm the email, then run this in Neon's SQL editor:

```sql
UPDATE "user" SET is_superuser = true WHERE email = 'you@example.com';
```

Sign out and back in. The **Admin** link appears, and download links can be managed
through the site from then on.

---

## Checking it works

1. The home page loads
2. Registering delivers a real email
3. The link in it confirms the account
4. Signing in reaches the downloads
5. `/admin/downloads` is reachable once promoted, and refused before that

If something fails, Render's logs carry the traceback. Every error response includes a
`request_id` that appears on the matching log line.

---

## Known characteristics of this setup

**The API sleeps after about fifteen minutes idle**, and waking takes roughly a minute.
The home and about pages don't touch the API, so they are always fast; the home page
also fires a request at `/api/warm` on load, which wakes the API while the visitor is
still reading. By the time anyone reaches Downloads or Sign in it is usually up.

This is driven by real visits — an unvisited site still sleeps, which is what the free
tier expects. Do not add a cron job to keep it awake: it violates the spirit of the
tier and burns the monthly allowance.

**Neon also sleeps**, but wakes in well under a second.

**Avoid Supabase's free tier here.** Projects pause after a week of inactivity and need
manual resuming — poor for a site that may go unvisited for a while.

---

## What changes if you buy a domain

Point it at Vercel, then update `CORS_ORIGINS`, `VERIFICATION_URL_BASE` and
`PASSWORD_RESET_URL_BASE` on Render. Nothing else, and no code.

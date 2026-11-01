# PhysIQ

AI fitness coaching application built with Django and Azure OpenAI.

## Local setup

1. Create and activate a Python virtual environment.
2. Run `python -m pip install -r requirements.txt`.
3. Copy `.env.example` to `.env` and replace every placeholder locally.
4. Generate a unique Django secret with `python -c "import secrets; print(secrets.token_urlsafe(64))"` and put it in `DJANGO_SECRET_KEY` in your local `.env`.
5. Set `DJANGO_DEBUG=true` for local development only. Configure your own Azure credentials if using the AI features.
6. Run `python manage.py migrate`, then `python manage.py runserver`.

Keep `.env`, databases, uploaded photos, and Python caches untracked. Production needs a separate deployment configuration and fresh credentials.

## Publish as a new repository

This source-only copy intentionally has no previous Git history. Create an empty GitHub repository, then run these commands from this folder, replacing `YOUR-NEW-REPO-URL`:

```bash
git init -b main
git add .
git commit -m "Initial clean source import"
git remote add origin YOUR-NEW-REPO-URL
git push -u origin main
```

Do not import branches or history from the original repositories. Credentials previously committed there should be rotated before using this copy in a deployment.

Four large PNG files could not be retrieved through the GitHub connection: `coach_loader.png`, `icons/curl.png`, `icons/heart.png`, and `icons/robot.png`. Their paths contain existing bundled images as visual fallbacks. Replace them with your original artwork locally if desired.

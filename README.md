# Leafy

## Local development

Initialize the virtual environment:

```bash
make init
```

Run migrations (it will use a local sqlite database for development):

```bash
make makemigrations
```

Run the web server:

```bash
make serve
```

Run the bot (it requires a telegram token):

```bash
export TELEGRAM_TOKEN=...
make bot
```


## Docker Compose development

This environment resembles the production environment as closely as possible.

Run migrations:

```bash
docker-compose run --build migrate
```

Start the web server:

```bash
docker-compose up -d --build web
```

Access the web server at http://localhost:8000

Start the bot:

```bash
export TELEGRAM_TOKEN=...
docker-compose up -d --build bot
```

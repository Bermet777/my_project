echo "Waiting for Postgres..."
while ! nc -z postgres 5432; do
    sleep 0.1
done
echo "PostgreSQL started"

alembic upgrade head
gunicorn -w 1 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 autoapp:app --timeout 90

"""Autoapp module."""
from app.main import create_app
from config.settings import get_settings

settings = get_settings()

app = create_app(settings)

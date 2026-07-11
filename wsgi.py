"""wsgi.py — Production entry point for Gunicorn / Render.com.

Usage:
    gunicorn wsgi:server --bind 0.0.0.0:8050 --workers 2
"""
from app import server  # noqa: F401 — Gunicorn looks for 'server' in this module

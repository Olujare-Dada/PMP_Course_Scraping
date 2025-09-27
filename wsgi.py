#!/usr/bin/env python3
"""
WSGI configuration for production deployment
"""
from scraping_api import app

if __name__ == "__main__":
    app.run()

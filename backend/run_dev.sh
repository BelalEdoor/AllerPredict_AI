#!/usr/bin/env bash
# Simple helper to run backend in development
export PYTHONUNBUFFERED=1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

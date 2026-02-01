#!/bin/bash

echo "🚀 Starting LabMan v2 Backend..."
uvicorn app.main:app --reload --port 8000

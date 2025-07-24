# Biotech DMS Flask API

## Endpoints

- POST `/upload` — Upload CSV and return DMS scores
- POST `/ai-search` — Use OpenAI to search and summarize programs for a given target + modality

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# Add your OpenAI key to .env
python app.py
```

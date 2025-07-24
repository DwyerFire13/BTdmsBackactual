import os
import csv
import io
import openai
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime

app = Flask(__name__)
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    df = pd.read_csv(file)
    df["score"] = df.apply(compute_score, axis=1)
    return jsonify(df.to_dict(orient="records"))

def compute_score(row):
    score = 100
    if row.get("ind_enabling_studies_done"):
        score -= 40
    if row.get("received_pre_ind_feedback"):
        score -= 20
    if row.get("has_in_vivo_data"):
        score -= 20
    if row.get("has_in_vitro_data"):
        score -= 20
    return max(1, min(100, score))

@app.route("/ai-search", methods=["POST"])
def ai_search():
    data = request.json
    target = data.get("target", "")
    modality = data.get("modality", "")

    prompt = f"""You are a biotech analyst. Based on public information, generate 3 fictional but realistic programs targeting {target} using {modality}. Return as CSV with the columns:
company,program,development_stage,target,expected_ind_date,has_in_vivo_data,has_in_vitro_data,modality,received_pre_ind_feedback,ind_enabling_studies_done. Dates should be in YYYY-MM-DD. Use TRUE/FALSE for booleans.
"""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=500
    )

    csv_data = response["choices"][0]["message"]["content"]

    # Parse CSV
    reader = csv.DictReader(io.StringIO(csv_data))
    rows = list(reader)
    return jsonify(rows)

if __name__ == "__main__":
    app.run(debug=True)

import os
import csv
import io
import openai
from flask import Flask, request, render_template, redirect, url_for, flash
from dotenv import load_dotenv
import pandas as pd

AI_PROMPT_TEMPLATE = """You are a biotech analyst. Based on public information, generate 3 fictional but realistic programs targeting {target} using {modality}. Return as CSV with the columns:
company,program,development_stage,target,expected_ind_date,has_in_vivo_data,has_in_vitro_data,modality,received_pre_ind_feedback,ind_enabling_studies_done. Dates should be in YYYY-MM-DD. Use TRUE/FALSE for booleans.
"""

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "your-secret-key-here")
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")
    if not file:
        flash("No file uploaded", "error")
        return redirect(url_for("index"))

    try:
        df = pd.read_csv(file)
        df["score"] = df.apply(compute_score, axis=1)
        rows = df.to_dict(orient="records")
        return render_template("index.html", rows=rows)
    except Exception as e:
        flash(f"Error processing file: {str(e)}", "error")
        return redirect(url_for("index"))

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
    target = request.form.get("target", "")
    modality = request.form.get("modality", "")
    
    if not target or not modality:
        flash("Please provide both target and modality", "error")
        return redirect(url_for("index"))

    try:
        prompt = AI_PROMPT_TEMPLATE.format(target=target, modality=modality)

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )

        csv_data = response["choices"][0]["message"]["content"]

        # Parse CSV
        reader = csv.DictReader(io.StringIO(csv_data))
        ai_results = list(reader)
        return render_template("index.html", ai_results=ai_results, target=target, modality=modality)
    except Exception as e:
        flash(f"Error generating AI results: {str(e)}", "error")
        return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)

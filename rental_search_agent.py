"""
Rental Agent System - Full Production-ready Version

Features:
- Scrapes up to 290 listings in one search from a user-provided rental site search page.
- Built-in + user-defined questions (typed or uploaded from a text file).
- Twilio automated calls to assets with phone numbers.
- Records calls, transcribes using OpenAI Whisper via HTTPS API.
- Summarizes all responses using GPT-4-Turbo via HTTPS API.
- Stores assets, responses, summaries, and recording URLs in SQLite.
- Simple Flask dashboard displays listings, responses, summaries, and recordings.

Environment Variables Required:
- OPENAI_API_KEY: for Whisper and GPT-4-Turbo
- TWILIO_ACCOUNT_SID
- TWILIO_AUTH_TOKEN
- TWILIO_PHONE_NUMBER
- HOST_BASE_URL: public URL Twilio can reach (for local testing, use ngrok)
- RENTAL_AGENT_DB (optional, defaults to rental_agent.db)

Notes:
- Twilio webhooks require public URL acces, deploy to a real server (AWS, DigitalOcean, Heroku, etc.) or for local testing, use ngrok.
- Scraping is generic; update CSS selectors per target site and respect robots.txt.
- Calls and transcription/summarization run asynchronously in background threads.
"""

import os
import sqlite3
import logging
import uuid
import time
import json
from typing import List, Dict, Optional
from urllib.parse import urlencode

import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify, render_template_string, url_for
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather
from threading import Thread

# -------------------------------
# Environment variables and configuration
# -------------------------------
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "").strip()
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID", "").strip()
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "").strip()
TWILIO_PHONE_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER", "").strip()  # e.g. +1234567890
HOST_BASE_URL = os.environ.get("HOST_BASE_URL", "http://localhost:5000").rstrip("/")
DB_PATH = os.environ.get("RENTAL_AGENT_DB", "rental_agent.db")

# Twilio client initialization
twilio_client: Optional[Client] = None
if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

if not (OPENAI_API_KEY and TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and TWILIO_PHONE_NUMBER):
    logging.warning("One or more environment variables are missing. Calling, transcription, or summarization may fail.")

# OpenAI models
OPENAI_SUMMARY_MODEL = "gpt-4-turbo"
OPENAI_WHISPER_MODEL = "whisper-1"

# -------------------------------
# Flask app
# -------------------------------
app = Flask(__name__)

# -------------------------------
# Database helpers (SQLite)
# -------------------------------
def init_db():
    """Initialize the SQLite database with assets and responses tables."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS assets (
            id TEXT PRIMARY KEY,
            title TEXT,
            description TEXT,
            phone TEXT,
            scraped_at INTEGER,
            summary TEXT,
            recording_url TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS responses (
            id TEXT PRIMARY KEY,
            asset_id TEXT,
            question_index INTEGER,
            question TEXT,
            answer_text TEXT,
            created_at INTEGER,
            FOREIGN KEY(asset_id) REFERENCES assets(id)
        )
    """)
    conn.commit()
    conn.close()


def insert_asset(asset_id: str, title: str, description: str, phone: str):
    """Insert or update an asset in the DB."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO assets (id, title, description, phone, scraped_at)
        VALUES (?, ?, ?, ?, ?)
    """, (asset_id, title, description, phone, int(time.time())))
    conn.commit()
    conn.close()


def save_response(asset_id: str, q_index: int, question: str, answer_text: str):
    """Save a single question response for an asset."""
    resp_id = str(uuid.uuid4())
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO responses (id, asset_id, question_index, question, answer_text, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (resp_id, asset_id, q_index, question, answer_text, int(time.time())))
    conn.commit()
    conn.close()


def get_asset_responses(asset_id: str) -> List[Dict]:
    """Retrieve all responses for a given asset."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT question_index, question, answer_text
        FROM responses
        WHERE asset_id = ?
        ORDER BY question_index
    """, (asset_id,))
    rows = c.fetchall()
    conn.close()
    return [{"index": r[0], "question": r[1], "answer": r[2]} for r in rows]


def set_asset_summary(asset_id: str, summary_text: str):
    """Update the summary for an asset."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE assets SET summary = ? WHERE id = ?", (summary_text, asset_id))
    conn.commit()
    conn.close()


def set_asset_recording(asset_id: str, recording_url: str):
    """Update the recording URL for an asset."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE assets SET recording_url = ? WHERE id = ?", (recording_url, asset_id))
    conn.commit()
    conn.close()


def list_assets() -> List[Dict]:
    """Return all assets from the DB with latest scraped first."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT id, title, description, phone, summary, recording_url, scraped_at
        FROM assets
        ORDER BY scraped_at DESC
    """)
    rows = c.fetchall()
    conn.close()
    keys = ["id", "title", "description", "phone", "summary", "recording_url", "scraped_at"]
    return [dict(zip(keys, row)) for row in rows]

# -------------------------------
# Scraper
# -------------------------------
def scrape_rental_site(url: str, categories: List[str], max_listings: int = 290) -> List[Dict]:
    """
    Scrape rental listings from the given URL.
    :param url: User-specified rental site search page
    :param categories: List of keywords to filter listings
    :param max_listings: Maximum number of listings to return
    :return: List of assets
    """
    logging.info(f"Scraping URL={url} with categories={categories}")
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        logging.exception("Failed to fetch rental site URL")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    # Generic example: replace 'div.listing' with actual CSS selector per site
    listings = soup.find_all("div", class_="listing")
    matched = []

    for listing in listings:
        if len(matched) >= max_listings:
            break
        title_el = listing.find("h2")
        desc_el = listing.find("p")
        phone_el = listing.find("span", class_="phone")
        title = title_el.get_text(strip=True) if title_el else ""
        desc = desc_el.get_text(strip=True) if desc_el else ""
        phone = phone_el.get_text(strip=True) if phone_el else "N/A"

        text_blob = f"{title} {desc}".lower()
        if all(cat.strip().lower() in text_blob for cat in categories):
            asset_id = str(uuid.uuid4())
            matched.append({"id": asset_id, "title": title, "description": desc, "phone": phone})
            insert_asset(asset_id, title, desc, phone)

    logging.info(f"Scrape found {len(matched)} matching assets")
    return matched

# -------------------------------
# Built-in questions
# -------------------------------
DEFAULT_PREDEFINED_QUESTIONS = [
    "Are there external noises that are heard inside the asset?",
    "What is the monthly rent?",
    "Is the deposit refundable?",
    "What is the minimum lease period?",
    "Are pets allowed?"
]

# -------------------------------
# Twilio call orchestration
# -------------------------------
def create_outbound_call(asset_id: str, to_phone: str, questions: List[str]) -> Optional[str]:
    """Create a Twilio outbound call for a single asset."""
    if not twilio_client:
        logging.error("Twilio client not configured.")
        return None

    params = urlencode({"asset_id": asset_id, "qidx": "0"})
    call_url = f"{HOST_BASE_URL}/twilio/ask?{params}"

    try:
        call = twilio_client.calls.create(
            to=to_phone,
            from_=TWILIO_PHONE_NUMBER,
            url=call_url,
            record=True,
            machine_detection="Enable"
        )
        logging.info(f"Created call SID={call.sid} for asset={asset_id}")
        return call.sid
    except Exception:
        logging.exception("Twilio call creation failed")
        return None

# -------------------------------
# Twilio webhook endpoints
# -------------------------------
@app.route("/twilio/ask", methods=["POST", "GET"])
def twilio_ask():
    """Twilio endpoint: asks questions via <Gather>."""
    asset_id = request.values.get("asset_id")
    qidx = int(request.values.get("qidx", "0"))

    # Load user questions from environment (typed or file)
    user_questions = os.environ.get("USER_DEFINED_QUESTIONS", "")
    user_qs = [q.strip() for q in user_questions.split(";") if q.strip()]
    questions = DEFAULT_PREDEFINED_QUESTIONS + user_qs

    if qidx >= len(questions):
        vr = VoiceResponse()
        vr.say("Thank you for your time. Goodbye.")
        vr.hangup()
        return str(vr)

    question_text = questions[qidx]
    vr = VoiceResponse()
    gather = Gather(input="speech", action=url_for("twilio_gather", _external=True), method="POST", timeout=5)
    gather.say(question_text)
    vr.append(gather)
    vr.say("I did not hear a response. Repeating the question.")
    params = urlencode({"asset_id": asset_id, "qidx": str(qidx)})
    vr.redirect(f"/twilio/ask?{params}")
    return str(vr)


@app.route("/twilio/gather", methods=["POST"])
def twilio_gather():
    """Twilio endpoint: receives speech result, saves, asks next question or summarizes."""
    speech_result = request.values.get("SpeechResult", "").strip()
    asset_id = request.values.get("asset_id") or request.args.get("asset_id") or "unknown"
    try:
        qidx = int(request.values.get("qidx", request.args.get("qidx", "0")))
    except Exception:
        qidx = 0

    user_questions = os.environ.get("USER_DEFINED_QUESTIONS", "")
    user_qs = [q.strip() for q in user_questions.split(";") if q.strip()]
    questions = DEFAULT_PREDEFINED_QUESTIONS + user_qs
    question_text = questions[qidx] if qidx < len(questions) else f"Q{qidx}"

    save_response(asset_id, qidx, question_text, speech_result or "[NO_TRANSCRIPT]")

    vr = VoiceResponse()
    next_qidx = qidx + 1
    if next_qidx < len(questions):
        params = urlencode({"asset_id": asset_id, "qidx": str(next_qidx)})
        vr.redirect(f"/twilio/ask?{params}")
        return str(vr)
    else:
        vr.say("Thank you. We have recorded your answers. Goodbye.")
        vr.hangup()
        # Start transcription + summarization asynchronously
        Thread(target=post_call_finishing, args=(asset_id,), daemon=True).start()
        return str(vr)

# -------------------------------
# Post-call transcription and summarization
# -------------------------------
def post_call_finishing(asset_id: str):
    """
    After call ends: retrieve recording, transcribe via OpenAI Whisper (HTTPS),
    summarize via GPT-4-Turbo (HTTPS), and store in DB.
    """
    logging.info(f"Finishing call for asset_id={asset_id}")
    responses = get_asset_responses(asset_id)

    # 1) Retrieve Twilio recording URL for the asset
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT recording_url FROM assets WHERE id = ?", (asset_id,))
    row = c.fetchone()
    conn.close()
    recording_url = row[0] if row else None

    transcript_text = ""
    if recording_url:
        logging.info(f"Transcribing recording {recording_url} via Whisper API")
        try:
            files = {"file": requests.get(recording_url, stream=True).raw}
            headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
            data = {"model": OPENAI_WHISPER_MODEL}
            r = requests.post("https://api.openai.com/v1/audio/transcriptions", headers=headers, files=files, data=data)
            if r.status_code == 200:
                transcript_text = r.json().get("text", "")
            else:
                logging.warning("Whisper API failed: %s", r.text)
        except Exception:
            logging.exception("Whisper transcription failed")

    # 2) Build summarization prompt
    prompt_lines = [f"Q: {r['question']}\nA: {r['answer']}" for r in responses]
    if transcript_text:
        prompt_lines.append(f"\nFull call transcript:\n{transcript_text}")

    prompt = "Summarize the renter's responses into concise bullets (3-6) and one short paragraph:\n\n"
    prompt += "\n".join(prompt_lines)

    # 3) GPT-4-Turbo summarization via HTTPS
    summary_text = "[NO_SUMMARY]"
    if OPENAI_API_KEY:
        logging.info("Generating summary via GPT-4-Turbo")
        try:
            headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
            body = {
                "model": OPENAI_SUMMARY_MODEL,
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant that summarizes rental agent phone call transcripts."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.2,
                "max_tokens": 400
            }
            r = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, data=json.dumps(body))
            if r.status_code == 200:
                summary_text = r.json()["choices"][0]["message"]["content"].strip()
            else:
                logging.warning("GPT summarization failed: %s", r.text)
        except Exception:
            logging.exception("GPT summarization failed")

    set_asset_summary(asset_id, summary_text)
    logging.info(f"Saved summary for asset {asset_id}")

# -------------------------------
# Twilio recording callback
# -------------------------------
@app.route("/twilio/recording_callback", methods=["POST"])
def twilio_recording_callback():
    """Optional endpoint for Twilio recording events."""
    recording_url = request.values.get("RecordingUrl")
    call_sid = request.values.get("CallSid")
    asset_id = request.values.get("asset_id")
    if asset_id and recording_url:
        set_asset_recording(asset_id, recording_url)
    logging.info(f"Recording callback: callSid={call_sid} recording={recording_url} asset={asset_id}")
    return ("", 204)

# -------------------------------
# Admin endpoint to scrape and call
# -------------------------------
@app.route("/admin/scrape_and_call", methods=["POST"])
def admin_scrape_and_call():
    """
    Trigger scraping and Twilio calls.
    Expects JSON:
    {
      "url": "https://target.site/search",
      "categories": ["2 bedroom", "San Francisco"],
      "user_questions": "Custom Q1;Custom Q2",
      "call_delay_seconds": 2
    }
    """
    payload = request.get_json(force=True)
    url = payload.get("url")
    categories = payload.get("categories", [])
    user_questions = payload.get("user_questions", "")
    call_delay = float(payload.get("call_delay_seconds", 2.0))

    if not url or not categories:
        return jsonify({"error": "url and categories required"}), 400

    os.environ["USER_DEFINED_QUESTIONS"] = user_questions
    assets = scrape_rental_site(url, categories, max_listings=290)

    calls = []
    for asset in assets:
        phone = asset.get("phone")
        if phone and phone.strip().upper() != "N/A":
            sid = create_outbound_call(asset["id"], phone, DEFAULT_PREDEFINED_QUESTIONS)
            calls.append({"asset_id": asset["id"], "phone": phone, "call_sid": sid})
            time.sleep(call_delay)
        else:
            calls.append({"asset_id": asset["id"], "phone": phone, "call_sid": None})

    return jsonify({"assets": assets, "calls": calls})

# -------------------------------
# Dashboard
# -------------------------------
DASH_TEMPLATE = """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Rental Agent Dashboard</title>
    <style>
      body {font-family:"Segoe UI",Arial,sans-serif; max-width:1100px; margin:40px auto; padding:20px; background:#f9f9fb; color:#2c3e50;}
      h1 {font-size:2.2rem; font-weight:700; margin-bottom:10px; text-align:center; color:#2c3e50;}
      p.subtitle {text-align:center; color:#7f8c8d; margin-bottom:50px;} /* increased spacing */
      .asset {border:1px solid #e0e0e0; padding:20px; margin:25px 0; border-radius:12px; background:#fff; box-shadow:0 2px 6px rgba(0,0,0,0.05);}
      .asset h2 {margin-top:0; color:#34495e;}
      .asset .phone {font-weight:600; margin-top:10px; margin-bottom:20px;}
      .asset .description {margin-bottom:20px;}
      .responses {margin-left:20px; margin-bottom:20px;}
      .summary {background:#ecf0f1; padding:10px 15px; border-radius:6px;}
      audio {margin-top:10px;}
    </style>
  </head>
  <body>
    <h1>Rental Agent Dashboard</h1>
    <p class="subtitle">Overview of scraped assets, responses, summaries, and recordings</p>
    {% for asset in assets %}
      <div class="asset">
        <h2>{{ asset.title }}</h2>
        <div class="phone">Phone: {{ asset.phone }}</div>
        <div class="description">{{ asset.description }}</div>
        <div class="responses">
          <strong>Responses:</strong>
          <ul>
            {% for r in asset.responses %}
              <li><b>{{ r.question }}:</b> {{ r.answer }}</li>
            {% endfor %}
          </ul>
        </div>
        <div class="summary">
          <strong>Summary:</strong><br>
          <pre>{{ asset.summary }}</pre>
        </div>
        {% if asset.recording_url %}
          <audio controls src="{{ asset.recording_url }}.mp3"></audio>
        {% endif %}
      </div>
    {% endfor %}
  </body>
</html>
"""

@app.route("/dashboard")
def dashboard():
    """Render the clean dashboard."""
    assets = list_assets()
    for asset in assets:
        asset["responses"] = get_asset_responses(asset["id"])
    return render_template_string(DASH_TEMPLATE, assets=assets)

# -------------------------------
# Main
# -------------------------------
if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)

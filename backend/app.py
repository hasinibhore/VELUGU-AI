"""
backend/app.py  —  Flask API for Velugu
Endpoints: /api/chat, /api/medicines, /api/emergency, /api/alerts
"""

import os
import sys
import json
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Allow imports from project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from database.db import (
    init_db,
    get_medicines, add_medicine, mark_taken, delete_medicine,
    get_emergency_contacts, add_emergency_contact,
    log_interaction, get_active_alerts, resolve_alert,
)

load_dotenv()
app = Flask(__name__)

# ── AI setup ─────────────────────────────────────────────────────────────────

GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")

def ask_gemini(user_message: str) -> str:
    """Send a message to Gemini and return a Telugu reply."""
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")

        system_prompt = (
            "మీరు వృద్ధులకు సహాయం చేసే ఒక స్నేహపూర్వకమైన AI సహాయకుడు పేరు 'వెలుగు'. "
            "ఎల్లప్పుడూ తెలుగులో సమాధానం ఇవ్వండి. "
            "చిన్న, సరళమైన వాక్యాలు ఉపయోగించండి. "
            "వృద్ధుల పట్ల గౌరవంగా మరియు ఆప్యాయంగా మాట్లాడండి. "
            "మందుల గురించి అడిగితే, వైద్యుడిని సంప్రదించమని సలహా ఇవ్వండి. "
            "ప్రమాద సందర్భాల్లో వెంటనే 108కి కాల్ చేయమని చెప్పండి."
        )

        full_prompt = f"{system_prompt}\n\nవినియోగదారు: {user_message}\nవెలుగు:"
        response = model.generate_content(full_prompt)
        return response.text.strip()

    except Exception as e:
        # Fallback responses in Telugu if API fails
        fallback = {
            "medicine": "మీ మందులు సరైన సమయానికి తీసుకోవడం చాలా ముఖ్యం. దయచేసి మీ డాక్టర్‌ను సంప్రదించండి.",
            "default": "క్షమించండి, ఇప్పుడు సమాధానం ఇవ్వలేకపోతున్నాను. దయచేసి కొద్దిసేపు తర్వాత మళ్ళీ అడగండి.",
        }
        msg = user_message.lower()
        if any(w in msg for w in ["medicine", "మందు", "tablet", "మాత్ర"]):
            return fallback["medicine"]
        return fallback["default"]


# ── Health check ──────────────────────────────────────────────────────────────

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "app": "Velugu"})


# ── Chat ──────────────────────────────────────────────────────────────────────

@app.route("/api/chat", methods=["POST"])
def chat():
    data    = request.get_json(force=True)
    message = data.get("message", "").strip()

    if not message:
        return jsonify({"error": "Empty message"}), 400

    # Log and check for confusion
    confused  = log_interaction(message)
    ai_reply  = ask_gemini(message)

    return jsonify({
        "reply":    ai_reply,
        "confused": confused,
    })


# ── Medicines ─────────────────────────────────────────────────────────────────

@app.route("/api/medicines", methods=["GET"])
def list_medicines():
    return jsonify(get_medicines())


@app.route("/api/medicines", methods=["POST"])
def create_medicine():
    d = request.get_json(force=True)
    name       = d.get("name", "").strip()
    dosage     = d.get("dosage", "").strip()
    time_label = d.get("time_label", "").strip()
    if not name:
        return jsonify({"error": "Medicine name required"}), 400
    add_medicine(name, dosage, time_label)
    return jsonify({"ok": True})


@app.route("/api/medicines/<int:med_id>/toggle", methods=["POST"])
def toggle_medicine(med_id):
    mark_taken(med_id)
    return jsonify({"ok": True})


@app.route("/api/medicines/<int:med_id>", methods=["DELETE"])
def remove_medicine(med_id):
    delete_medicine(med_id)
    return jsonify({"ok": True})


# ── Emergency contacts ────────────────────────────────────────────────────────

@app.route("/api/emergency/contacts", methods=["GET"])
def list_contacts():
    return jsonify(get_emergency_contacts())


@app.route("/api/emergency/contacts", methods=["POST"])
def create_contact():
    d        = request.get_json(force=True)
    name     = d.get("name", "").strip()
    phone    = d.get("phone", "").strip()
    relation = d.get("relation", "").strip()
    if not name or not phone:
        return jsonify({"error": "Name and phone required"}), 400
    add_emergency_contact(name, phone, relation)
    return jsonify({"ok": True})


@app.route("/api/emergency/trigger", methods=["POST"])
def trigger_emergency():
    """
    In a real app this would send SMS via Twilio / WhatsApp.
    For the hackathon demo we return the contacts so the UI
    can display a realistic 'Alert sent' confirmation.
    """
    contacts = get_emergency_contacts()
    return jsonify({
        "ok":      True,
        "message": "అత్యవసర హెచ్చరిక పంపబడింది!",
        "contacts": contacts,
    })


# ── Caregiver alerts (confusion detection) ────────────────────────────────────

@app.route("/api/alerts", methods=["GET"])
def list_alerts():
    return jsonify(get_active_alerts())


@app.route("/api/alerts/<int:alert_id>/resolve", methods=["POST"])
def resolve(alert_id):
    resolve_alert(alert_id)
    return jsonify({"ok": True})


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    print("✅  Database initialised")
    print("🚀  Velugu API running on http://localhost:5000")
    app.run(debug=True, port=5000)
"""
frontend/app.py  —  Velugu Streamlit UI
Telugu AI Companion for Elderly Users

Run: streamlit run frontend/app.py
(Flask backend must be running on port 5000 first)
"""

import streamlit as st
import requests
import sys, os

# Allow TTS import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from backend.tts import text_to_audio_b64, audio_html

API = "http://localhost:5000/api"

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="వెలుగు — పెద్దల AI సహాయకుడు",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Global styles ─────────────────────────────────────────────────────────────

st.markdown("""
<style>
/* ── Base typography & colours ───────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Telugu:wght@400;600;700&family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Noto Sans Telugu', 'Inter', sans-serif !important;
    background: #0f1117;
    color: #e8e6df;
}

/* Streamlit default padding fix */
.block-container { padding: 1.5rem 2rem 2rem !important; max-width: 1200px; }

/* ── Header bar ──────────────────────────────────────────────────────────── */
.velugu-header {
    background: linear-gradient(135deg, #1a1f2e 0%, #0f1117 100%);
    border: 1px solid #2a2f3e;
    border-radius: 16px;
    padding: 20px 28px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    gap: 16px;
}
.velugu-header .logo { font-size: 2.4rem; }
.velugu-header .title-block h1 {
    font-size: 1.8rem;
    font-weight: 700;
    color: #f9c74f;
    margin: 0;
    line-height: 1.2;
}
.velugu-header .title-block p {
    font-size: 0.9rem;
    color: #8a8f9e;
    margin: 4px 0 0;
}

/* ── Nav tabs ────────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: transparent;
    border-bottom: 1px solid #2a2f3e;
    padding-bottom: 0;
}
.stTabs [data-baseweb="tab"] {
    font-size: 1.05rem !important;
    font-weight: 600 !important;
    padding: 12px 24px !important;
    border-radius: 10px 10px 0 0 !important;
    color: #8a8f9e !important;
    background: transparent !important;
    border: none !important;
}
.stTabs [aria-selected="true"] {
    color: #f9c74f !important;
    background: #1a1f2e !important;
    border-bottom: 3px solid #f9c74f !important;
}

/* ── Big action buttons ──────────────────────────────────────────────────── */
.stButton > button {
    border-radius: 12px !important;
    font-size: 1.1rem !important;
    font-weight: 600 !important;
    padding: 14px 20px !important;
    transition: transform 0.1s, box-shadow 0.1s !important;
    width: 100%;
    min-height: 56px;
}
.stButton > button:active { transform: scale(0.97); }

/* Primary (yellow) buttons */
.primary-btn > button {
    background: #f9c74f !important;
    color: #0f1117 !important;
    border: none !important;
    font-size: 1.2rem !important;
}
.primary-btn > button:hover { box-shadow: 0 4px 20px rgba(249,199,79,0.4) !important; }

/* Emergency button */
.emergency-btn > button {
    background: #e63946 !important;
    color: white !important;
    border: none !important;
    font-size: 1.5rem !important;
    min-height: 80px !important;
    border-radius: 16px !important;
    letter-spacing: 0.02em;
}
.emergency-btn > button:hover { box-shadow: 0 4px 24px rgba(230,57,70,0.5) !important; }

/* Success (green) buttons */
.success-btn > button {
    background: #2d6a4f !important;
    color: #d8f3dc !important;
    border: 1px solid #40916c !important;
}

/* Taken toggle */
.taken-btn > button {
    background: #1b4332 !important;
    color: #95d5b2 !important;
    border: 1px solid #40916c !important;
    font-size: 0.95rem !important;
    min-height: 44px !important;
    padding: 8px 16px !important;
}
.nottaken-btn > button {
    background: #1a1f2e !important;
    color: #8a8f9e !important;
    border: 1px solid #2a2f3e !important;
    font-size: 0.95rem !important;
    min-height: 44px !important;
    padding: 8px 16px !important;
}

/* ── Card components ─────────────────────────────────────────────────────── */
.med-card {
    background: #1a1f2e;
    border: 1px solid #2a2f3e;
    border-radius: 14px;
    padding: 18px 20px;
    margin-bottom: 12px;
}
.med-card.taken {
    border-color: #40916c;
    background: #0d2218;
}
.med-name { font-size: 1.2rem; font-weight: 700; color: #e8e6df; }
.med-meta { font-size: 0.9rem; color: #8a8f9e; margin-top: 4px; }

.chat-bubble-user {
    background: #f9c74f;
    color: #0f1117;
    border-radius: 18px 18px 4px 18px;
    padding: 12px 18px;
    margin: 8px 0;
    max-width: 80%;
    margin-left: auto;
    font-size: 1.05rem;
    font-weight: 500;
}
.chat-bubble-ai {
    background: #1a1f2e;
    border: 1px solid #2a2f3e;
    color: #e8e6df;
    border-radius: 18px 18px 18px 4px;
    padding: 12px 18px;
    margin: 8px 0;
    max-width: 80%;
    font-size: 1.05rem;
    line-height: 1.6;
}

.confusion-alert {
    background: #3d1f00;
    border: 2px solid #f4a261;
    border-radius: 14px;
    padding: 16px 20px;
    margin: 12px 0;
}
.confusion-alert .alert-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #f4a261;
}
.confusion-alert .alert-body {
    font-size: 0.95rem;
    color: #e8c99a;
    margin-top: 4px;
}

.emergency-panel {
    background: #200a0b;
    border: 2px solid #e63946;
    border-radius: 16px;
    padding: 24px;
    text-align: center;
    margin-bottom: 20px;
}
.emergency-panel .ep-title {
    font-size: 1.4rem;
    font-weight: 700;
    color: #e63946;
    margin-bottom: 8px;
}
.emergency-panel .ep-sub {
    font-size: 0.95rem;
    color: #c9a0a3;
}

.contact-card {
    background: #1a1f2e;
    border: 1px solid #2a2f3e;
    border-radius: 12px;
    padding: 14px 18px;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 14px;
}
.contact-avatar {
    width: 44px; height: 44px;
    background: #2d3561;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.3rem; font-weight: 700; color: #a5b4fc;
    flex-shrink: 0;
}

/* ── Input overrides ─────────────────────────────────────────────────────── */
.stTextInput input, .stTextArea textarea, .stSelectbox select {
    background: #1a1f2e !important;
    border: 1px solid #2a2f3e !important;
    border-radius: 10px !important;
    color: #e8e6df !important;
    font-size: 1rem !important;
    padding: 12px 16px !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #f9c74f !important;
    box-shadow: 0 0 0 2px rgba(249,199,79,0.2) !important;
}

/* ── Section headers ─────────────────────────────────────────────────────── */
.section-head {
    font-size: 1.1rem;
    font-weight: 700;
    color: #f9c74f;
    margin: 20px 0 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid #2a2f3e;
}

/* ── Streamlit component spacing ────────────────────────────────────────── */
div[data-testid="stVerticalBlock"] > div { gap: 0 !important; }
.stMarkdown p { margin: 0 !important; }
</style>
""", unsafe_allow_html=True)


# ── Session state init ────────────────────────────────────────────────────────

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {
            "role": "ai",
            "text": "నమస్కారం! నేను వెలుగు, మీ AI సహాయకుడు. మీకు ఏ విధంగా సహాయం చేయాలి? 🙏",
        }
    ]
if "confusion_alerts" not in st.session_state:
    st.session_state.confusion_alerts = []
if "emergency_triggered" not in st.session_state:
    st.session_state.emergency_triggered = False


# ── Helper: call Flask API ────────────────────────────────────────────────────

def api(method: str, path: str, **kwargs):
    try:
        r = getattr(requests, method)(f"{API}{path}", timeout=15, **kwargs)
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error("⚠️ Flask backend is not running. Start it with: python backend/app.py")
        return None
    except Exception as e:
        st.error(f"API error: {e}")
        return None


# ── Header ────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="velugu-header">
  <div class="logo">🌟</div>
  <div class="title-block">
    <h1>వెలుగు</h1>
    <p>పెద్దల కోసం తెలుగు AI సహాయకుడు · Telugu AI Companion for Elderly</p>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Confusion alert banner (persistent) ──────────────────────────────────────

alerts_data = api("get", "/alerts")
if alerts_data:
    for alert in alerts_data:
        st.markdown(f"""
        <div class="confusion-alert">
          <div class="alert-title">⚠️ జాగ్రత్త హెచ్చరిక — కేర్‌గివర్ అలర్ట్</div>
          <div class="alert-body">
            వినియోగదారు అదే ప్రశ్న పదే పదే అడుగుతున్నారు:<br>
            <strong>"{alert['query']}"</strong><br>
            సమయం: {alert['alert_time'][:16]}
          </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("✅ అలర్ట్ పరిష్కరించండి", key=f"resolve_{alert['id']}"):
            api("post", f"/alerts/{alert['id']}/resolve")
            st.rerun()

# ── Main tabs ─────────────────────────────────────────────────────────────────

tab_chat, tab_meds, tab_emergency, tab_info = st.tabs([
    "💬 మాట్లాడు",
    "💊 మందులు",
    "🚨 అత్యవసరం",
    "ℹ️ సమాచారం",
])


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — AI CHAT
# ═══════════════════════════════════════════════════════════════════════════════

with tab_chat:
    st.markdown('<div class="section-head">AI సహాయకుడితో మాట్లాడండి</div>', unsafe_allow_html=True)

    # Chat history display
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(
                    f'<div class="chat-bubble-user">{msg["text"]}</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<div class="chat-bubble-ai">🤖 {msg["text"]}</div>',
                    unsafe_allow_html=True,
                )

    st.markdown("---")

    # Quick-reply buttons (common elderly queries)
    st.markdown('<div class="section-head" style="font-size:0.95rem">త్వరిత ప్రశ్నలు</div>', unsafe_allow_html=True)
    qcols = st.columns(3)
    quick = [
        ("💊 మందు తీసుకున్నానా?", "నేను ఈరోజు మందు తీసుకున్నానా?"),
        ("🌡️ వాతావరణం?", "ఈరోజు వాతావరణం ఎలా ఉంది?"),
        ("🕐 సమయం?", "ఇప్పుడు సమయం ఎంత?"),
        ("😔 ఒంట్లో బాగాలేదు", "నాకు ఒంట్లో బాగాలేదు, ఏం చేయాలి?"),
        ("🙏 ఒంటరిగా అనిపిస్తోంది", "నాకు చాలా ఒంటరిగా అనిపిస్తోంది"),
        ("📞 ఫోన్ చేయాలి", "కొడుకు/కూతురుకు ఫోన్ ఎలా చేయాలి?"),
    ]
    for i, (label, query) in enumerate(quick):
        with qcols[i % 3]:
            if st.button(label, key=f"quick_{i}"):
                st.session_state.pending_query = query

    # Text input
    user_input = st.text_input(
        "",
        placeholder="మీ ప్రశ్న ఇక్కడ టైప్ చేయండి... (Type your question in Telugu or English)",
        key="chat_input",
        label_visibility="collapsed",
    )

    send_col, clear_col = st.columns([4, 1])
    with send_col:
        with st.container():
            st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
            send_clicked = st.button("📨 పంపు (Send)", key="send_btn")
            st.markdown("</div>", unsafe_allow_html=True)
    with clear_col:
        if st.button("🗑️ క్లియర్", key="clear_btn"):
            st.session_state.chat_history = [
                {"role": "ai", "text": "నమస్కారం! నేను వెలుగు. మీకు ఏ విధంగా సహాయం చేయాలి? 🙏"}
            ]
            st.rerun()

    # Handle quick buttons
    if "pending_query" in st.session_state:
        query = st.session_state.pop("pending_query")
        _send_message(query) if False else None  # Placeholder — handled below

    # Process message
    final_query = None
    if send_clicked and user_input:
        final_query = user_input
    elif "pending_query" in st.session_state:
        final_query = st.session_state.pop("pending_query")

    if final_query:
        st.session_state.chat_history.append({"role": "user", "text": final_query})
        with st.spinner("వెలుగు ఆలోచిస్తోంది..."):
            result = api("post", "/chat", json={"message": final_query})

        if result:
            reply = result.get("reply", "క్షమించండి, మళ్ళీ ప్రయత్నించండి.")
            confused = result.get("confused", False)
            st.session_state.chat_history.append({"role": "ai", "text": reply})

            if confused:
                st.session_state.confusion_alerts.append(final_query)

            # Play Telugu TTS
            audio_b64 = text_to_audio_b64(reply, lang="te")
            if audio_b64:
                st.markdown(audio_html(audio_b64), unsafe_allow_html=True)

        st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — MEDICINES
# ═══════════════════════════════════════════════════════════════════════════════

with tab_meds:
    st.markdown('<div class="section-head">ఈరోజు మందులు</div>', unsafe_allow_html=True)

    meds = api("get", "/medicines")

    if meds:
        taken_count = sum(1 for m in meds if m["taken_today"])
        total_count = len(meds)

        # Progress summary
        prog_pct = int((taken_count / total_count) * 100) if total_count else 0
        prog_col1, prog_col2 = st.columns([3, 1])
        with prog_col1:
            st.progress(prog_pct / 100)
        with prog_col2:
            st.markdown(
                f'<p style="text-align:right;color:#f9c74f;font-weight:700">{taken_count}/{total_count} తీసుకున్నారు</p>',
                unsafe_allow_html=True,
            )

        # Medicine cards
        for med in meds:
            taken = bool(med["taken_today"])
            card_class = "med-card taken" if taken else "med-card"
            st.markdown(f"""
            <div class="{card_class}">
              <div class="med-name">{'✅ ' if taken else '⬜ '}{med['name']}</div>
              <div class="med-meta">
                {'💊 ' + med['dosage'] if med['dosage'] else ''}
                {'&nbsp;&nbsp;🕐 ' + med['time_label'] if med['time_label'] else ''}
              </div>
            </div>
            """, unsafe_allow_html=True)

            btn_col1, btn_col2 = st.columns([3, 1])
            with btn_col1:
                label = "✅ తీసుకున్నాను (Taken)" if not taken else "↩️ తీసుకోలేదు (Undo)"
                div_class = "taken-btn" if not taken else "nottaken-btn"
                st.markdown(f'<div class="{div_class}">', unsafe_allow_html=True)
                if st.button(label, key=f"taken_{med['id']}"):
                    api("post", f"/medicines/{med['id']}/toggle")
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
            with btn_col2:
                if st.button("🗑️", key=f"del_{med['id']}", help="మందు తొలగించు"):
                    api("delete", f"/medicines/{med['id']}")
                    st.rerun()
    else:
        st.info("మందులు ఏవీ జోడించబడలేదు.")

    # Add new medicine
    st.markdown('<div class="section-head">కొత్త మందు జోడించండి</div>', unsafe_allow_html=True)
    with st.expander("➕ మందు జోడించు", expanded=False):
        m1, m2, m3 = st.columns(3)
        with m1:
            new_name = st.text_input("మందు పేరు *", placeholder="ఉదా: మెట్‌ఫార్మిన్")
        with m2:
            new_dosage = st.text_input("మోతాదు", placeholder="ఉదా: 500mg")
        with m3:
            new_time = st.selectbox(
                "సమయం",
                ["ఉదయం", "మధ్యాహ్నం", "రాత్రి", "అవసరమైనప్పుడు"],
            )
        st.markdown('<div class="success-btn">', unsafe_allow_html=True)
        if st.button("💊 మందు సేవ్ చేయండి", key="save_med"):
            if new_name:
                api("post", "/medicines", json={
                    "name": new_name,
                    "dosage": new_dosage,
                    "time_label": new_time,
                })
                st.success(f"✅ '{new_name}' జోడించబడింది!")
                st.rerun()
            else:
                st.error("మందు పేరు అవసరం.")
        st.markdown("</div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — EMERGENCY
# ═══════════════════════════════════════════════════════════════════════════════

with tab_emergency:

    if st.session_state.emergency_triggered:
        st.markdown("""
        <div style="background:#0d2218;border:2px solid #40916c;border-radius:16px;padding:28px;text-align:center;margin-bottom:20px">
          <div style="font-size:2.5rem">✅</div>
          <div style="font-size:1.4rem;font-weight:700;color:#40916c;margin-top:8px">హెచ్చరిక పంపబడింది!</div>
          <div style="color:#95d5b2;margin-top:8px">మీ కుటుంబ సభ్యులకు అత్యవసర హెచ్చరిక పంపబడింది.<br>
          వారు త్వరలో మీకు కాల్ చేస్తారు.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🔄 తిరిగి వెళ్ళు", key="reset_emergency"):
            st.session_state.emergency_triggered = False
            st.rerun()

    else:
        st.markdown("""
        <div class="emergency-panel">
          <div class="ep-title">🚨 అత్యవసర సహాయం</div>
          <div class="ep-sub">
            ప్రమాదం లేదా అత్యవసర పరిస్థితిలో దిగువ బటన్ నొక్కండి.<br>
            మీ కుటుంబ సభ్యులకు వెంటనే సమాచారం అందుతుంది.
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="emergency-btn">', unsafe_allow_html=True)
        if st.button("🆘  అత్యవసర హెచ్చరిక పంపండి  🆘", key="emergency_main"):
            result = api("post", "/emergency/trigger")
            if result:
                st.session_state.emergency_triggered = True
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(
            '<p style="text-align:center;font-size:0.85rem;color:#8a8f9e;margin-top:8px">'
            'జాతీయ అత్యవసర నంబర్: <strong style="color:#e63946">108</strong> &nbsp;|&nbsp; '
            'పోలీస్: <strong style="color:#e63946">100</strong>'
            "</p>",
            unsafe_allow_html=True,
        )

    # Contacts list
    st.markdown('<div class="section-head">అత్యవసర పరిచయాలు</div>', unsafe_allow_html=True)
    contacts = api("get", "/emergency/contacts")
    if contacts:
        for c in contacts:
            initials = c["name"][0].upper() if c["name"] else "?"
            st.markdown(f"""
            <div class="contact-card">
              <div class="contact-avatar">{initials}</div>
              <div>
                <div style="font-weight:700;font-size:1rem">{c['name']}</div>
                <div style="color:#8a8f9e;font-size:0.9rem">{c['phone']}
                  {'&nbsp;·&nbsp;' + c['relation'] if c.get('relation') else ''}
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("అత్యవసర పరిచయాలు ఏవీ జోడించబడలేదు.")

    # Add contact
    with st.expander("➕ కొత్త పరిచయం జోడించండి"):
        cc1, cc2, cc3 = st.columns(3)
        with cc1:
            c_name = st.text_input("పేరు *", key="c_name")
        with cc2:
            c_phone = st.text_input("ఫోన్ నంబర్ *", key="c_phone", placeholder="+91 XXXXX XXXXX")
        with cc3:
            c_rel = st.text_input("సంబంధం", key="c_rel", placeholder="ఉదా: కొడుకు")
        if st.button("💾 పరిచయం సేవ్ చేయండి", key="save_contact"):
            if c_name and c_phone:
                api("post", "/emergency/contacts", json={
                    "name": c_name, "phone": c_phone, "relation": c_rel
                })
                st.success("✅ పరిచయం జోడించబడింది!")
                st.rerun()
            else:
                st.error("పేరు మరియు ఫోన్ నంబర్ అవసరం.")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — INFO / DAILY TIPS
# ═══════════════════════════════════════════════════════════════════════════════

with tab_info:
    st.markdown('<div class="section-head">ఈరోజు ఆరోగ్య సలహాలు</div>', unsafe_allow_html=True)

    tips = [
        ("💧", "నీళ్ళు తాగండి", "రోజూ 8 గ్లాసుల నీళ్ళు తాగడం చాలా అవసరం."),
        ("🚶", "నడక చేయండి", "ప్రతిరోజూ 30 నిమిషాలు నడవడం గుండెకు మంచిది."),
        ("🌿", "కూరగాయలు తినండి", "రోజువారీ భోజనంలో తాజా కూరగాయలు చేర్చండి."),
        ("😴", "సరిగ్గా నిద్రపోండి", "రాత్రి 7-8 గంటలు నిద్ర చాలా ముఖ్యం."),
        ("🧘", "ధ్యానం చేయండి", "రోజూ 10 నిమిషాలు ధ్యానం ఒత్తిడిని తగ్గిస్తుంది."),
        ("👨‍⚕️", "డాక్టర్‌ను సందర్శించండి", "నెలకు ఒకసారి వైద్యుడిని కలవడం మంచిది."),
    ]

    col1, col2 = st.columns(2)
    for i, (icon, title, desc) in enumerate(tips):
        with (col1 if i % 2 == 0 else col2):
            st.markdown(f"""
            <div style="background:#1a1f2e;border:1px solid #2a2f3e;border-radius:12px;
                        padding:16px;margin-bottom:12px;display:flex;gap:14px;align-items:flex-start">
              <div style="font-size:1.8rem;line-height:1">{icon}</div>
              <div>
                <div style="font-weight:700;font-size:1rem;color:#e8e6df">{title}</div>
                <div style="font-size:0.9rem;color:#8a8f9e;margin-top:4px">{desc}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div class="section-head" style="margin-top:24px">వెలుగు గురించి</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="background:#1a1f2e;border:1px solid #2a2f3e;border-radius:14px;padding:20px;line-height:1.8;color:#c8c6bf">
      <p><strong style="color:#f9c74f">వెలుగు</strong> అంటే తెలుగులో 'వెలుతురు' అని అర్థం.</p>
      <p>ఈ యాప్ పెద్దలకు వారి రోజువారీ జీవితంలో సహాయం చేయడానికి రూపొందించబడింది:</p>
      <p>✅ తెలుగులో AI సంభాషణ<br>
         ✅ మందుల రిమైండర్లు<br>
         ✅ అత్యవసర హెచ్చరిక వ్యవస్థ<br>
         ✅ గందరగోళ గుర్తింపు (Confusion Detection)<br>
         ✅ కేర్‌గివర్ అలర్ట్ వ్యవస్థ</p>
      <p style="color:#8a8f9e;font-size:0.85rem;margin-top:12px">
        Swecha Hackathon 2024 · Built with ❤️ for Telugu elders
      </p>
    </div>
    """, unsafe_allow_html=True)
import streamlit as st
import pandas as pd
import json
from datetime import datetime
from ml.suggest import recommend_action
import random
import openai
import os

# Inject CSS styling
st.markdown("""
    <style>
    body {
        background-color: #F5F7FA;
        color: #333C4F;
        font-family: 'Inter', sans-serif;
    }
    .stButton>button {
        background-color: #4A90E2;
        color: white;
        border-radius: 20px;
        padding: 10px 20px;
        font-weight: bold;
        border: none;
        transition: background-color 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #3f7ac9;
    }
    .stRadio label {
        font-size: 18px;
        padding: 6px 10px;
    }
    .stMarkdown {
        background-color: #FFFFFF;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    .stSubheader, .stInfo, .stSuccess {
        margin-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="RebootMe", layout="centered")
st.title("🔄 RebootMe - Refresh Your Mind")

# Load stretches
with open("assets/stretches.json") as f:
    stretches = json.load(f)

# Initialize state
if "water_count" not in st.session_state:
    st.session_state.water_count = 0
if "mood" not in st.session_state:
    st.session_state.mood = None
if "stretched" not in st.session_state:
    st.session_state.stretched = False
if "last_stretch_reminder" not in st.session_state:
    st.session_state.last_stretch_reminder = datetime.now()
if "last_eye_reminder" not in st.session_state:
    st.session_state.last_eye_reminder = datetime.now()

# Notification via browser JS
def send_browser_notification(title, message):
    st.components.v1.html(f"""
        <script>
            Notification.requestPermission().then(function(permission) {{
                if (permission === "granted") {{
                    new Notification("{title}", {{ body: "{message}" }});
                }}
            }});
        </script>
    """, height=0)

# Load OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_ai_quote():
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a wellness coach who gives short motivational quotes for mental wellbeing."},
                {"role": "user", "content": "Give me one short motivational quote to boost my mood today."}
            ]
        )
        return response.choices[0].message.content.strip()
    except:
        fallback_quotes = [
            "You are stronger than you think, and braver than you feel.",
            "Your mind is a powerful thing. Fill it with positive thoughts.",
            "Small steps every day lead to big changes.",
            "It's okay to rest. Don't forget to care for yourself.",
            "You are doing your best, and that is enough.",
            "Every day may not be good, but there is something good in every day."
        ]
        return random.choice(fallback_quotes)

# Hydration Tracker
st.subheader("💧 Hydration Tracker")
if st.button("Drink Water"):
    st.session_state.water_count += 1
    send_browser_notification("RebootMe Reminder", "Great! You drank water 💧")
st.write(f"Water Count Today: {st.session_state.water_count} glasses")

# Stretch Suggestion
st.subheader("🙆 Stretch Now")
selected_stretch = stretches[datetime.now().minute % len(stretches)]
st.markdown(f"**{selected_stretch['name']}** - {selected_stretch['description']} ({selected_stretch['duration']})")
if st.button("Mark Stretch Done"):
    st.session_state.stretched = True
    send_browser_notification("RebootMe Reminder", "Nice! You stretched 🧘")

# Mood Check-In
st.subheader("😊 Mood Check")
mood_emojis = ["😔", "😐", "🙂", "😃", "🤩"]
mood = st.radio("How are you feeling?", mood_emojis)
mood_score = mood_emojis.index(mood)
st.session_state.mood = mood_score

# Tips per mood
MOOD_TIPS = {
    "😔": "Take a deep breath and do a 5-minute guided meditation.",
    "😐": "Listen to calming music and write down 3 good things.",
    "🙂": "Maintain this calm by walking outside for a few minutes.",
    "😃": "Share your smile with someone today — it doubles your joy.",
    "🤩": "You're glowing! Use this energy to plan something you love."
}

today_tip = MOOD_TIPS.get(mood, "Remember, your well-being matters.")

# AI-generated motivational quote
ai_quote = get_ai_quote()

# Suggestion (mood-based tip)
st.subheader("🧠 Wellness Tip")
st.info(today_tip)

st.subheader("📊 Daily Mood Booster")
st.success(f"✨ {ai_quote}")
send_browser_notification("Daily Mental Boost", ai_quote)

# Save Log
if st.button("Save Today's Log"):
    try:
        log = pd.read_csv("data/log.csv")
    except FileNotFoundError:
        log = pd.DataFrame(columns=["timestamp", "mood", "water", "stretched"])

    new_row = {
        "timestamp": datetime.now(),
        "mood": mood_score,
        "water": st.session_state.water_count,
        "stretched": st.session_state.stretched
    }
    log = pd.concat([log, pd.DataFrame([new_row])], ignore_index=True)
    log.to_csv("data/log.csv", index=False)
    st.success("Saved! ✅")

# Show chart
if st.checkbox("📈 Show History"):
    log = pd.read_csv("data/log.csv")
    st.line_chart(log[['mood', 'water']])

import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime, timedelta
import pytz
import time

st.set_page_config(page_title="Realtime Chat", layout="centered")

# 🔐 Load Firebase credentials
firebase_secrets = dict(st.secrets["firebase"])
database_url = f"https://{firebase_secrets['project_id']}-default-rtdb.firebaseio.com/"

# 🔌 Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_secrets)
    firebase_admin.initialize_app(cred, {
        'databaseURL': database_url
    })

ref = db.reference("messages")

# 🧹 Delete messages older than 2 days
def delete_old_messages():
    messages = ref.get() or {}
    now = datetime.now(pytz.utc)
    for key, msg in messages.items():
        try:
            msg_time = datetime.fromisoformat(msg["timestamp"])
            if now - msg_time > timedelta(days=2):
                ref.child(key).delete()
        except Exception:
            continue

# 💬 Display messages in white chat bubbles with black text
def display_messages(current_user):
    messages = ref.order_by_child("timestamp").get()
    if messages:
        for msg in messages.values():
            user = msg["user"]
            text = msg["text"]
            time_stamp = msg["timestamp"]

            is_self = user == current_user
            align = "flex-end" if is_self else "flex-start"
            text_align = "right" if is_self else "left"

            bubble = f"""
            <div style="display: flex; justify-content: {align}; margin-bottom: 12px;">
                <div style="
                    background-color: white;
                    padding: 12px 16px;
                    border-radius: 12px;
                    max-width: 70%;
                    word-wrap: break-word;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                    font-family: 'Segoe UI', sans-serif;
                    text-align: {text_align};
                ">
                    <strong style="color: #1b5e20;">{user}</strong><br>
                    <div style="margin: 6px 0; color: black; font-size: 15px;">{text}</div>
                    <span style="font-size: 11px; color: #555;">{time_stamp}</span>
                </div>
            </div>
            """
            st.markdown(bubble, unsafe_allow_html=True)

# 🖥️ Chat UI
st.title("💬 Real-Time Chatroom")

username = st.text_input("Enter your name to join the chat 👇", key="username")

if username:
    message = st.text_input("Type your message", key="message")
    if st.button("Send") and message:
        timestamp = datetime.now(pytz.utc).isoformat()
        try:
            ref.push({
                "user": username,
                "text": message,
                "timestamp": timestamp
            })
            st.rerun()
        except Exception as e:
            st.error(f"⚠️ Failed to send message: {e}")

    try:
        delete_old_messages()
        st.subheader("🔴 Live Chat")
        display_messages(username)
        time.sleep(2)
        st.rerun()
    except Exception as e:
        st.error(f"⚠️ Failed to load messages: {e}")
else:
    st.info("Please enter your name to view and send messages.")

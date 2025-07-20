import streamlit as st
import json
import os
import hashlib
import tempfile
import queue
import threading
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, VideoProcessorBase
import av

from recipe_store import save_recipe, recipe_exists, search_recipes_by_dish
from geo_utils import get_coordinates
from voice_utils import transcribe_audio

USERS_FILE = "data/users.json"

# Audio Recording Queue
audio_queue = queue.Queue()
class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.recording = []

    def recv(self, frame):
        audio_queue.put(frame.to_ndarray())
        return frame

# Video Capture Stub
class VideoProcessor(VideoProcessorBase):
    def recv(self, frame):
        return frame

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_user(username, password):
    users = load_users()
    if username in users:
        return False
    users[username] = hash_password(password)
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)
    return True

def login_form():
    st.subheader("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        users = load_users()
        hashed_input = hash_password(password)
        if username in users and users[username] == hashed_input:
            st.success(f"Welcome {username}!")
            return username
        else:
            st.error("Invalid username or password.")
    return None

def register_form():
    st.subheader("📝 Register")
    username = st.text_input("New Username")
    password = st.text_input("New Password", type="password")
    confirm = st.text_input("Confirm Password", type="password")
    if st.button("Register"):
        if password != confirm:
            st.error("Passwords do not match!")
        elif save_user(username, password):
            st.success("User registered! Please login.")
        else:
            st.warning("Username already exists.")

def record_audio():
    webrtc_streamer(
        key="audio",
        mode="SENDRECV",
        media_stream_constraints={"audio": True, "video": False},
        audio_processor_factory=AudioProcessor,
        async_processing=True,
    )
    st.info("Recording... Speak now")

def capture_video():
    webrtc_streamer(
        key="video",
        mode="SENDRECV",
        media_stream_constraints={"video": True, "audio": False},
        video_processor_factory=VideoProcessor,
        async_processing=False,
    )
    st.info("Capturing video... Show your preparation")

def recipe_submission_form(logged_user):
    st.subheader("🍲 Submit a Festival Recipe")

    name = st.text_input("Your Name", value=logged_user)
    dish = st.text_input("Dish Name")
    language = st.selectbox("Language", ["Telugu", "Hindi", "Tamil", "Bengali", "Marathi", "Kannada"])
    festival = st.text_input("Festival (optional)")
    ingredients = st.text_area("Ingredients (comma separated)")
    instructions = ""

    use_voice = st.checkbox("🎤 Record Instructions using Microphone")
    if use_voice:
        record_audio()
        if st.button("Transcribe Audio"):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
                # Assume `voice_utils` handles audio_queue to .wav
                tmp_path = f.name
            instructions = transcribe_audio(tmp_path)
            st.success("Transcription complete")
    else:
        instructions = st.text_area("Instructions")

    st.markdown("---")
    st.markdown("🎥 **Record Recipe Preparation Video (Optional)**")
    capture_video()

    image = st.file_uploader("Upload Image (optional)", type=["jpg", "jpeg", "png"])

    submit = st.button("Submit Recipe")

    if submit:
        if not dish.strip() or not language.strip() or not instructions.strip():
            st.warning("Dish name, language, and instructions are mandatory.")
            return False, dish, language, ingredients, instructions, (0.0, 0.0)

        if recipe_exists(name, dish):
            st.warning("Recipe already exists!")
            return False, dish, language, ingredients, instructions, (0.0, 0.0)

        lat, lon = get_coordinates()
        save_recipe(name, festival, dish, language, ingredients, instructions, image, lat, lon)
        st.success("Recipe submitted successfully!")
        return True, dish, language, ingredients, instructions, (lat, lon)

    return False, dish, language, ingredients, instructions, (0.0, 0.0)

def search_recipes():
    st.subheader("🔍 Search Recipes")
    query = st.text_input("Enter Dish Name")
    if st.button("Search"):
        if query:
            matches = search_recipes_by_dish(query)
            if matches:
                for r in matches:
                    st.markdown(f"### {r.dish} ({r.language})")
                    st.text(f"Festival: {r.festival or 'N/A'}")
                    st.text(f"By: {r.name}")
                    st.markdown(f"**Instructions:** {r.instructions}")
                    if r.image:
                        st.image(r.image, caption="Dish Image", use_container_width=True)
                    if r.video:
                        st.video(r.video)
                    if r.audio:
                        st.audio(r.audio, format="audio/wav")

            else:
                st.info("No recipes found.")
        else:
            st.warning("Please enter a dish name.")

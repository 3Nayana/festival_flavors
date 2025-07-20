import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import tempfile

from src.components import login_form, register_form
from src.geo_utils import get_coordinates
from src.recipe_store import save_recipe, recipe_exists, search_recipes_by_dish

st.set_page_config(page_title="Festival Flavors", layout="centered")
st.title("🎉 Festival Flavors")

# --- Session Init ---
if "user" not in st.session_state:
    st.session_state["user"] = None

# --- Navigation ---
tab = st.sidebar.radio("Navigate", [
    "Login",
    "Register",
    "Submit Recipe",
    "Voice Input",
    "Search Recipes",
    "Logout" if st.session_state["user"] else None
])

# --- Authentication ---
if tab == "Register":
    register_form()

elif tab == "Login":
    if not st.session_state["user"]:
        user = login_form()
        if user:
            st.session_state["user"] = user
            st.success(f"Welcome, {user}!")
            st.rerun()
    else:
        st.success(f"You're logged in as **{st.session_state['user']}**.")

elif tab == "Logout":
    st.session_state["user"] = None
    st.success("Logged out successfully.")
    st.rerun()

# --- Recipe Submission ---
elif tab == "Submit Recipe":
    if not st.session_state["user"]:
        st.warning("⚠️ Please login first to submit a recipe.")
    else:
        st.subheader("📋 Submit Your Recipe")

        name = st.session_state["user"]
        festival = st.text_input("Festival (optional)")
        dish = st.text_input("Dish Name *")
        language = st.text_input("Language *")
        ingredients = st.text_area("Ingredients")
        instructions = st.text_area("Instructions *")

        image_file = st.file_uploader("📷 Upload Dish Image", type=["jpg", "jpeg", "png"])
        video_file = st.file_uploader("🎥 Upload Recipe Video", type=["mp4", "mov", "avi"])

        if st.checkbox("📍 Auto-detect location"):
            coords = get_coordinates()
            lat, lon = coords if coords else (None, None)
            if coords:
                st.success(f"Location detected: ({lat}, {lon})")
            else:
                st.warning("Could not detect location.")
        else:
            lat = st.number_input("Latitude (optional)", format="%.6f")
            lon = st.number_input("Longitude (optional)", format="%.6f")

        if st.button("Submit Recipe"):
            if not dish or not language or not instructions:
                st.error("❗ Dish name, language, and instructions are required.")
            elif recipe_exists(name, dish):
                st.warning("⚠️ A recipe with this dish name already exists under your name.")
            else:
                image_bytes = image_file.read() if image_file else None
                video_bytes = video_file.read() if video_file else None

                save_recipe(name, festival, dish, language, ingredients, instructions,
                            image_bytes, lat, lon, video_bytes)
                st.success("✅ Recipe submitted successfully!")

# --- Voice Input (Upload) ---
elif tab == "Voice Input":
    if not st.session_state["user"]:
        st.warning("⚠️ Please login to use voice input.")
    else:
        st.subheader("🎤 Upload Recipe Voice Recording")

        name = st.session_state["user"]
        festival = st.text_input("Festival Name *")
        dish = st.text_input("Dish Name *")
        description = st.text_area("Dish Description *")

        audio_file = st.file_uploader("🎙️ Upload Audio Recording", type=["wav", "mp3", "m4a", "ogg"])

        if st.button("Submit Voice Recording"):
            if not audio_file:
                st.warning("⚠️ Please upload an audio file.")
            elif not dish or not description or not festival:
                st.warning("❗ Festival, dish name, and description are required.")
            elif recipe_exists(name, dish):
                st.warning("⚠️ A recipe with this dish name already exists under your name.")
            else:
                audio_bytes = audio_file.read()

                save_recipe(
                    name=name,
                    festival=festival,
                    dish=dish,
                    language="Voice",
                    ingredients="(submitted via voice)",
                    instructions=description,
                    image=None,
                    latitude=None,
                    longitude=None,
                    video=None,
                    audio=audio_bytes,
                )
                st.success("✅ Voice recipe uploaded successfully!")

# --- Search Recipes ---
elif tab == "Search Recipes":
    st.subheader("🔍 Search Recipes by Dish Name")
    search_query = st.text_input("Enter Dish Name")
    if search_query:
        results = search_recipes_by_dish(search_query)
        if results:
            st.success(f"Found {len(results)} recipe(s):")
            for recipe in results:
                st.markdown(f"### 🍽️ {recipe.dish}")
                st.markdown(f"- Festival: {recipe.festival or 'N/A'}")
                st.markdown(f"- Language: {recipe.language}")
                st.markdown(f"- Instructions: {recipe.instructions}")
                st.markdown(f"- Ingredients: {recipe.ingredients or 'N/A'}")
                if recipe.image:
                    st.image(recipe.image, caption="Dish Image", use_container_width=True)
                if recipe.video:
                    st.video(recipe.video)
                if recipe.audio:
                    st.audio(recipe.audio, format="audio/wav")
                st.markdown("---")
        else:
            st.warning("No recipes found.")

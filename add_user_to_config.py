import yaml
import streamlit_authenticator as stauth
from pathlib import Path

# === Input Section ===
username = input("Enter a username: ")
name = input("Enter full name: ")
password = input("Enter password: ")

# === Hash the password ===
hashed_password = stauth.Hasher([password]).generate()[0]

# === Load existing config.yaml ===
config_path = Path("app/config.yaml")  # Change path if needed

if not config_path.exists():
    raise FileNotFoundError("config.yaml not found at 'app/config.yaml'")

with open(config_path, "r") as file:
    config = yaml.safe_load(file)

# === Insert the new user ===
if "credentials" not in config:
    config["credentials"] = {}
if "usernames" not in config["credentials"]:
    config["credentials"]["usernames"] = {}

config["credentials"]["usernames"][username] = {
    "name": name,
    "password": hashed_password
}

# === Write back to config.yaml ===
with open(config_path, "w") as file:
    yaml.safe_dump(config, file)

print(f"\n✅ User '{username}' added to config.yaml successfully.")

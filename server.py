# -*- coding: utf-8 -*-
"""
Created on Mon Jun  2 14:14:35 2025

@author: rosem
"""

from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)
DB_FILE = "users.json"

def load_users():
    """Charge les utilisateurs depuis le fichier JSON."""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    """Sauvegarde les utilisateurs dans le fichier JSON."""
    with open(DB_FILE, "w") as f:
        json.dump(users, f)

@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    users = load_users()

    if username in users:
        return jsonify({"status": "fail", "message": "Username already exists"}), 409
    users[username] = password
    save_users(users)
    return jsonify({"status": "success", "message": "Signup successful"}), 201

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    users = load_users()

    if users.get(username) == password:
        return jsonify({"status": "success", "message": "Login successful"}), 200
    return jsonify({"status": "fail", "message": "Invalid credentials"}), 401


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Render fournit automatiquement ce port
    app.run(host="0.0.0.0", port=port)
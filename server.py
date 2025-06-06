# -*- coding: utf-8 -*-
"""
Created on Mon Jun  2 14:14:35 2025

@author: rosem
"""

from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev_secret")
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///local.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Database Model ---
class User(db.Model):
    username = db.Column(db.String(80), primary_key=True)
    password = db.Column(db.String(120), nullable=False)
    liked_facts = db.Column(db.JSON, default={})

# --- Initialize DB ---
with app.app_context():
    db.create_all()

# --- Routes ---
@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if User.query.get(username):
        return jsonify({"status": "fail", "message": "Username already exists"}), 409
    
    if not username or len(username) < 3:
        return jsonify({"status": "fail", "message": "Nom d'utilisateur trop court"}), 400

    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"status": "success", "message": "Signup successful"}), 201


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = User.query.get(username)
    if user and user.password == password:
        session['username'] = username
        return jsonify({"status": "success", "message": "Login successful"}), 200

    return jsonify({"status": "fail", "message": "Invalid credentials"}), 401


@app.route("/liked_facts/<username>", methods=["GET"])
def get_liked_facts(username):
    user = User.query.get(username)
    if user:
        return jsonify({"liked_facts": user.liked_facts or {}}), 200
    return jsonify({"liked_facts": {}}), 404


@app.route("/like_fact", methods=["POST"])
def like_fact():
    data = request.get_json()
    print("Données reçues dans /like_fact :", data) 
    username = data.get("username")
    category = data.get("category")
    fact = data.get("fact")

    user = User.query.get(username)
    if not user:
        return jsonify({"status": "fail", "message": "Utilisateur non trouvé"}), 404

    if user.liked_facts is None:
        user.liked_facts = {}

    if category not in user.liked_facts:
        user.liked_facts[category] = []

    if fact not in user.liked_facts[category]:
        user.liked_facts[category].append(fact)
        db.session.commit()
        return jsonify({"status": "success"}), 200
    else:
        return jsonify({"status": "exists"}), 409


# --- Run the server ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# backend/app/routes/main.py
from flask import Blueprint, jsonify

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    return jsonify({"message": "Welcome to the RealValue Backend API!"})

@main_bp.route('/status')
def status():
    return jsonify({"status": "Backend is running!"})
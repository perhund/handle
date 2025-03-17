from app import app
from models import db

with app.app_context():
    db.drop_all()  # Optional: drop existing tables for a clean slate
    db.create_all()
    print("Database tables created.")

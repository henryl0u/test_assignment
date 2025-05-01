from datetime import datetime
from database import db

class Message(db.Model):
    id = db.Column(db.String, primary_key=True)
    recipient = db.Column(db.String, nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now())
    read = db.Column(db.Boolean, default=False)

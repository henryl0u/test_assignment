from flask import Blueprint, request, jsonify
from uuid import uuid4
from models import Message
from schemas import MessageSchema
from database import db

bp = Blueprint('messages', __name__)

message_schema = MessageSchema()
messages_schema = MessageSchema(many=True)

@bp.route('/messages', methods=['POST'])
def submit_message():
    data = request.get_json()
    if not data or 'recipient' not in data or 'content' not in data:
        return jsonify({'error': 'Missing recipient or content'}), 400

    message = Message(
        id=str(uuid4()),
        recipient=data['recipient'],
        content=data['content']
    )

    db.session.add(message)
    db.session.commit()
    return jsonify(message_schema.dump(message)), 201

@bp.route('/messages/unread', methods=['GET'])
def fetch_unread():
    recipient = request.args.get('recipient')
    if not recipient:
        return jsonify({'error': 'Recipient is required'}), 400

    unread_messages = Message.query.filter_by(recipient=recipient, read=False).all()
    for msg in unread_messages:
        msg.read = True
    db.session.commit()
    return jsonify(messages_schema.dump(unread_messages))

@bp.route('/messages/<message_id>', methods=['DELETE'])
def delete_message(message_id):
    message = Message.query.get(message_id)
    if not message:
        return jsonify({"error": "Message not found"}), 404

    db.session.delete(message)
    db.session.commit()
    return '', 204

@bp.route('/messages', methods=['DELETE'])
def delete_multiple():
    data = request.get_json()
    ids = data.get('ids') if data else None

    if not ids or not isinstance(ids, list):
        return jsonify({'error': 'A list of message IDs is required'}), 400

    Message.query.filter(Message.id.in_(ids)).delete(synchronize_session='fetch')
    db.session.commit()
    return '', 204

@bp.route('/messages', methods=['GET'])
def fetch_messages():
    recipient = request.args.get('recipient')
    if not recipient:
        return jsonify({'error': 'Recipient is required'}), 400

    start = request.args.get('start')
    stop = request.args.get('stop')

    query = Message.query.filter_by(recipient=recipient).order_by(Message.timestamp)

    try:
        if start is not None and stop is not None:
            start = int(start)
            stop = int(stop)
            query = query.slice(start, stop)
        elif start is not None:
            start = int(start)
            query = query.offset(start)
        elif stop is not None:
            stop = int(stop)
            query = query.limit(stop)
    except ValueError:
        return jsonify({'error': 'start and stop must be integers'}), 400

    messages = query.all()
    return jsonify(messages_schema.dump(messages))

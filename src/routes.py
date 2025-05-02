from flask import Blueprint, request, jsonify
from uuid import uuid4
from models import Message
from schemas import MessageSchema, RecipientSchema, PaginationSchema, BulkDeleteSchema
from marshmallow import ValidationError
from database import db

MAX_PAGE_SIZE = 100
DEFAULT_PAGE_SIZE = 10

bp = Blueprint("messages", __name__)

message_schema = MessageSchema()
messages_schema = MessageSchema(many=True)
recipient_schema = RecipientSchema()
pagination_schema = PaginationSchema()
bulk_delete_schema = BulkDeleteSchema()


@bp.route("/messages", methods=["POST"])
def submit_message():
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "No input data provided"}), 400

    try:
        validated_data = message_schema.load(json_data)
    except Exception as err:
        return jsonify({"error": err.messages}), 400

    message = Message(
        id=str(uuid4()),
        recipient=validated_data["recipient"],
        content=validated_data["content"],
    )

    db.session.add(message)
    db.session.commit()
    return jsonify(message_schema.dump(message)), 201


@bp.route("/messages/unread", methods=["GET"])
def fetch_unread():
    try:
        validated = recipient_schema.load(request.args)
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

    recipient = validated["recipient"]
    unread_messages = Message.query.filter_by(recipient=recipient, read=False).all()
    for msg in unread_messages:
        msg.read = True
    db.session.commit()
    return jsonify(messages_schema.dump(unread_messages))


@bp.route("/messages/<message_id>", methods=["DELETE"])
def delete_message(message_id):
    if not message_id:
        return jsonify({"error": "Message ID is required"}), 400

    message = Message.query.get(message_id)
    if not message:
        return jsonify({"error": "Message not found"}), 404

    db.session.delete(message)
    db.session.commit()
    return "", 204


@bp.route("/messages", methods=["DELETE"])
def delete_multiple():
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "No input data provided"}), 400

    try:
        validated_data = bulk_delete_schema.load(json_data)
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

    ids = validated_data["ids"]
    Message.query.filter(Message.id.in_(ids)).delete(synchronize_session="fetch")
    db.session.commit()
    return "", 204


@bp.route("/messages", methods=["GET"])
def fetch_messages():
    try:
        recipient_data = recipient_schema.load(request.args, unknown="exclude")
        pagination_data = pagination_schema.load(request.args, unknown="exclude")
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

    recipient = recipient_data["recipient"]
    start = pagination_data["start"] 
    stop = pagination_data["stop"]

    if start is None and stop is None:
        start = 0
        stop = DEFAULT_PAGE_SIZE - 1

    # 🔍 Validate pagination
    if start is not None and stop is not None:
        if stop < start:
            return jsonify({"error": {"stop": "'stop' must be greater than or equal to 'start'"}}), 400
        if (stop - start + 1) > MAX_PAGE_SIZE:
            return jsonify({"error": {"stop": f"Page size exceeds max of {MAX_PAGE_SIZE}"}}), 400

    # 🔁 Build query
    query = Message.query.filter_by(recipient=recipient).order_by(Message.timestamp)

    if start is not None:
        query = query.offset(start)
    if stop is not None and start is not None:
        query = query.limit(stop - start + 1)

    messages = query.all()
    return jsonify(messages_schema.dump(messages))

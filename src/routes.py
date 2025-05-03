from flask import Blueprint, request, jsonify
from uuid import uuid4
from models import Message
from schemas import MessageSchema, RecipientSchema, PaginationSchema, BulkDeleteSchema
from marshmallow import ValidationError
from database import db
from werkzeug.exceptions import BadRequest

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
    try:
        json_data = request.get_json(force=True)
    except BadRequest:
        return jsonify({"error": "Invalid or malformed JSON"}), 400
    
    if not json_data:
        return jsonify({"error": "No input data provided"}), 400

    try:
        validated_data = message_schema.load(json_data)
    except ValidationError as err:
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
    try:
        json_data = request.get_json(force=True)
    except BadRequest:
        return jsonify({"error": "Invalid or malformed JSON"}), 400

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
    elif start is None:
        start = 0
    elif stop is None:
        stop = start + DEFAULT_PAGE_SIZE - 1

    page_size = stop - start + 1
    if stop < start:
        return jsonify({"error": {"stop": "'stop' must be greater than or equal to 'start'"}}), 400
    if (page_size) > MAX_PAGE_SIZE:
        return jsonify({"error": {"stop": f"Page size exceeds max of {MAX_PAGE_SIZE}"}}), 400

    query = Message.query.filter_by(recipient=recipient).order_by(Message.timestamp)
    messages = query.offset(start).limit(page_size).all()

    return jsonify(messages_schema.dump(messages))

@bp.app_errorhandler(404)
def handle_404(e):
    return jsonify({"error": "Endpoint not found"}), 404

@bp.app_errorhandler(405)
def handle_405(e):
    return jsonify({"error": "Method not allowed"}), 405

@bp.app_errorhandler(500)
def handle_500(e):
    return jsonify({"error": "Internal server error"}), 500

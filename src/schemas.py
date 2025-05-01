from marshmallow import Schema, fields

class MessageSchema(Schema):
    id = fields.Str(dump_only=True)
    recipient = fields.Str(required=True)
    content = fields.Str(required=True)
    timestamp = fields.DateTime()
    read = fields.Bool()

from marshmallow import Schema, fields, validate

class MessageSchema(Schema):
    id = fields.Str(dump_only=True)
    recipient = fields.Email(required=True)
    content = fields.Str(required=True)
    timestamp = fields.DateTime(dump_only=True)
    read = fields.Bool(dump_only=True)

class RecipientSchema(Schema):
    recipient = fields.Email(required=True)

class PaginationSchema(Schema):
    start = fields.Int(load_default=None, validate=validate.Range(min=0))
    stop = fields.Int(load_default=None, validate=validate.Range(min=0))

class BulkDeleteSchema(Schema):
    ids = fields.List(fields.Str(), required=True, validate=validate.Length(min=1))
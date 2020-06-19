from marshmallow import Schema, fields, validate

sensor_types = ['temperature', 'humidity']

class DeviceReadingsSchema(Schema):
    type = fields.Str(required=True, validate=[validate.OneOf(sensor_types)])
    value = fields.Int(required=True, validate=[validate.Range(min=0, max=100)])
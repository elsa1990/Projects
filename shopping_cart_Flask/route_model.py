from marshmallow import Schema, fields

# Log in
class LoginSchema(Schema):
    account = fields.Str(doc="account", example="string", required=True)
    password = fields.Str(doc="password", example="string", required=True)


# Registration
class RegistrationSchema(Schema):
    name = fields.Str(doc="name", example="string", required=True)
    account = fields.Str(doc="account", example="string", required=True)
    password = fields.Str(doc="password", example="string", required=True)
    gender = fields.Str(doc="gender", example="string", required=True)
    birthdate = fields.Str(doc="birthdate", example="string", required=True)


class UserGetSchema(Schema):
    name = fields.Str(example="string")


class UserPostSchema(Schema):
    product_name = fields.Str(doc="product_name", example="string", required=True)
    user_id = fields.Int(doc="user_id", example="int", required=True)
    amount = fields.Int(doc="amount", example="int", required=True)


class UserPatchSchema(Schema):
    product_name = fields.Str(doc="product_name", example="string")
    order_number = fields.Int(doc="order_id", example="int")
    amount = fields.Int(doc="amount", example="int")


# Response
class UserCommonResponse(Schema):
    message = fields.Str(example="success")


class UserPostResponse(UserPostSchema):
    total_price = fields.Int(example={"total_price": 0})


# Get
class UserGetResponse(UserCommonResponse):
    datatime = fields.Str()
    name = fields.Str(doc="product_name", example="string")
    data = fields.List(fields.Dict(), example={
        "id": 1,
        "name": "name",
        "price": 10,
        "amount": 5
    })



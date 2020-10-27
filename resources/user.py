from functools import wraps

from flask_restful import Resource, reqparse
from flask_jwt_extended import create_access_token, create_refresh_token, \
    jwt_refresh_token_required, get_jwt_identity, jwt_required, \
    get_raw_jwt, get_jti, get_jwt_claims, get_current_user, current_user, verify_jwt_in_request
from models.user import UserModel
from sqlalchemy.exc import DataError

_user_parser = reqparse.RequestParser()
_user_parser.add_argument("email", type=str)
_user_parser.add_argument("fullname", type=str)
_user_parser.add_argument('username', type=str)
_user_parser.add_argument("password", type=str)
_user_parser.add_argument("role", type=str)


class UserRegister(Resource):
    def post(self):
        data = _user_parser.parse_args()
        email = data["email"]
        fullname = data["fullname"]
        username = data["username"]
        password = data["password"]
        role = "User"

        if UserModel.find_by_email(email):
            return {"message": "Email Already Exists"}, 400
        if UserModel.find_by_username(username):
            return {"message": "Username exist"}, 400
        if not email or email == "":
            return {"message": "Enter an Email"}, 400
        if not password or password == '':
            return {"message": "ENter A  Password"}, 400
        if not fullname or fullname == '':
            return {"message": "Enter Your Fullname"}, 400
        if not username or username == '':
            return {"mesage": "Enter A username"}, 400
        try:
            new_user = UserModel(
                email=email,
                password=UserModel.generate_hash(password),
                fullname=fullname,
                username=username,
                role=role
            )
            new_user.save()
            return {"message": "Registered Success"}, 201
        except DataError as e:
            return dict(message=e._message())


def admin_required(fn):
    @wraps(fn)
    def secure_func(*args, **kwargs):
        verify_jwt_in_request()
        if "Admin" not in current_user.role:
            return {'message': 'only admin can access this resource'}
        return fn(*args, **kwargs)

    return secure_func


class GetAllUser(Resource):
    @admin_required
    def get(self):
        users = [user.json() for user in UserModel.get_all_users("User")]
        admin_users = [user.json() for user in UserModel.get_all_users("Super Admin")]

        return {"users": users, "admin": admin_users}, 200


class User(Resource):
    @jwt_required
    def get(self):
        return current_user.json(), 200


class UserId(Resource):
    @jwt_required
    def get(self, user_id):
        user = UserModel.find_by_id(user_id)
        return user.json(), 200


class UserBlogPosts(Resource):
    @jwt_required
    def get(self):
        return current_user.blog_json(), 200


class UserLogin(Resource):
    def post(self):
        data = _user_parser.parse_args()
        email = data["email"]
        password = data["password"]
        current_user = UserModel.find_by_email(email)
        if not email or email == '':
            return {"message": "Email is Required"}, 400
        if not password or password == '':
            return {"message ": "Password is required "}, 400

        if not current_user:
            return {'message': 'User doesn\'t exist'}, 404
        if UserModel.verify_password(password, current_user.password):
            access_token = create_access_token(identity=current_user.username, fresh=True)
            refresh_token = create_refresh_token(current_user.username)
            return {
                       "user_id": current_user.slug or None,
                       "access_token": access_token,
                       "refresh_token": refresh_token,
                       "Message": "Login Successful"
                   }, 201
        else:
            return {"message": "Wrong Credentials"}, 401


class AdminLogin(Resource):
    def post(self):
        data = _user_parser.parse_args()
        email = data["email"]
        password = data["password"]
        current_user = UserModel.find_by_email(email)
        if "Admin" not in current_user.role:
            return {"message":"Not Authorized"}, 401
        if not email or email == '':
            return {"message": "Email is Required"}, 400
        if not password or password == '':
            return {"message ": "Password is required "}, 400
        if not current_user:
            return {'message': 'User doesn\'t exist'}, 404
        if UserModel.verify_password(password, current_user.password):
            access_token = create_access_token(identity=current_user.username, fresh=True)
            refresh_token = create_refresh_token(current_user.username)
            return {
                       "access_token": access_token,
                       "refresh_token": refresh_token,
                       "Message": "Login Successful"
                   }, 201
        else:
            return {"message": "Wrong Credentials"}, 40


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user.username, fresh=False)
        return {'access_token': new_token}, 200

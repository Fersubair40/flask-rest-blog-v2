import os
from flask import Flask
from flask_restful import Api, Resource
from flask_jwt_extended import JWTManager, current_user, jwt_required
from flask_migrate import Migrate
from flask_cors import CORS


from resources.user import UserRegister, UserLogin, GetAllUser, TokenRefresh, User, UserId, AdminLogin
from resources.blog import CreateBlog, UserBlogPosts
from models.user import UserModel

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['CORS_HEADERS'] = 'Content-Type'
app.secret_key = os.environ.get("JWT_SECRET_KEY")
app.config['PROPAGATE_EXCEPTIONS'] = True
api = Api(app)
jwt = JWTManager(app)

# migrate = Migrate(app, db)


@jwt.user_loader_callback_loader
def user_loader_callback(identity):
    user = UserModel.find_by_username(identity)
    return user if user else None


@jwt.user_loader_error_loader
def user_error_callback(identity):
    return {'message': "user with {} not found..".format(identity)}


@jwt.expired_token_loader
def expired_token_callback():
    return {
               'description': 'The token has expired.',
               "message": "expired token"
           }, 401


@jwt.invalid_token_loader
def invalid_token_callback(error):
    return {
               'description': 'Invalid Token Entered'

           }, 401


@jwt.unauthorized_loader
def missing_token_callback(error):
    return {
               'message': 'Request does not contain an access token.',
               "error": error
           }, 401


@jwt.needs_fresh_token_loader
def token_not_fresh_callback():
    return {
               'message': 'The token is not fresh.'
           }, 401


@jwt.revoked_token_loader
def revoked_token_callback():
    return {
               'message': 'Your token has been revoked.'
           }, 401


class Index(Resource):
    def get(self):
        return {"hello":"hello"}


api.add_resource(Index, '/')
api.add_resource(UserRegister, "/register")
api.add_resource(UserLogin, "/login")
api.add_resource(GetAllUser, "/users")
api.add_resource(TokenRefresh, '/refresh')
api.add_resource(User, "/user/me")
api.add_resource(UserId, "/user/<string:user_id>")
api.add_resource(AdminLogin, "/admin/login")
api.add_resource(UserBlogPosts, "/user/blogs")
api.add_resource(CreateBlog, "/<string:user_slug>/blog")

if __name__ == '__main__':
    from models import db
    db.init_app(app)
    app.run()

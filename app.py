import os
from flask import Flask
from flask_restful import Api, Resource
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

from models import db

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = os.environ.get("JWT_SECRET_KEY")
api = Api(app)
jwt = JWTManager(app)
db.init_app(app)
migrate = Migrate(app, db)


@jwt.user_claims_loader
def add_claims_to_jwt(identity):
    if identity == 'Admin':
        return {"is_admin": True}
    return {"is_admin": False}


class Index(Resource):
    def get(self):
        return {"msg": "Hello"}, 200


api.add_resource(Index, '/')

if __name__ == '__main__':
    app.run()

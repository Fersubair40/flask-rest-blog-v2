import datetime
import random
import string
from passlib.hash import pbkdf2_sha256 as sha256

from . import db
from .blog import BlogModel


def random_string_digits(string_length=8):
    letter_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letter_and_digits) for i in range(string_length))


class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String)
    email = db.Column(db.String(120), nullable=False, unique=True)
    username = db.Column(db.String(120), nullable=False, unique=True)
    fullname = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(90))
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)

    blogposts = db.relationship(BlogModel, lazy="dynamic")

    def __init__(self, email, username, fullname, password, role):
        self.email = email
        self.slug = random_string_digits()
        self.username = username
        self.fullname = fullname
        self.password = password
        self.role = role
        self.created_at = datetime.datetime.utcnow()
        self.modified_at = datetime.datetime.utcnow()

    def json(self):
        return {
            "id": self.id,
            "slug": self.slug,
            "email": self.email,
            "username": self.username,
            "fullname": self.fullname,
            "role": self.role,
            "blogposts": [blog.json() for blog in self.blogposts.all()]
        }

    def blog_json(self):
        return {
            "slug": self.slug,
            "blogpost": [blog.json for blog in self.blogposts.all()]
        }

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self, data, value):
        for key, item in data.item():
            if key == "password":
                self.password = self.generate_hash(value)
            setattr(self, key, item)
            self.modified_at = datetime.datetime.utcnow()
            db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def generate_hash(password):
        return sha256.hash(password)

    @staticmethod
    def verify_password(password, hash):
        return sha256.verify(password, hash)

    @staticmethod
    def find_by_email(value):
        return UserModel.query.filter_by(email=value).first()

    @staticmethod
    def find_by_username(value):
        return UserModel.query.filter_by(username=value).first()

    @staticmethod
    def find_by_id(_id):
        return UserModel.query.filter_by(slug=_id).first()

    @staticmethod
    def get_all_users(value):
        return UserModel.query.filter_by(role=value).all()

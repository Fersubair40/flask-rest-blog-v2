from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, current_user
from sqlalchemy.exc import DataError

from models.blog import BlogModel
from models.user import UserModel

_blog_parser = reqparse.RequestParser()
_blog_parser.add_argument("title", type=str)
_blog_parser.add_argument("content", type=str)
_blog_parser.add_argument("user_id", type=str)


class CreateBlog(Resource):
    @jwt_required
    def post(self, user_slug):
        data = _blog_parser.parse_args()
        title = data["title"]
        content = data["content"]
        user_id = user_slug
        user = UserModel.find_by_id(user_slug)

        if not user:
            return {"Message": "Unauthorised"}, 401
        if not title or title == '':
            return {"message": "title is required"}, 401
        if not content or content == '':
            return {"message": "content is required"}, 401
        if not user_id or user_id == '':
            return {"message": "user id is required"}, 401
        try:
            new_blog = BlogModel(
                title=title,
                content=content,
                user_id=user_id
            )
            new_blog.save()
            return {"message": "Post created"}

        except DataError as e:
            return dict(message=e._message())


class UserBlogPosts(Resource):
    @jwt_required
    def get(self):
        return current_user.blog_json(), 200

import  datetime

from . import  db


class BlogModel(db.Model):
    __tablename__ = "blogs"

    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    def __init__(self, title, content, user_id):
        self.title = title
        self.content = content
        self.user_id = user_id
        self.created_at = datetime.datetime.utcnow()
        self.modified_at = datetime.datetime.utcnow()

    def json(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "user_id": self.user_id
        }

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self, data):
        for key, item in data.items():
            setattr(self, key, item)
        self.modified_at = datetime.datetime.utcnow()
        db.session.commit()

    @staticmethod
    def find_by_id(id):
        return  BlogModel.query.get(id)

    @staticmethod
    def get_all_blog():
        return  BlogModel.query.all()


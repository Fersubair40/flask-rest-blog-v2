from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from models.user import UserModel
from models.blog import BlogModel

from app import  app, db

migrate = Migrate(app=app, db=db)
manager = Manager(app=app)

manager.add_command("db", MigrateCommand)

if __name__ == '__main__':
    manager.run()
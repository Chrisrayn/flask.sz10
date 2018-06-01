from flask import render_template
from flask_script import Manager

# 启动项目

from app import create_app
from config import DevelopConfig

app = create_app(DevelopConfig)

manager = Manager(app)

# 扩展迁移
from models import db
db.init_app(app)

from flask_migrate import Migrate,MigrateCommand
Migrate(app,db)
manager.add_command('db',MigrateCommand)


if __name__ == '__main__':
    manager.run()

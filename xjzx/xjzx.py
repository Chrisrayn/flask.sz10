from flask_script import Manager

from app import create_app
from config import developConfig

app = create_app(developConfig)

manager = Manager(app)

if __name__ == '__main__':
    manager.run()

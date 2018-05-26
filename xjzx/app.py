from flask import Flask

def create_app(config):
    app = Flask(__name__)

    app.config.from_object(config)

    from views_news import news_blueprint
    app.register_blueprint(news_blueprint)

    from views_user import user_blueprint
    app.register_blueprint(user_blueprint)

    from views_admin import admin_blueprint
    app.register_blueprint(admin_blueprint)

    return app
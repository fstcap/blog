import os
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_socketio import SocketIO

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
            SECRET_KEY='dev',
            DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite')
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db, auth, blog, comment, like
  
    bootstrap = Bootstrap()
    bootstrap.init_app(app)
    
    socketio = SocketIO()
    socketio.init_app(app)

    db.init_app(app)
    app.register_blueprint(auth.bp)
    app.register_blueprint(blog.bp)
    app.register_blueprint(comment.bp)
    app.register_blueprint(like.bp)

    app.add_url_rule('/', endpoint='index')

    return app

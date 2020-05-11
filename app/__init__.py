import os
from flask import Flask
from dotenv import load_dotenv
from .auth import auth
from .posts import post

load_dotenv('../.env')

def create_app(test_config=None):
  app = Flask(__name__, instance_relative_config=True)
  app.config.from_mapping(
    SECRET_KEY=os.getenv('SECRET'),
    DATABASE= os.path.join(app.instance_path, 'vibes.sqlite')
  )
  if test_config is None:
    app.config.from_pyfile('config.py', silent=True)
  else:
    app.config.from_mapping(test_config)

  if (not os.path.isdir(app.instance_path)):
    try:
      os.makedirs(app.instance_path)
    except OSError as e:
      app.logger.error(f'Failed to create instance folder: {e}')

  from . import db
  db.init_app(app)
  app.register_blueprint(auth.auth_bp)
  app.register_blueprint(post.bp)
  app.add_url_rule('/', endpoint='view_posts')
  return app
    

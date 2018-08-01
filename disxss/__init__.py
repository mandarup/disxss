



from flask import (Blueprint, request, render_template, flash, g, session,
    redirect, url_for, abort, Flask)
from werkzeug.routing import BaseConverter
import uuid
from flask_wtf.csrf import CSRFError, CSRFProtect

from flask import Flask
from flask_pymongo import PyMongo

from disxss import logging_config


# Secret key used to encrypt session cookies.
# We'll just generate one randomly when the app starts up, since this is just
# a demonstration project.
SECRET_KEY = str(uuid.uuid4())
WTF_CSRF_SESSION_KEY = str(uuid.uuid4())

logging_config.set_config()

app = Flask(__name__, static_url_path='/static')
app.config.from_object('config')
# app.secret_key = app.config['SECRET_KEY']
app.secret_key = SECRET_KEY
# app.secret_key = CSRF_SESSION_KEY

app.config["MONGO_URI"] = "mongodb://localhost:27017/disxss"
mongo = PyMongo()
mongo.init_app(app)
db = mongo.db


csrf = CSRFProtect()
csrf.init_app(app)

class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]

app.url_map.converters['regex'] = RegexConverter

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def not_found(error):
    return render_template('500.html'), 500

@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    app.logger.error(e.description)
    return render_template('csrf_error.html', reason=e.description), 400

from disxss.users.views import bp as  users_bp
app.register_blueprint(users_bp)

from disxss.frontends.views import bp as frontends_bp
app.register_blueprint(frontends_bp)


def custom_render(template, *args, **kwargs):
    """
    custom template rendering including some flask_reddit vars
    """
    return render_template(template, *args, **kwargs)

app.debug = app.config['DEBUG']

if __name__ == '__main__':
    print('We are running flask via main()')
    app.run()

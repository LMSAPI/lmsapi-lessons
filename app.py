from flask import Flask, request, abort
from flask_pymongo import PyMongo
from functools import wraps
from bson import json_util

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'heroku_k0kdm9jl'
app.config['MONGO_URI'] = 'mongodb://test_user:test_pass@ds157380.mlab.com:57380/heroku_k0kdm9jl'
app.secret_key = 'mysecret'

mongo = PyMongo(app)


def require_appkey(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        if request.args.get('key') and key_exists(request.args.get('key')):
            return view_function(*args, **kwargs)
        else:
            abort(401)

    return decorated_function


@app.route('/')
@require_appkey
def root():
    return 'hello there'


def obj_dict(obj):
    return obj.__dict__


def user_name(key):
    users = mongo.db.users
    user = users.find_one({'apikey': key})
    return user['name']


def key_exists(key):
    users = mongo.db.users
    user_key = users.find_one({'apikey':key})

    if user_key is None:
        return False

    return True


if __name__ == '__main__':
    app.run(debug=True)

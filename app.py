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


@app.route('/lessons', methods=['POST', 'GET'], defaults={'course': None, 'lesson': None})
@app.route('/lessons/<course>/<lesson>', methods=['PUT', 'DELETE'])
@require_appkey
def lessons(course, lesson):
    mongo_lessons = mongo.db.lessons
    teacheruser = user_name(request.args.get('key'))

    # get all lessons for a course
    if request.method == 'GET':
        lessons_resp = mongo_lessons.find({'course_num': request.args.get('course_num'),
                                           'teacheruser': teacheruser})
        return json_util.dumps(lessons_resp)

    # insert new lesson into a course
    if request.method == 'POST':
        existing_lesson = mongo_lessons.find_one({'number': request.args.get('number'),
                                                  'course_num': request.args.get('course_num'),
                                                  'teacheruser': teacheruser})
        if existing_lesson is None:
            mongo_lessons.insert({'number': request.args.get('number'),
                                  'course_num': request.args.get('course_num'),
                                  'title': request.args.get('title'),
                                  'content': request.args.get('content'),
                                  'teacheruser': teacheruser})
            return 'Added'

        return 'already exists!'

    # update a lesson
    if request.method == 'PUT':
        existing_lesson = mongo_lessons.find_one({'number': lesson,
                                                      'course_num': course,
                                                      'teacheruser': teacheruser})
        if existing_lesson is not None:
            print(request.args)
            mongo_lessons.update_one({'number': lesson,
                                      'course_num': course,
                                      'teacheruser': teacheruser},
                                     {'$set': {'title': request.args.get('title'),
                                               'content': request.args.get('content')}})

            return 'Updated'

        return 'Update failed'

    # delete a lesson
    if request.method == 'DELETE':
        existing_lesson = mongo_lessons.find_one({'number': lesson,
                                                  'course_num': course,
                                                  'teacheruser': teacheruser})
        if existing_lesson is not None:
            mongo_lessons.delete_one({'number': lesson,
                                      'course_num': course,
                                      'teacheruser': teacheruser})
            return 'Deleted'

        return 'Delete failed'


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

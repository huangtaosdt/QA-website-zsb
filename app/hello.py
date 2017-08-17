from flask import Flask
from flask import request
from flask import make_response
from flask import abort
from flask import redirect
from flask.ext.script import Manager


app = Flask(__name__)
manager=Manager(app)

@app.route('/')
def index():
    # user_agent=request.headers.get('User-Agent')
    # return '<h1> browser:%s!</h1>' %user_agent
    # response = make_response('<h1> Cookie!</h1>')
    # response.set_cookie('answer','42')
    return redirect("http://www.examsssple.com")

@app.route('/user/<id>')
def get_user(id):
    user=id

    if not user:
        abort(404)
    return '<h1>Hello,%s</h1>'%user


if __name__ == '__main__':
    # app.run(debug=True)
    manager.run()
from flask import render_template
from app import app
from app.forms import LoginForm

user = {"username": "Michal"}

posts = [
  {
      'author': {'username': 'Foo'},
      'body': 'Welcome!'
  },
  {
      'author': {'username': 'Bar'},
      'body': 'Good to be here!'
  }
]

@app.route('/')
@app.route('/index')
def index():
    return render_template(
      'index.html', 
      title='Home', 
      user=user, 
      posts=posts
    )

@app.route('/login')
def login():
    return render_template(
        'login.html',
        title='Sign In',
        form=LoginForm()
    )


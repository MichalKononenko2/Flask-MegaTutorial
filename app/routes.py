from flask import render_template
from app import app

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


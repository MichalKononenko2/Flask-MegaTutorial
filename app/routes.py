from flask import render_template
from app import app

user = {"username": "Michal"}

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home', user=user)


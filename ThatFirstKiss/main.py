from flask import Flask, redirect, url_for
from datetime import timedelta
from admin.main import admin
from user.main import user
from users import db
app = Flask(__name__)
app.secret_key = 'nothing'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'nothing' 
app.app_context().push()
db.init_app(app)
app.permanent_session_lifetime = timedelta(minutes=5)
app.register_blueprint(admin, url_prefix='/admin')
app.register_blueprint(user, url_prefix='/user')

@app.route('/')
def home():
    return redirect(url_for('user.home'))

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
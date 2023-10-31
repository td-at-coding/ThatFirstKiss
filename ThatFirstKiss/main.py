from flask import Flask, redirect, url_for, session
from datetime import timedelta
from admin.main import admin
from user.main import user
from users import db, messages, matches, users
from flask_socketio import SocketIO, send, join_room, leave_room
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
socketio = SocketIO(app)

@socketio.on('message')
def handle_message(data):
    if 'user' not in session:
        return
    
    user_name = data['sender']
    user = users.query.filter_by(name=user_name).first()
    match_id = int(data['match_id'])
    ms = matches.query.filter_by(id=match_id).first()
    msg = messages(data['message'], ms, user)
    db.session.add(msg)
    db.session.commit()

    send(data, to=data['match_id'])

@socketio.on('join_match')
def connect(data):
    if 'user' not in session:
        return
    user_name = session['user']
    user_id = users.query.filter_by(name=user_name).first().id
    match_id = int(data['match_id'])
    ms = matches.query.filter_by(id=match_id).first()
    if not ms or (ms.user_one_id !=user_id and ms.user_two_id !=user_id):
        return
    join_room(data['match_id'])

@socketio.on('leave_match')
def disconnect(data):
    leave_room(data['match_id'])


@app.route('/')
def home():
    return redirect(url_for('user.home'))

if __name__ == '__main__':
    db.create_all()
    socketio.run(app, debug=True)
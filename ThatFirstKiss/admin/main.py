from flask import Blueprint, render_template, redirect, request, session, flash, url_for
from users import db, users, images
admin = Blueprint('admin',__name__, static_folder='static', template_folder='templates')


@admin.route('/home')
@admin.route('/')
def home():
    return render_template('admin/home.html')

@admin.route('/data', methods=['POST','GET'])
def data():
    if 'adminloggedin' in session:
        if request.method == 'POST':
            request_form = request.form['submit']
            if '.' in request_form:
                submit_value = request_form.split('.')
                if submit_value[0] == 'ban_request':
                    usr = users.query.filter_by(id=int(submit_value[1])).first()
                    usr.banned = True
                    db.session.commit()
                elif submit_value[0] == 'unban_request':
                    usr = users.query.filter_by(id=int(submit_value[1])).first()
                    usr.banned = False
                    db.session.commit()
        return render_template('admin/view.html', values=users.query.all(),images=images.query.all())
    else:
        flash('Must Login First!')
        return redirect(url_for('admin.login'))

@admin.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'password':
            flash('Login Successful!')
            session['adminloggedin'] = True
            return redirect(url_for('admin.data'))
        else:
            flash('Invalid Login!')
            return render_template('admin/login.html')
    else:
        if 'adminloggedin' in session:
            return redirect(url_for('admin.data'))
        return render_template('admin/login.html')


from flask import Blueprint, render_template, redirect, request, session, flash, url_for
from users import users, images
admin = Blueprint('admin',__name__, static_folder='static', template_folder='templates')


@admin.route('/home')
@admin.route('/')
def home():
    return render_template('admin/home.html')

@admin.route('/data')
def data():
    if 'adminloggedin' in session:
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


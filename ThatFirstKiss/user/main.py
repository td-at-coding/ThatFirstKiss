from flask import Blueprint, render_template, redirect, request, session, flash, url_for, current_app
from users import users, db, images
from werkzeug.utils import secure_filename
import base64
user = Blueprint('user',__name__, template_folder='templates')

ALLOWED_EXTENSIONS = ['png','jpg','jpeg']

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@user.route('/')
def home():
    active = 'user' in session
    return render_template('user/index.html',active=active)

@user.route('/login', methods=["POST","GET"])
def login():
    if request.method == 'POST':
        session.permanent = True
        nm = request.form['nm']
        session['user'] = nm
        found_user = users.query.filter_by(name=nm).first()
        if found_user:
            session['email'] = found_user.email
            session['sex'] = ['female','male'][found_user.sex=='M'] if found_user.sex else None
            session['images'] = found_user.id
        else:
            usr = users(nm, "", '')
            db.session.add(usr)
            db.session.commit()
        flash('Login Successful!')
        return redirect(url_for('user.user_page'))
    else:
        if 'user' in session:
            flash('Already Logged In!')
            return redirect(url_for('user.user_page'))
        return render_template('user/login.html')

@user.route('/user', methods=["POST","GET"])
def user_page():
    email = None
    sex = None
    pics = None
    if "user" in session:
        nm = session['user']
        if request.method == "POST":
            submit_value = request.form['submit']
            if submit_value == 'submit_data':
                email = request.form["email"]
                sex = request.form["sex"]
                session["email"] = email
                session["sex"] = None if sex == 'none' else sex
                found_user = users.query.filter_by(name=nm).first()
                found_user.email = email
                found_user.sex = ['F','M'][sex=='male'] if sex else 'N'
                image = request.files['image']
                if image.filename:
                    filename = secure_filename(image.filename)
                    if not allowed_file(filename):
                        flash('The File Extension Is Not Allowed!')
                        return render_template('user/user.html', active=True)
                    mimetype = image.mimetype
                    file = image.read()
                    file = base64.b64encode(file).decode('utf-8')
                    file = f'data:{mimetype};base64,{file}'
                    pics = found_user.id
                    session['pics'] = pics
                    all_images = images.query.all()
                    for img in all_images:
                        if img.img == file:
                            flash('The Image Already Exists!')
                            return render_template('user/user.html', active=True)
                    img = images(file,filename,mimetype,found_user.id)
                    db.session.add(img)
                    db.session.commit()
                else:
                    if 'images' in session:
                        pics = session['images']
                flash('info was saved!')
            else:
                images.query.filter_by(id=int(submit_value)).delete()
                db.session.commit()
                if 'email' in session:
                    email = session["email"]
                if 'sex' in session:
                    sex = session['sex']
                if 'images' in session:
                    pics = session['images']
        else:
            if 'email' in session:
                email = session["email"]
            if 'sex' in session:
                sex = session['sex']
            if 'images' in session:
                pics = session['images']
        pics = images.query.filter_by(user_id=pics).all()
        return render_template('user/user.html', active=True, email=email, sex=sex, pics=pics)
    else:
        flash("You are not logged in!", 'error')
        return redirect(url_for('user.login'))
    
@user.route('/logout')
def logout():
    flash(f'you have been logged out!', 'info')
    session.pop('user',None)
    session.pop('email',None)
    session.pop('sex',None)
    session.pop('images',None)
    return redirect(url_for('user.login'))

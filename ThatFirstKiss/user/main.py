from flask import Blueprint, render_template, redirect, request, session, flash, url_for
from users import users, db, images, matches, requests, messages, dislikes
from werkzeug.utils import secure_filename
from sqlalchemy import or_, and_
import base64
import random
user = Blueprint('user',__name__, template_folder='templates')

ALLOWED_EXTENSIONS = ['png','jpg','jpeg']

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@user.route('/')
def home():
    name = session.get('user')
    current_user = users.query.filter_by(name=name).first()
    return render_template('user/index.html',active=current_user)

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
            if found_user.banned:
                return redirect(url_for('user.ban'))
        else:
            usr = users(nm, "", '')
            db.session.add(usr)
            db.session.commit()
        flash('Login Successful!')
        return redirect(url_for('user.profile'))
    else:
        if 'user' in session:
            flash('Already Logged In!')
            found_user = users.query.filter_by(name=session['user']).first()
            if found_user.banned:
                return redirect(url_for('user.ban'))
            return redirect(url_for('user.profile'))
        return render_template('user/login.html', active=False)


@user.route('/ban')
def ban():
    name = session.pop('user',None)
    session.pop('email',None)
    session.pop('sex',None)
    session.pop('images',None)
    current_user = users.query.filter_by(name=name).first()
    return render_template('user/prison.html', active=current_user)


@user.route('/profile', methods=["POST","GET"])
def profile():
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
                db.session.commit()
                image = request.files['image']
                if image.filename:
                    filename = secure_filename(image.filename)
                    if not allowed_file(filename):
                        flash('The File Extension Is Not Allowed!')
                        return render_template('user/profile.html', active=found_user)
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
                            return render_template('user/profile.html', active=found_user)
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
        current_user = users.query.filter_by(name=nm).first()
        return render_template('user/profile.html', active=current_user, email=email, sex=sex, pics=pics)
    else:
        flash("You are not logged in!", 'error')
        return redirect(url_for('user.login'))
    
@user.route('/search', methods=['POST','GET'])
def search():
    if 'user' in session and 'sex' in session:
        current_user = users.query.filter_by(name=session['user']).first()
        if request.method == 'POST':
            submit_value = request.form['submit'].split('.')
            if submit_value[0] == 'submit_like':
                user_id = int(submit_value[1])
                second_user = users.query.filter_by(id=user_id).first()
                r = requests.query.filter_by(initiator_id=user_id,receiver_id=current_user.id)
                if r.first():
                    r.delete()
                    m = matches(current_user,second_user)
                    db.session.add(m)
                    db.session.commit()
                    flash('You Matched!')
                else:
                    re = requests(current_user, second_user)
                    db.session.add(re)
                    db.session.commit()
            elif submit_value[0] == 'submit_dislike':
                user_id = int(submit_value[1])
                second_user = users.query.filter_by(id=user_id).first()
                dislike = dislikes(current_user, second_user)
                db.session.add(dislike)
                db.session.commit()
            else:
                return 'Error invalid post request'
        sex = session['sex']
        y1 = matches.query.filter_by(user_one_id=current_user.id)
        y2 = matches.query.filter_by(user_two_id=current_user.id)
        x = requests.query.filter_by(initiator_id=current_user.id)
        z1 = dislikes.query.filter_by(user_id=current_user.id)
        z2 = dislikes.query.filter_by(disliked_id=current_user.id)
        if sex == 'male':
            women = users.query.filter_by(sex='F').filter(
                ~users.id.in_(y1.with_entities(matches.user_two_id))
                , ~users.id.in_(y2.with_entities(matches.user_one_id))
                , ~users.id.in_(x.with_entities(requests.receiver_id))
                , ~users.id.in_(z1.with_entities(dislikes.disliked_id))
                , ~users.id.in_(z2.with_entities(dislikes.user_id))
                , users.banned == False
            ).all()
            if len(women):
                choice = random.choice(women)
                pics = images.query.filter_by(user_id=choice.id).all()
                return render_template('user/search.html', active=current_user, name=choice.name, id=choice.id, pics=pics)
            else:
                return "Can't find any body!"
        elif sex == 'female':
            men = users.query.filter_by(sex='M').filter(
                ~users.id.in_(y1.with_entities(matches.user_two_id))
                , ~users.id.in_(y2.with_entities(matches.user_one_id))
                , ~users.id.in_(x.with_entities(requests.receiver_id))
                , ~users.id.in_(z1.with_entities(dislikes.disliked_id))
                , ~users.id.in_(z2.with_entities(dislikes.user_id))
                , users.banned == False
            ).all()
            if len(men):
                choice = random.choice(men)
                pics = images.query.filter_by(user_id=choice.id).all()
                return render_template('user/search.html', active=current_user, name=choice.name, id=choice.id, pics=pics)
            else:
                return "Can't find any body!"
        else:
            flash('You must enter a sex first!')
            return redirect(url_for('user.profile'))
    else:
        flash("You've to be logged in order to access!")
        return redirect(url_for('user.home'))

@user.route('/settings', methods=['POST','GET'])
def settings():
    if 'user' in session:
        if request.method == 'POST':
            request_form = request.form['submit']
            if '.' in request_form:
                submit_value = request_form.split('.')
                if submit_value[0] == 'delete_request':
                    request_id = int(submit_value[1])
                    requests.query.filter_by(id=request_id).delete()
                    db.session.commit()
                elif submit_value[0] == 'delete_match':
                    match_id = int(submit_value[1])
                    matches.query.filter_by(id=match_id).delete()
                    messages.query.filter_by(match_id=match_id).delete()
                    db.session.commit()
        
        current_user = users.query.filter_by(name=session['user']).first()
        current_id = current_user.id
        reqs = requests.query.filter_by(initiator_id=current_id).all()
        ms = matches.query.filter(or_(matches.user_one_id==current_id, matches.user_two_id==current_id))
        return render_template('user/settings.html', active=current_user, reqs=reqs, ms=ms, name=current_user.name )
    else:
        flash("You've to be logged in order to access!")
        return redirect(url_for('user.home'))

@user.route('/chats', methods=['POST','GET'])
def chats():
    if 'user' in session:
        current_user = users.query.filter_by(name=session['user']).first()
        current_id = current_user.id
        ms = matches.query.filter(or_(matches.user_one_id==current_id, matches.user_two_id==current_id))
        if request.method == 'POST':
            request_form = request.form['submit']
            if '.' in request_form:
                submit_value = request_form.split('.')
                if submit_value[0] == 'match_chat':
                    match_id = int(submit_value[1])
                    return redirect(url_for('user.view',match_id=match_id))
        return render_template('user/chats.html', active=current_user, ms=ms)
    else:
        flash("You've to be logged in order to access!")
        return redirect(url_for('user.home'))

@user.route('/chats/<int:match_id>')
def view(match_id):
    if 'user' in session:
        current_user = users.query.filter_by(name=session['user']).first()
        current_id = current_user.id
        ms = matches.query \
            .filter(or_(matches.user_one_id==current_id, matches.user_two_id==current_id)) \
            .filter_by(id=match_id).first()
        if ms:
            l = messages.query.filter_by(match_id=match_id).all()
            receiver = ms.user_one if ms.user_two.name == current_user.name else ms.user_two
            return render_template('user/view.html', active=current_user,l=l,sender=current_user,receiver=receiver,match_id=match_id)
        else:
            flash("You've to be matched in order to access!")
            return redirect(url_for('user.chats'))

    else:
        flash("You've to be logged in order to access!")
        return redirect(url_for('user.home'))

    pass

@user.route('/logout')
def logout():
    flash(f'you have been logged out!', 'info')
    session.pop('user',None)
    session.pop('email',None)
    session.pop('sex',None)
    session.pop('images',None)
    return redirect(url_for('user.login'))

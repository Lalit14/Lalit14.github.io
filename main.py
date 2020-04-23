from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
import json
import os
import math
from werkzeug.utils import secure_filename
from flask_mail import Mail
from datetime import datetime

with open('config.json', 'r') as c:
    params = json.load(c)["params"]

local_server = True
app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['UPLOAD_FOLDER']=params['location']
# app.config.update(
#     MAIL_SERVER='smtp.gamil.com',
#     MAIL_PORT=465,
#     MAIL_USE_SSL=True,
#     MAIL_USERNAME=params['gmail-user'],
#     MAIL_PASSWORD=params['gmail-pass']
# )
# mail=Mail(app)

if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']


db = SQLAlchemy(app)


class Contacts(db.Model):
    # sno name email phone_num mes date
    sno = db.Column(db.Integer, primary_key=True)
    nameid = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(30), unique=False, nullable=False)
    phone_num = db.Column(db.String(12), unique=True, nullable=False)
    mes = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(120), nullable=True)


class Posts(db.Model):
    # sno name email phone_num mes date
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=False, nullable=False)
    slug = db.Column(db.String(30), unique=False, nullable=False)
    content = db.Column(db.String(200), unique=False, nullable=False)
    date = db.Column(db.String(120), nullable=False)
    img_file = db.Column(db.String(120))

    # date = db.Column(db.String(120), nullable=True)


@app.route("/")
def home():
    # msg=Message("msg",sender="email",recipients=["lalitchouhan@267@gmail.com"])
    posts = Posts.query.filter_by().all()
    # [0:params['no_of_post']]
    page=request.args.get('page')
    last=math.ceil(len(posts)/int(params['no_of_post']))
    print(last)
    if(not str(page).isnumeric()):
        page=1
    page=int(page)    
    posts=posts[(page-1)* int(params['no_of_post']):(page-1)*int(params['no_of_post'])+int(params['no_of_post'])]

    # pagination logic 
    if (page==1):
        prev="#"
        next="/?page=" +str(page+1)
    elif(page==last):
        next="#"
        prev="/?page="+str(page-1)
    else:
        prev="/?page="+str(page-1)
        
        next="/?page=" +str(page+1)

    

    return render_template('index.html', params=params, posts=posts,prev=prev,next=next)

@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if(request.method == 'POST'):
        name = request.form.get('username')
        email = request.form.get('email')
        phonenum = request.form.get('phonenumber')
        message = request.form.get('message')
        # database wala contacts
        entry = Contacts(nameid=name, email=email,
                         phone_num=phonenum, mes=message)
        db.session.add(entry)
        db.session.commit()
        # mail.send_message('new message from' + name,
        #                 sender=email,
        #                 recipients=[params['gmail-user']],
        #                 body=message + "\n" + phonenum
        #                                 )

    return render_template('contact.html', params=params)


@app.route("/admin", methods=['GET', 'POST'])
def admin():
    if ('user' in session and session['user'] == params['admin_user']):
        posts = Posts.query.all()
        return render_template('dashboard.html', params=params, posts=posts)
    # name="das"
    if request.method == 'POST':
        username = request.form.get('name')
        userpass = request.form.get('pass')
        if(username == params['admin_user'] and userpass == params['admin_password']):
            session['user'] = username
            posts = Posts.query.all()

            # redirect to admin panel
            return render_template('dashboard.html', params=params, posts=posts)
    else:
        return render_template('admin.html', params=params)




@app.route("/about")
def about():
    # name="das"
    return render_template('about.html', params=params)


@app.route("/post/<string:post_slug>", methods=['GET'])
def post(post_slug):
    # name="das"
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html', params=params, post=post)


@app.route("/edit/<string:sno>", methods=['GET', 'POST'])
def edit(sno):
    if ('user' in session and session['user'] == params['admin_user']):
        if request.method == 'POST':
            box_title = request.form.get('title')
            box_slug = request.form.get('slug')
            box_content = request.form.get('content')
            box_imgfile = request.form.get('imagefile')
            date = datetime.now()
            if sno == '0':
                post = Posts(title=box_title, slug=box_slug,
                             content=box_content, img_file=box_imgfile, date=date)
            # return render_template('title.html',params=params)
                db.session.add(post)
                db.session.commit()

            else:
                post = Posts.query.filter_by(sno=sno).first()
                post.title = box_title
                post.slug = box_slug
                post.content = box_content
                post.img_file = box_imgfile
                post.date = date
                db.session.commit()
                return redirect('/edit/'+sno)
        post = Posts.query.filter_by(sno=sno).first()
        return render_template('title.html', params=params, post=post,sno=sno)


@app.route("/logout")
def logout():
    session.pop('user')
    # name="das"
    return redirect('/admin')

@app.route("/delete/<string:sno>", methods=['GET','POST'])
def delete(sno):
    if ('user' in session and session['user'] == params['admin_user']):
        post=Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
        db.execute('delete from post where id=?')
        return redirect('/dashboard')
    
    # name="das"
    # return redirect('/admin')


@app.route("/uploader", methods=['GET','POST'])
def uploader():
    if ('user' in session and session['user'] == params['admin_user']):
        if(request.method=='POST'):
            f=request.files['file1']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename) ))
            return "uploaded successfully"



app.run(debug=True)


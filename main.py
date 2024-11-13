from flask import Flask,render_template,request,redirect,url_for,make_response,session,flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
from functools import wraps
from sqlalchemy.exc import IntegrityError

app=Flask(__name__)
app.secret_key='my_secret_key'

app.config['SQLALCHEMY_DATABASE_URI']="mysql://root:Guna%40123@localhost/myproject"
app.config['SQLALCHEMY_BINDS']={
    'vote_db':'mysql://root:Guna%40123@localhost/myproject'
}
app.config['SQLALCHEMY_TRACK_MODIFICATION']=False

db=SQLAlchemy(app)

class Admin(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100),nullable=False)
    password
    email=db.Column(db.String(100),unique=True)
    voters=db.relationship("Voter",backref="admin",lazy=False)
class Voter(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100),nullable=False)
    voter_id=db.Column(db.Integer,unique=True)
    admin_id=db.Column(db.Integer,db.ForeignKey('admin.id'),nullable=False)

class Vote(db.Model):
    __bind_key__ = 'vote_db'
    __tablename__='vote'
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100),nullable=False)
    vote=db.Column(db.Integer)
    vote_id=db.Column(db.Integer,unique=True)

@app.before_request
def create():
 db.create_all()
 db.create_all(bind_key=['vote_db'])

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "email" not in session:
            flash("Please log in to access this page.", "danger")
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    return wrapper

@app.route('/')
def index():
    return render_template("home_page.html")

@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method=="POST":
      try:
        username=request.form['username']
        password=request.form['password']
        email=request.form['email']

        admin = Admin.query.filter(Admin.email == email).first()
        if admin:
            return render_template("sign_up.html", new_flask=flash("Already you have account...please login", 'danger'))

        admin=Admin(name=username,password=password,email=email)
        db.session.add(admin)
        db.session.commit()
        session['id']=admin.id
        session['email']=admin.email
        flash("your account is created", 'success')
      except IntegrityError:
          flash("try another email","danger")
    return render_template("sign_up.html")

@app.route('/login',methods=['POST','GET'])
def login():
    if request.method=='POST':
      try:
        password=request.form['password']
        email=request.form['email']
        admin=Admin.query.filter(and_(Admin.password==password,Admin.email==email)).first()
        print(admin)
        session['id']= admin.id
        print(session['id'])
        session['email']=admin.email
        return redirect("/admin")
      except AttributeError:
          flash("you dont have any account.. please signup!!!",'danger')
    return render_template("log_in.html")

@app.route('/voters_list')
@login_required
def voters_list():
    admin_id=session['id']
    print(admin_id)
    voters=Voter.query.filter(Voter.admin_id==admin_id).all()
    return render_template("voters_list.html",voters=voters)


@app.route('/admin')
@login_required
def admin():
    admin_email=session['email']
    if admin_email:
        admin_details=Admin.query.filter(Admin.email==admin_email).first()
        return render_template("admin.html",admin_details=admin_details)
    else:
        return redirect('/index')

@app.route('/add_user',methods=['POST','GET'])
@login_required
def add_user():
    admin_id=session['id']

    if request.method=='POST':
        name=request.form['name']
        voter_id=request.form['voter_id']
        # if voter:
        #     check_voter=Voter.query.filter_by(Voter.id==voter.id)
        #     flash("")
        voter = Voter(name=name, voter_id=voter_id, admin_id=admin_id)
        db.session.add(voter)
        db.session.commit()
        flash("voters updated",'success')
    return render_template("add_user_form.html",all_voters=Voter.query.all())


@app.route('/vote',methods=['GET','POST'])
@login_required
def vote():
  if request.method=="POST":
   try:
     python=[]
     java=[]
     script=[]
     name=request.form['name']
     voter_id=request.form['voter_id']
     voter=Voter.query.filter(Voter.voter_id==voter_id).first()
     if voter.id:
         if name=='Python':
             votes=1
             python.append(name)
             python.append(votes)
             python.append(voter_id)
             python=name,votes,voter_id
             vote_data_add=Vote(name=name,vote=votes,vote_id=voter_id)
             db.session.add(vote_data_add)
             db.session.commit()
             del python
             return redirect(url_for("vote"))
         elif name=='Java':
             votes=1
             java.append(name)
             java.append(votes)
             java.append(voter_id)
             java=name,votes,voter_id
             vote_data_add=Vote(name=name,vote=votes,vote_id=voter_id)
             db.session.add(vote_data_add)
             db.session.commit()
             del java
             return redirect(url_for("vote"))
         elif name=='JavaScript':
             votes=1
             script.append(name)
             script.append(votes)
             script.append(voter_id)
             script=name,votes,voter_id
             vote_data_add=Vote(name=name,vote=votes,vote_id=voter_id)
             db.session.add(vote_data_add)
             db.session.commit()
             del script
             return redirect(url_for("vote"))
   except IntegrityError:
       flash("already you voted ","danger")
  return render_template("vote.html")

@app.route('/view_vote')
@login_required
def view_vote():
    python=Vote.query.filter(Vote.name=='python').count()
    java=Vote.query.filter(Vote.name=='java').count()
    script=Vote.query.filter(Vote.name=='javascript').count()

    return render_template("view_vote.html",python=python,java=java,script=script)




@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')



if __name__=="__main__":
    app.run(debug=True)




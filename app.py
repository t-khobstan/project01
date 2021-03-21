import os
import requests
import datetime 
import json
from flask import Flask, session,render_template,request,redirect,url_for,flash
from flask_assets import Environment, Bundle
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from functools import wraps



app = Flask(__name__)
"""
# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")
"""
css=Bundle('css/bootstrap.min.css','css/style.css',output='gen/main.css')
js=Bundle('js/jquery.slim.min.js','js/popper.min.js','js/bootstrap.min.js','js/myjs.js',output='gen/all.js')
assets=Environment(app)
assets.register('main_js',js)
assets.register('main_css',css)


# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine= create_engine("postgres://nuxxobzishgsqu:dcac47a4e6fb98f212343ee66fcef1419e29d6ff93bf9203e6118cdfaee2ea00@ec2-174-129-227-51.compute-1.amazonaws.com:5432/dcv18nm8jcev6s")
db =scoped_session(sessionmaker(bind=engine))


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if len(session.get("username"))==0:
            flash("Create an account first or Sign in if already have one, Please.")
            return render_template("index.html")
        return f(*args, **kwargs)
    return decorated_function



@app.route("/")
def index():
        if session.get("username") is None:
                session["username"]=[]
        return render_template("index.html",username=session["username"])

@app.route("/join",methods=["GET","POST"])
def joinUs():
        if request.method=='GET':
                return render_template("join_us.html")
        else:
                email=request.form.get("email")
                userPassword=request.form.get("userPassword")
                if db.execute("SELECT * from users WHERE username=:us",{'us':email}).rowcount>0:
                        flash('Invalid already existe', 'error')
                        return render_template("join_us.html")
                else:
                        db.execute("INSERT INTO users (username,password) VALUES (:a,:b)",{'a':email,'b':userPassword})
                        db.commit()
                        message="Success! You can "
        return render_template("success.html",message=message)               
                
@app.route("/sign",methods=["GET","POST"])
def signIn():
        if request.method=='GET':
                return render_template("sign_in.html")
        else:
            signInEmail=request.form.get('signInEmail')    
            signInPassword=request.form.get('signInPassword') 
            data=db.execute("SELECT * FROM users WHERE username=:user and password=:password",{"user":signInEmail,"password":signInPassword}).fetchone() 
            
            if data!=None:
                    if data.username==signInEmail and data.password==signInPassword:
                            
                            session["username"]=data.username[:data.username.find("@")]
                            return render_template('search.html',username=session["username"])
                    
            else:
                   flash("Wrong email or password. Try again.,'error'") 
        
        return render_template("sign_in.html")

@app.route('/logout')
def logout():
        session.clear()
        return redirect(url_for('index'))

@app.route("/search",methods=["GET","POST"])
@login_required
def search():
         
        username=session.get("username")
        message=""
        if request.method=="GET":
                return render_template("search.html",username=username)
        else:
                text=request.form.get("search")
                session["books"]=[]
                data=db.execute("SELECT * FROM books WHERE isbn iLIKE ('%' || :a || '%')  or title ILIKE ('%' || :a || '%') or author ILIKE ('%' || :a || '%')    ",{"a":text}).fetchall()
                if len(data)==0 :
                        message="Nothing found. Try againg"
                else:
                        message=len(data)
                        if session.get("books") is None:
                                session["books"]=[]
                        else:
                                for book in data:
                                        session["books"].append(book)        
        return render_template("search.html",data=session["books"],message=message,username=username)
@app.route("/details/<isbn>",methods=["GET","POST"])

def bookPage(isbn):
                
                username=session.get("username")
                data=db.execute("SELECT * FROM books WHERE isbn=:isbn_id ",{"isbn_id":isbn}).fetchone()
                                 
                res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "InKyxvwZeo0RZRSPvdxpvw","isbns":isbn })
                work_ratings_count=res.json()["books"][0]["work_ratings_count"]     
                average_rating =res.json()["books"][0]["average_rating"] 
                
                if session.get("reviews") is None:
                        session["reviews"]=[]

                if request.method=="GET":        
                        reviews=db.execute("SELECT review,rating,username,time,books.isbn FROM books JOIN reviews ON (books.isbn=reviews.isbn) WHERE books.isbn=:isbn  ",{"isbn":isbn}).fetchall() 
                        session["reviews"]=[]
                        for review in reviews:
                                session["reviews"].append(review)

                if request.method=="POST":
                                                   
                        if db.execute("SELECT * FROM reviews WHERE  isbn=:isbn",{"isbn":isbn}).rowcount==0:
                                db.execute("SELECT * FROM reviews WHERE username=:user and isbn=:isbn",{"user":username,"isbn":isbn})
                                rating=request.form.get("rating")
                                review=request.form.get("comment")
                                time=datetime.datetime.now()

                                time=time.strftime(" %d / %m /%y  %X " ) 
                                session["reviews"].append(review)
                                if rating is None and review =="": 
                                         flash(" Rating or review is empty ")                                      
                                else:
                                        db.execute("INSERT INTO reviews (isbn,review,rating,username,time) VALUES (:isbn,:review,:rating,:username, :time)",{"isbn":isbn ,"review":review ,"rating":rating ,"username": username,"time":time}) 
                                        db.commit() 
                                
                                    
                                 
                        else: 
                                flash("Sorry. You cannot add second review.")  
                          
                        reviews=db.execute("SELECT review,rating,username,time,books.isbn FROM books JOIN reviews ON (books.isbn=reviews.isbn) WHERE books.isbn=:isbn",{"isbn":isbn}).fetchall() 
                        
                        for review in reviews:
                                session["reviews"].append(review)
                return render_template("bookPage.html",data=data,username=username,work_ratings_count=work_ratings_count,average_rating=average_rating,reviews=session["reviews"])
@app.route("/api/<string:isbn>") 
@login_required
def api(isbn):
        data=db.execute("SELECT * FROM books WHERE isbn=:isbn",{"isbn":isbn}).fetchone()
        if data is None:
                return redirect(url_for('page_non_trouvee'))
        
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "InKyxvwZeo0RZRSPvdxpvw","isbns":isbn })
        work_ratings_count=res.json()["books"][0]["work_ratings_count"]     
        average_rating =res.json()["books"][0]["average_rating"] 
        book={
        "title": data.title,
        "author": data.author,
        "year": data.year,
        "isbn": data.isbn,
        "review_count": work_ratings_count,
        "average_score":average_rating
        }

        api=json.dumps(book)
        return api
        
@app.route('/404')
def page_non_trouvee():
        return " 404 Nothing found. Try againg",404        


    



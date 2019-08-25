import os
import csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker



engine= create_engine("postgres://nuxxobzishgsqu:dcac47a4e6fb98f212343ee66fcef1419e29d6ff93bf9203e6118cdfaee2ea00@ec2-174-129-227-51.compute-1.amazonaws.com:5432/dcv18nm8jcev6s")
db =scoped_session(sessionmaker(bind=engine))



def main():
    db.execute("CREATE TABLE users(id SERIAL PRIMARY KEY ,username VARCHAR NOT NULL,password VARCHAR NOT NULL)")
    db.execute("CREATE TABLE reviews(isbn VARCHAR NOT NULL ,review VARCHAR NOT NULL,rating INTEGER NOT NULL,username VARCHAR NOT NULL)")
    db.execute("CREATE TABLE books(isbn VARCHAR PRIMARY KEY ,title VARCHAR NOT NULL,author VARCHAR NOT NULL,year VARCHAR NOT NULL)")
    
    f=open("books.csv")
    reader=csv.reader(f)
    for isbn,title,author,year in reader:
        if isbn=="isbn":
            print("skip first line")
        else:
            db.execute("INSERT INTO books(isbn,title,author,year)VALUES(:isbn,:title,:author,:year)",{"isbn":isbn,"title":title,"author":author,"year":year})
    print("done")

    db.commit()






if __name__=="__main__":
    main()
    

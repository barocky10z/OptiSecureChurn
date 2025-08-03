from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
#from connect import get_db
from dotenv import load_dotenv
import os

load_dotenv()

dbusername = os.getenv("dbusername")
dbpassword = os.getenv("dbpassword")
dbhost = os.getenv("dbhost")
dbname = os.getenv("dbname")
dbport = os.getenv("dbport")

DATABASE_URL = f"mysql+pymysql://{dbusername}:{dbpassword}@{dbhost}:{dbport}/{dbname}"  

engine = create_engine(DATABASE_URL)
session = sessionmaker(bind=engine)
Base = declarative_base()

def getdb():
    db = session()
    return db
    


    
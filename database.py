from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

connectionString = "postgresql://bills:itsover9000@localhost/bills"
engine = create_engine(connectionString, echo=False)

db_session = scoped_session(sessionmaker(bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
	Base.metadata.create_all(bind=engine)
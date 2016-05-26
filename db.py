import sqlalchemy.orm as orm
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Date
from sqlalchemy.orm import relationship
import bcrypt

Base = declarative_base()

Session = orm.scoped_session(orm.sessionmaker())

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    email = Column(String, unique=True)
    pw_hash = Column(String)
    salt = Column(String)
    signedin = Column(Boolean)
    scheduleverified=Column(Boolean)
    schedule=Column(String)
    signins = relationship("Signin", back_populates="user")
    events = relationship("Event", back_populates="user")

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def check_password(self, password):
        return self.pw_hash == bcrypt.hashpw(password.encode('utf-8'), self.salt)

    def is_admin(self):
        if self.email == 'daynb@guilford.edu':
            return True
        elif self.email == 'kiddlm@guilford.edu':
            return True
        else:
            return False

    def __repr__(self):
        return "<User(name='%s')>" % (self.name)

class Signin(Base):
    __tablename__ = 'signins'

    id = Column(Integer, primary_key=True)
    date_in = Column(DateTime)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="signins")

    def __repr__(self):
        return "<Signin(id='%s')>" % (self.id)

class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True)
    from_date = Column(Date)
    to_date = Column(Date)
    title = Column(String)
    description = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="events")

    def __repr__(self):
        return "<Event(id='%s')>" % (self.id)

import sqlalchemy.orm as orm
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
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
    signins = relationship("Signin", back_populates="user")

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def check_password(self, password):
        return self.pw_hash == bcrypt.hashpw(password.encode('utf-8'), self.salt)

    def is_admin(self):
        return self.email == 'daynb@guilford.edu'

    def __repr__(self):
        return "<User(name='%s')>" % (self.name)

class Signin(Base):
    __tablename__ = 'signin'

    id = Column(Integer, primary_key=True)
    date_in = Column(DateTime)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="signins")

    def __repr__(self):
        return "<Signin(id='%s')>" % (self.id)

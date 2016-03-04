import falcon
import sqlalchemy as sa
from falcon_cors import CORS

import db
from db import Session, Base
from middleware import RequireJSON, JSONTranslator, SQLAlchemySessionManager, JWTAuthenticator
import users
import events

engine = sa.create_engine('sqlite:///data.db')
Session.configure(bind=engine)
Base.metadata.create_all(engine)

api = application = falcon.API(middleware=[
    CORS(allow_all_origins=True),
    RequireJSON(),
    JSONTranslator(),
    JWTAuthenticator(),
    SQLAlchemySessionManager(Session)])

register = users.Register()
login = users.Login()

user_collection = users.Collection()

event_collection = events.Collection()
event = events.Item()

logout = users.Logout()

api.add_route('/login', login)
api.add_route('/logout', logout)
api.add_route('/register', register)
api.add_route('/events', event_collection)
api.add_route('/events/{item_id}', event)
api.add_route('/users', user_collection)

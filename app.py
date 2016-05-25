import falcon
import sqlalchemy as sa
from falcon_cors import CORS

import db
from db import Session, Base
from middleware import RequireJSON, JSONTranslator, SQLAlchemySessionManager, JWTAuthenticator
import users
import signins
import events

engine = sa.create_engine('sqlite:///data.db')
Session.configure(bind=engine)
Base.metadata.create_all(engine)

headers = ['Authorization']

cors = CORS(allow_all_origins=True, allow_all_headers=True,
        allow_all_methods=True, allow_credentials_all_origins=True,
        expose_headers_list=headers)

api = application = falcon.API(middleware=[
    cors.middleware,
    RequireJSON(),
    JSONTranslator(),
    JWTAuthenticator(),
    SQLAlchemySessionManager(Session)])

register = users.Register()
login = users.Login()

user_collection = users.Collection()
user = users.Item()

signin_collection = signins.Collection()
signin = signins.Item()

event_collection = events.Collection()
event = events.Item()

logout = users.Logout()

api.add_route('/login', login)
api.add_route('/logout', logout)
api.add_route('/register', register)
api.add_route('/signins', signin_collection)
api.add_route('/signins/{item_id}', signin)
api.add_route('/events', event_collection)
api.add_route('/events/{item_id}', event)
api.add_route('/users', user_collection)
api.add_route('/users/{item_id}', user)

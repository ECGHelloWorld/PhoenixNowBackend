import falcon
import bcrypt
import base64
from db import User, Session
from sqlalchemy import exc

def unauthorized_user(req):
    req.context['user'] = None
    description = "User was not found in database"
    title = "Unauthorized Access"
    raise falcon.HTTPUnauthorized(title=title, description=description)


def get_user(req, resp):
    if 'user' in req.context:
        user = Session.query(User).get(req.context['user'])
        if user is None:
            unauthorized_user(req)
    if 'doc' in req.context:
        doc = req.context['doc']
        if 'email' in doc:
            user = Session.query(User).filter_by(email=doc['email']).first()
            if user is None:
                unauthorized_user(req)

        if 'password' in doc:
            if not user.check_password(doc['password']):
                unauthorized_user(req)

    return user

class Register(object):
    def on_post(self, req, resp):
        doc = req.context['doc']
        try: 
            user = User(name=doc['name'], email=doc['email'])
            user.salt = bcrypt.gensalt()
            user.pw_hash = bcrypt.hashpw(doc['password'].encode('utf-8'), user.salt)
            Session.add(user)
            Session.flush()
        except exc.IntegrityError:
            description = "User was already made"
            title = "User creation conflict"
            raise falcon.HTTPConflict(title=title, description=description)
        Session.commit()
        req.context['user'] = user.id
        req.context['result'] = {"result": "success", "action": "register"}

class Collection(object):
    def on_get(self, req, resp):
        json_users = []
        users = Session.query(User).all()
        for user in users:
            json_user = {
                "id": user.id,
                "name": user.name,
                "email": user.email,
            }
            json_users.append(json_user)

        req.context['result'] = {"users": json_users}

class Login(object):
    def on_post(self, req, resp):
        user = get_user(req, resp)

        req.context['user'] = user.id
        req.context['result'] = {"result": "success", "action": "login"}
        resp.status = falcon.HTTP_200

class Logout(object):
    def on_get(self, req, resp):
        req.context['user'] = None
        resp.status = falcon.HTTP_200
        req.context['result'] = {"result": "success", "action": "logout"}

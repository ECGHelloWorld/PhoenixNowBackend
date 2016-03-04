import falcon
import bcrypt
import base64
from db import User, Session
from sqlalchemy import exc

def get_user(req, resp):
    user = Session.query(User).get(req.context['user'])
    if user is None:
        req.context['user'] = None
        description = "User was not found in database"
        title = "Unauthorized Access"
        raise falcon.HTTPUnauthorized(title=title, description=description)
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
        doc = req.context['doc']
        user = get_user(req, resp)

        if user.check_password(doc['password']):
            req.context['user'] = user.id
            req.context['result'] = {"result": "success", "action": "login"}
            resp.status = falcon.HTTP_200
        else:
            req.context['result'] = {"result": "failure", "action": "login"}

class Logout(object):
    def on_get(self, req, resp):
        req.context['user'] = None
        resp.status = falcon.HTTP_200
        req.context['result'] = {"result": "success", "action": "logout"}

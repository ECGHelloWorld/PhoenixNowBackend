import falcon
import bcrypt
import base64
from db import User, Session

class Register(object):
    def on_post(self, req, resp):
        doc = req.context['doc']
        user = User(name=doc['name'], email=doc['email'])
        user.salt = bcrypt.gensalt()
        user.pw_hash = bcrypt.hashpw(doc['password'].encode('utf-8'), user.salt)
        Session.add(user)
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
                "pw_hash": base64.b64encode(user.pw_hash).decode('utf-8'),
                "salt": base64.b64encode(user.salt).decode('utf-8'),
                "email": user.email,
            }
            json_users.append(json_user)

        req.context['result'] = {"users": json_users}

class Login(object):
    def on_post(self, req, resp):
        doc = req.context['doc']
        user = Session.query(User).filter_by(email=doc['email']).first()
        if user is None:
            return

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

import falcon
import bcrypt
import base64
from db import User, Session
from sqlalchemy import exc
import smtplib
from email.mime.text import MIMEText
from random import randint

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

class Item(object):
    def on_get(self, req, resp, item_id):
        user = get_user(req, resp)

        if user.is_admin():
            user = Session.query(User).get(item_id)
            signins_json = []
            for signin in user.signins:
                date = signin.date_in.strftime("%Y-%m-%d")
                signins_json.append({'id': signin.id, 'date': date})

            req.context['result'] = {
                    'action': 'get signins',
                    'result': 'success',
                    'signins': signins_json
            }

            resp.status = falcon.HTTP_200
        else:
            description = "User is not administrator and can not access this information"
            title = "User unauthorized"
            raise falcon.HTTPUnauthorized(title=title, description=description)
    def on_post(self,req,resp,item_id):
        user=get_user(req,resp)

        if user.is_admin():
            user=Session.query(User).get(item_id)
            user.scheduleverified=True
            user.finalschedule=user.schedule
            Session.commit()
            resp.status=falcon.HTTP_200
            req.context['result']={'action':'verify_schedule','result':'success'}
        else:
            description = "User is not administrator and can not change this information"
            title = "User unauthorized"
            raise falcon.HTTPUnauthorized(title=title, description=description)

class Register(object):
    def on_post(self, req, resp):
        doc = req.context['doc']
        users=Session.query(User).all()
        unique=True
        for user in users:
            if doc['email'] == user.email:
                unique=False
        if unique:
            user = User(name=doc['name'], email=doc['email'], signedin=False)
            user.salt = bcrypt.gensalt()
            user.pw_hash = bcrypt.hashpw(doc['password'].encode('utf-8'), user.salt)
            s=smtplib.SMTP_SSL('smtp.gmail.com',465)
            s.ehlo()
            s.login('phoenixnownoreply@gmail.com','helloworld@ppclub')
            code=randint(1000,9999)
            user.code=code
            msg=MIMEText('Hi '+user.name+', your verification code is: '+str(code))
            msg['From']='phoenixnownoreply@gmail.com'
            msg['To']=user.email
            msg['Subject']='PhoenixNow Account Confirmation'
            s.send_message(msg)
            s.close()
            Session.add(user)
            Session.flush()
        else:
            description = "User was already made"
            title = "User creation conflict"
            raise falcon.HTTPConflict(title=title, description=description)
        Session.commit()
        req.context['user'] = user.id
        req.context['result'] = {"result": "success", "action": "register"}

class Collection(object):
    def on_get(self, req, resp):
        user = get_user(req, resp)

        if user.is_admin():
            json_users = []
            users = Session.query(User).all()
            for user in users:
                json_user = {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "signedin": str(user.signedin),
                    "schedule":user.schedule,
                    "scheduleverified":str(user.scheduleverified),
                    "finalschedule":user.finalschedule
                }
                json_users.append(json_user)

            req.context['result'] = {"users": json_users}
        else:
            description = "User is not administrator and can not access this information"
            title = "User unauthorized"
            raise falcon.HTTPUnauthorized(title=title, description=description)

class Login(object):
    def on_post(self, req, resp):
        user = get_user(req, resp)
        if user.emailVerified:
            req.context['user'] = user.id
            req.context['result'] = {"result": "success", "action": "login"}
            resp.status = falcon.HTTP_200
        else:
            doc=req.context['doc']
            if doc['code']=='null':
                resp.status=falcon.HTTP_201
            else:
                if doc['code']==str(user.code):
                    user.emailVerified=True
                    Session.commit()
                    req.context['user'] = user.id
                    req.context['result'] = {"result": "success", "action": "login"}
                    resp.status = falcon.HTTP_200
                else:
                    resp.status=falcon.HTTP_202


class Logout(object):
    def on_get(self, req, resp):
        req.context['user'] = None
        resp.status = falcon.HTTP_200
        req.context['result'] = {"result": "success", "action": "logout"}

class Schedule(object):
    def on_post(self, req,resp):
        doc=req.context['doc']

        m=doc['M']
        t=doc['T']
        w=doc['W']
        r=doc['R']
        f=doc['F']

        user=get_user(req,resp)
        user.schedule=""
        if m=="true":
            user.schedule=user.schedule+"M"
        if t=="true":
            user.schedule=user.schedule+"T"
        if w=="true":
            user.schedule=user.schedule+"W"
        if r=="true":
            user.schedule=user.schedule+"R"
        if f=="true":
            user.schedule=user.schedule+"F"
        Session.commit()
class GetSchedule(object):
    def on_post(self,req,resp):
        user=get_user(req,resp)
        req.context['result']={"VerifiedSchedule":user.finalschedule, "SubmittedSchedule":user.schedule}
        resp.status=falcon.HTTP_200

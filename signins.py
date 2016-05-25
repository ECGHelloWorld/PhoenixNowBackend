import falcon
import datetime
from db import Signin, Session, User
from users import get_user

class Collection(object):
    def on_get(self, req, resp):
        user = get_user(req, resp)

        if user.is_admin():
            signins = Session.query(Signin).all()
        else:
            signins = Session.query(Signin).filter_by(user=user).all()

        signins_json = []
        for signin in signins:
            date = signin.date_in.strftime("%Y-%m-%d")
            signins_json.append({'id': signin.id, 'date': date})

        req.context['result'] = {
                'action': 'get signins',
                'result': 'success',
                'signins': signins_json
        }

        resp.status = falcon.HTTP_200

    def on_post(self, req, resp):
        doc = req.context['doc']
        lat = doc['lat']
        lon = doc['lon']
        date_in = datetime.datetime.utcnow()
        if lat and lon:
            user = get_user(req, resp)

        if lon >= -79.8921061:
            if lon <= -79.8833942:
                if lat <= 36.0984408:
                    if lat >= 36.0903956:
                        signin = Signin(date_in=date_in, user=user)
                        user.signedin = True
                        Session.add(signin)
                        Session.commit()

                        resp.status = falcon.HTTP_201
                        resp.location = '/signins/%s' % (signin.id)
                        req.context['result'] = {"action": "sign in", "result": "success"}
            else:
                resp.status = falcon.HTTP_409
                req.context['result'] = {"action": "sign in", "result": "failure"}

        else:
            resp.status = falcon.HTTP_409
            req.context['result'] = {"action": "sign in", "result": "failure"}

class Item(object):
    def on_get(self, req, resp, item_id):
        user = Session.query(User).get(req.context['user'])
        signin = Session.query(Signin).get(item_id)
        if signin.user == user or user.is_admin():
            date_in = signin.date_in.strftime("%Y-%m-%d")
            req.context['result'] = {
                    'action': 'get signin',
                    'result': 'success',
                    'signin': {
                        "id": signin.id,
                        "date": date_in
                    }
            }
            resp.status = falcon.HTTP_200
        else:
            req.context['result'] = {
                'action': 'get signin',
                'result': 'failure',
                'error': 'wrong user'
            }
            resp.status = falcon.HTTP_401

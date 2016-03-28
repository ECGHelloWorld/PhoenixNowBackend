import falcon
import datetime
from db import Event, Session, User
from users import get_user

class Collection(object):
    def on_get(self, req, resp):
        user = get_user(req, resp)

        if user.is_admin():
            events = Session.query(Event).all()
        else:
            events = Session.query(Event).filter_by(user=user).all()

        events_json = []
        for event in events:
            date = event.date_in.strftime("%Y-%m-%d")
            events_json.append({'id': event.id, 'date': date})

        req.context['result'] = {
                'action': 'get events',
                'result': 'success',
                'events': events_json
        }

        resp.status = falcon.HTTP_200

    def on_post(self, req, resp):
        doc = req.context['doc']
        lat = doc['lat']
        lon = doc['lon']
        date_in = datetime.datetime.utcnow()
        if lat and lon:
            user = get_user(req, resp)

            if lon >= -79.8833942:
                if lat <= 36.0984408:
                    if lat >= 36.0903956:
                        event = Event(date_in=date_in, user=user)
                        Session.add(event)
                        Session.commit()

                        resp.status = falcon.HTTP_201
                        resp.location = '/events/%s' % (event.id)
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
        event = Session.query(Event).get(item_id)
        if event.user == user or user.is_admin():
            date_in = event.date_in.strftime("%Y-%m-%d")
            req.context['result'] = {
                    'action': 'get event',
                    'result': 'success',
                    'event': {
                        "id": event.id,
                        "date": date_in
                    }
            }
            resp.status = falcon.HTTP_200
        else:
            req.context['result'] = {
                'action': 'get event',
                'result': 'failure',
                'error': 'wrong user'
            }
            resp.status = falcon.HTTP_401

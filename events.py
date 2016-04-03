import falcon
import datetime
from db import Event, Session, User
from users import get_user

class Collection(object):
    def on_get(self, req, resp):
        user = get_user(req, resp)

        events = Session.query(Event).all()

        events_json = []
        for event in events:
            from_date = event.from_date.strftime("%Y-%m-%d")
            to_date = event.to_date.strftime("%Y-%m-%d")
            events_json.append({
                'id': event.id,
                'from_date': from_date,
                'to_date': to_date,
                'title': event.title,
                'description': event.description
            })

        req.context['result'] = {
                'action': 'get events',
                'result': 'success',
                'events': events_json
        }

        resp.status = falcon.HTTP_200

    def on_post(self, req, resp):
        doc = req.context['doc']

        title = doc['title']
        description = doc['description']
        from_date = doc['from_date']
        to_date = doc['to_date']

        from_date_datetime = datetime.datetime.strptime(from_date, "%Y-%m-%d")
        to_date_datetime = datetime.datetime.strptime(to_date, "%Y-%m-%d")

        user = get_user(req, resp)

        event = Event(from_date=from_date_datetime, to_date=to_date_datetime, title=title,
                description=description, user=user)
        Session.add(event)
        Session.commit()

        resp.status = falcon.HTTP_201
        req.context['result'] = {"action": "add event", "result": "success",
                "event": {
                    'id': event.id,
                    'from_date': from_date,
                    'to_date': to_date,
                    'title': event.title,
                    'description': event.description
                }
            }

class Item(object):
    def on_get(self, req, resp, item_id):
        event = Session.query(Event).get(item_id)
        from_date = event.from_date.strftime("%Y-%m-%d")
        to_date = event.to_date.strftime("%Y-%m-%d")
        req.context['result'] = {
                'action': 'get event',
                'result': 'success',
                'event': {
                    'id': event.id,
                    'from_date': from_date,
                    'to_date': to_date,
                    'title': event.title,
                    'description': event.description
                }
        }
        resp.status = falcon.HTTP_200

    def on_delete(self, req, resp, item_id):
        event = Session.query(Event).get(item_id)
        from_date = event.from_date.strftime("%Y-%m-%d")
        to_date = event.to_date.strftime("%Y-%m-%d")
        req.context['result'] = {
                'action': 'delete event',
                'result': 'success',
                'event': {
                    'id': event.id,
                    'from_date': from_date,
                    'to_date': to_date,
                    'title': event.title,
                    'description': event.description
                }
        }
        resp.status = falcon.HTTP_200
        Session.delete(event)
        Session.commit()

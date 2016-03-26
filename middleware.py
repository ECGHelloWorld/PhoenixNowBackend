import jwt
import falcon
import json
import sqlalchemy.orm.scoping as scoping

class JWTAuthenticator(object):
    def process_request(self, req, resp):
        if req.method == "OPTIONS":
            return 

        token = req.get_header('Authorization')

        if req.path != '/register' and req.path != '/login':
            if token is None:
                description = ('Please provide an auth token '
                               'as part of the request.')

                raise falcon.HTTPUnauthorized('Auth token required',
                                              description,
                                              href='http://docs.example.com/auth')

        if token != None:
            try:
                token = token.split()
                decoded_token = jwt.decode(token[1], 'habberdashery212', algorithm='HS512', verify=False)
                req.context['user'] = decoded_token['user']

            except jwt.exceptions.DecodeError:
                description = ('The provided auth token is not valid. '
                               'Please request a new token and try again.')
                description += token[2]

                raise falcon.HTTPUnauthorized('Authentication required',
                                              description,
                                              href='http://docs.example.com/auth',
                                              scheme='Token; UUID')

    def process_response(self, req, resp, resource):
        if 'user' in req.context:
            if req.context['user'] is not None:
                result = req.context['result']
                result['user'] = req.context['user']

                token = jwt.encode(result, 'habberdashery212', algorithm='HS512')

                resp.set_header('Authorization', "Bearer " + token.decode('utf-8'))
                result['token'] = "Bearer " + token.decode('utf-8')


class SQLAlchemySessionManager(object):
    def __init__(self, session_factory, auto_commit=False):
        self._session_factory = session_factory
        self._scoped = isinstance(session_factory, scoping.ScopedSession)
        self._auto_commit = auto_commit

    def process_request(self, req, resp):
        req.context['session'] = self._session_factory

    def process_response(self, req, resp, params):
        session = req.context['session']

        if self._auto_commit:
            session.commit()

        if self._scoped:
            session.remove()
        else:
            session.close()

class RequireJSON(object):

    def process_request(self, req, resp):
        if not req.client_accepts_json:
            raise falcon.HTTPNotAcceptable(
                'This API only supports responses encoded as JSON.',
                href='http://docs.examples.com/api/json')

        if req.method in ('POST', 'PUT'):
            if req.content_type is not None:
                if 'application/json' not in req.content_type:
                    raise falcon.HTTPUnsupportedMediaType(
                        'This API only supports requests encoded as JSON.',
                        href='http://docs.examples.com/api/json')


class JSONTranslator(object):

    def process_request(self, req, resp):
        # req.stream corresponds to the WSGI wsgi.input environ variable,
        # and allows you to read bytes from the request body.
        #
        # See also: PEP 3333
        if req.content_length in (None, 0):
            # Nothing to do
            return

        body = req.stream.read()
        if not body:
            raise falcon.HTTPBadRequest('Empty request body',
                                        'A valid JSON document is required.')

        try:
            req.context['doc'] = json.loads(body.decode('utf-8'))

        except (ValueError, UnicodeDecodeError):
            raise falcon.HTTPError(falcon.HTTP_753,
                                   'Malformed JSON',
                                   'Could not decode the request body. The '
                                   'JSON was incorrect or not encoded as '
                                   'UTF-8.')

    def process_response(self, req, resp, resource):
        if 'result' not in req.context:
            return

        resp.body = json.dumps(req.context['result'])


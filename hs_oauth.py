"""A client for the HackerSchool OAuth API.

The script aims to do stuff without having a web-server as the "middle man"
"""
from __future__ import absolute_import, print_function

import getpass
import re

from requests import get, post, Session

HS_ID = ''
HS_SECRET = ''

# The redirect url should match exactly with the url provided when
# registering the client, if one was provided.
# This URI is a special one, which prevents any redirects and puts the
# authorization code, directly in the URI.  This is only being used
# for demonstation purposes.
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'

#### Auth server end-points
HS_BASE_URL = 'https://www.hackerschool.com'
HS_AUTHORIZE_URL= HS_BASE_URL + '/oauth/authorize'
HS_ACCESS_TOKEN_URL= HS_BASE_URL + '/oauth/token'


def get_hs_credentials():
    """ Get the credentials of the user. """

    username = raw_input('HS Email: ').strip()
    password = getpass.getpass('HS Password: ').strip()

    return username, password


def get_authenticated_session(username=None, password=None):
    """ Return a session authenticated with the HS site. """

    if not username or not password:
        username, password =  get_hs_credentials()

    session = _authenticate(Session(), username, password)

    return session


def get_access_token(session=None, username=None, password=None):
    """ Get the access token from the server.

    Return a (access_token, refresh_token) pair.

    """

    if session is None:
        session = get_authenticated_session(username, password)

    # Request the authorization server for the code.
    _request_authorization_grant(session)

    # The auth server redirects our session to the specified REDIRECT_URI.  We
    # parse the redirected url to get the code.
    code_url = _authorize_client(session).url
    code = _get_code(code_url)

    # Request the tokens
    return _request_access_token(code)

def request(access_token, resource):
    """ Client requests a protected resource. """

    headers = {'Authorization': 'Bearer %s' % access_token}
    return get(resource, headers=headers).json()

#### Private protocol #########################################################

def _authenticate(session, username, password):
    """ Resource owner authenticates. """

    data = {
        'email': username,
        'password': password,
        'commit': 'Log+in',
        'authenticity_token': _get_authenticity_token(session),
    }
    session.post('https://www.hackerschool.com/sessions', data=data)

    return session


def _authorize_client(session):
    """ Emulates the resource owner authorizing the client.

    This function is essentially clicking on the "authorize" button
    shown on the familiar "do you want to allow bogus-application to
    use your hackerschool data?" page.

    """

    if not HS_ID or not HS_SECRET:
        raise ValueError('Need a valid HS client ID and secret.')

    data = {
        'client_id': HS_ID,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        }

    return session.post(HS_AUTHORIZE_URL, data=data)

def _get_authenticity_token(session):
    """ Parse the page to get the authenticity token. """

    response = session.get('https://www.hackerschool.com/login')
    matches = re.findall('<meta.*content="(.*?)".*name="(.*)".*/>', response.text)

    for content, name in matches:
        if name == 'csrf-token':
            return content

    raise ValueError('Could not find authenticity token')


def _get_code(url):
    """ A client-internal method to get the authentication code.

    Ideally, on user autorization, the user is redirected to a client
    url, where the client can obtain the code.

    In this example we cheat and call the method directly with the
    url.

    """

    _, code = url.rsplit('/', 1)

    return code


def _request_access_token(code):
    """ Client requests an access token using an authorization code.

    'grant_type', 'code', 'redirect_uri', 'client_id' and
    'client_secret' (if one was provided during registration) are all
    required parameters.

    """

    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI
        }

    response_data = post(
        HS_ACCESS_TOKEN_URL, data=data, auth=(HS_ID, HS_SECRET)
    ).json()

    return response_data['access_token'], response_data['refresh_token']


def _request_authorization_grant(session):
    """ Client requests for authorization.

    NOTE: The 'client_id' and 'response_type' are required arguments,
    and the 'redirect_uri' is required, if it was speicified when the
    client registered with the server. Also, to use this workflow the
    'response_type' MUST be 'code'.

    """

    data = {
        'client_id': HS_ID,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI
        }

    return session.get(HS_AUTHORIZE_URL, data=data)


if __name__ == '__main__':
    my_url = HS_BASE_URL + '/api/v1/people/me'
    username = raw_input('HS Username: ').strip()
    password = getpass.getpass('HS Password: ')
    access_token, _ = get_access_token(username=username, password=password)
    print(request(access_token, my_url))

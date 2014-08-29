#!/usr/bin/env python
from __future__ import absolute_import, print_function

import getpass

import requests
from requests.auth import HTTPBasicAuth

from hs_oauth import get_access_token, get_batches, get_people_in_a_batch


def follow_user(username, auth):
    url = 'https://api.github.com/user/following/%s' % username
    response = requests.put(url, auth=HTTPBasicAuth(*auth))
    if not response.ok:
        print('Failed to follow %s' % username)
    else:
        print('You are now following %s' % username)


def main():
    # Authenticate with HS.
    hs_username = raw_input('HS Email: ')
    hs_password = getpass.getpass('HS Password: ')

    gh_username = raw_input('GH Email: ')
    gh_password = getpass.getpass('GH Password: ')

    print('Authenticating as %s' % hs_username)
    access_token, _ = get_access_token(username=hs_username, password=hs_password)
    batches = get_batches(access_token)[::-1]

    for batch in batches:
        print('%s - %s' % (batch['id'], batch['name']))

    selected_id = raw_input('Enter batch id, for the batch you wish to follow: ').strip()
    batch = [b for b in batches if str(b['id']) == selected_id]

    if len(batch) == 1:
        for hacker in get_people_in_a_batch(batch[0]['id'], access_token):
            gh_name = hacker['github']
            if gh_name is not None:
                follow_user(gh_name, (gh_username, gh_password))


    else:
        print('Invalid batch selected.')


if __name__ == '__main__':
    main()

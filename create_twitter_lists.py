#!/usr/bin/env python
from __future__ import absolute_import, print_function

import getpass
from os.path import abspath, dirname, join, exists
import re

from hs_oauth import get_access_token, get_batches, get_people_in_a_batch

from twitter import Twitter, OAuth, read_token_file, oauth_dance
from twitter.cmdline import CONSUMER_KEY, CONSUMER_SECRET


# Create new twitter list.  Make sure it is private.
def get_twitter_instance():
    oauth_filename = '.twitter_oauth'
    oauth_path = join(dirname(abspath(__file__)), oauth_filename)

    if not exists(oauth_path):
        oauth_dance(
            "the Command-Line Tool", CONSUMER_KEY, CONSUMER_SECRET, oauth_filename
        )

    oauth_token, oauth_token_secret = read_token_file(oauth_path)

    twitter = Twitter(
        auth=OAuth(
            oauth_token, oauth_token_secret, CONSUMER_KEY, CONSUMER_SECRET
        ),
        secure=True,
        api_version='1.1',
        domain='api.twitter.com'
    )

    return twitter

# Add all members to it.
def create_list(name, members=None, description='', mode='private'):
    # Just making sure nothing bad happens with anybody's info!
    if mode != 'private':
        raise ValueError('We only support private lists.')

    twitter = get_twitter_instance()

    all_my_lists = twitter.lists.list()

    for twitter_list in all_my_lists:
        if twitter_list['member_count'] == 0:
            slug = twitter_list['slug']
            ownder_screen_name = twitter_list['user']['screen_name']
            twitter.lists.destroy(
                slug=slug, owner_screen_name=ownder_screen_name
            )
        elif twitter_list['name'] == name:
            break

    else:
        twitter_list = twitter.lists.create(
            name=name, mode=mode, description=description
        )
        print('Created list: %s' % twitter_list['name'])

    if members is not None:
        list_id = twitter_list['id_str']
        slug = twitter_list['slug']
        owner_screen_name = twitter_list['user']['screen_name']
        name_lists = [
            ','.join(members[i*100:(i+1)*100]) for i in range(len(members)/100 + 1)
        ]

        for name_list in name_lists:
            print('Given list of %s members to add' % len(members))
            valid_users = twitter.users.lookup(screen_name=name_list)
            print('%s members are valid ... ' % len(valid_users))
            name_list = ','.join([user['screen_name'] for user in valid_users])
            tl = twitter.lists.members.create_all(
                list_id=list_id,
                owner_screen_name=owner_screen_name,
                slug=slug,
                screen_name=name_list
            )
            print('Added %s members to %s' % (
                tl['member_count'] - twitter_list['member_count'], name)
            )


def sanitize_name(name):
    """ Sanitize a name to something that twitter allows. """

    sanitized_name = '-'.join(
        filter(None, re.sub("[^a-z0-9_-]+", '-', name.lower()).split('-'))
    )

    return sanitized_name[:25]


def main():
    # Authenticate with HS.
    hs_username = raw_input('HS Username: ')
    hs_password = getpass.getpass('HS Password: ')
    print('Authenticating as %s' % hs_username)

    # FIXME: The HS auth client API sucks.  Make it a class, if you want to
    # clean it up.  Yeah, we use the refresh token, and stuff if the access
    # token expires, etc.
    access_token, _ = get_access_token(username=hs_username, password=hs_password)

    batches = get_batches(access_token)[::-1]
    for batch in batches:
        description = batch['name']
        name = sanitize_name(description)
        members = [
            hacker['twitter']

            for hacker in get_people_in_a_batch(batch['id'], access_token)

            if 'twitter' in hacker and hacker['twitter']
        ]

        create_list(name=name, members=members, description=description)

if __name__ == '__main__':
    main()

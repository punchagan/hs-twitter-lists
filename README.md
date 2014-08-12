A script to create private lists of Hacker Schoolers or twitter, batch-wise.

# Setup

The script uses OAuth2.0 to authenticate with HackerSchool and Twitter.

You need to have an OAuth application registered under your HackerSchool
account. Create a new OAuth account on your HS settings page, with the
`REDIRECT_URL` set to `urn:ietf:wg:oauth:2.0:oob`.

Set the values of `HS_ID` and `HS_SECRET` (in `hs_oauth.py`) to the ID and
SECRET of this app.

# Usage

Run

    python create_lists.py

# Notes

The twitter API doesn't seem to work as well as some of the other ones I have
used.  The rate limits are quite crazy too.  So, you'll need a bag of patience
along with these scripts, to get what you want!
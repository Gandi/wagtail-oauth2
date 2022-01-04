Configure OAuth2.0
------------------

`wagtail-oauth2` requires a few settings to works.

They are all prefixed by `OAUTH2_`:

.. |br| raw:: html

  <div style="line-height: 0; padding: 0; margin: 0"></div>


+---------------------------+---------------------------+---------------------+-----------+
| name                      | description               | mandatory           | type      |
+===========================+===========================+=====================+===========+
| OAUTH2_CLIENT_ID          | OAuth2.0 client id        | yes                 | str       |
+---------------------------+---------------------------+---------------------+-----------+
| OAUTH2_CLIENT_SECRET      | OAuth2.0 client secret    | yes                 | str       |
+---------------------------+---------------------------+---------------------+-----------+
| OAUTH2_AUTH_URL           | /authorize endpoint       | yes                 | str       |
+---------------------------+---------------------------+---------------------+-----------+
| OAUTH2_TOKEN_URL          | /token url                | yes                 | str       |
+---------------------------+---------------------------+---------------------+-----------+
| OAUTH2_LOAD_USERINFO      | Load user info |br|       | yes                 | callable  |
|                           | from the oauth2 server    |                     |           |
+---------------------------+---------------------------+---------------------+-----------+
| OAUTH2_LOGOUT_URL         | url to redirect on logout | yes                 | str       |
+---------------------------+---------------------------+---------------------+-----------+
| OAUTH2_TIMEOUT            | HTTP Timeout in seconds   | no (30)             | int       |
+---------------------------+---------------------------+---------------------+-----------+
| OAUTH2_VERIFY_CERTIFICATE | Check TLS while |br|      | no (True)           | bool      |
|                           | consuming tokens          |                     |           |
+---------------------------+---------------------------+---------------------+-----------+
| OAUTH2_STORE_TOKENS       | Save the tokens |br|      | no (False)          | bool      |
|                           | in the django session     |                     |           |
+---------------------------+---------------------------+---------------------+-----------+
| OAUTH2_SESSION_KEY_PREFIX | Prefix of the key in |br| | no                  |           |
|                           | the django session.       | (`wagtail_oauth2_`) | str       |
+---------------------------+---------------------------+---------------------+-----------+
| OAUTH2_DEFAULT_TTL        | Fallback value if |br|    | no (900)            | int       |
|                           | ``expires_in`` is         |                     |           |
|                           | missing                   |                     |           |
+---------------------------+---------------------------+---------------------+-----------+


The settings `OAUTH2_LOAD_USERINFO` is a function that takes an `access_token` in parameter,
and builds a python dict or raises a `PermissionDenied` error.

Basically, this method is about fetching some information on the user loaded using
OAuth2.0 API and deciding to grant the user to log in, and to get the role of 
that user.

The userinfo dict contains the following keys:

+--------------+-------------------------------------+--------------------------------+-----------+
| key          | description                         | mandatory (default)            | type      |
+==============+=====================================+================================+===========+
| username     | user identifier                     | yes                            | str       |
+--------------+-------------------------------------+--------------------------------+-----------+
| is_superuser | makes the user an admin on creation | yes                            | bool      |
+--------------+-------------------------------------+--------------------------------+-----------+
| email        | email address (recommanded)         | no                             | str       |
+--------------+-------------------------------------+--------------------------------+-----------+
| first_name   | first name of the user              | no                             | str       |
+--------------+-------------------------------------+--------------------------------+-----------+
| last_name    | last name of the user               | no                             | str       |
+--------------+-------------------------------------+--------------------------------+-----------+
| is_staff     | grant access to the wagtail admin   | no (True)                      | bool      |
+--------------+-------------------------------------+--------------------------------+-----------+
| groups       | subscribe non superuser to groups   | no (["Moderators", "Editors"]) | List[str] |
+--------------+-------------------------------------+--------------------------------+-----------+


Exemple of settings
~~~~~~~~~~~~~~~~~~~

::


   USERS = {
      "mey_accesstoken": {
         "username": "mei",
         "is_superuser": True,
      }
   }


   def load_userinfo(access_token):
      try:
         # Real code consume an api with a header 
         # f"Authorization: Bearer {access_token}"
         return USERS[access_token]
      except KeyError:
         raise PermissionDenied


   OAUTH2_LOAD_USERINFO = load_userinfo

   OAUTH2_CLIENT_ID = "Mei"
   OAUTH2_CLIENT_SECRET = "T0t0r0"

   OAUTH2_AUTH_URL = "https://gandi.v5/authorize"
   OAUTH2_TOKEN_URL = "https://gandi.v5/token"
   OAUTH2_LOGOUT_URL = "https://gandi.v5/logout"

   OAUTH2_VERIFY_CERTIFICATE = True
   OAUTH2_TIMEOUT = 30


Consideration before activating OAUTH2_STORE_TOKENS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In OAuth2.0, tokens are for the app, not the user, so the session
must be secure to avoid security issues.

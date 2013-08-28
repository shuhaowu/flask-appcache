flask-appcache
==============

I've spent enough time tracking down appcache issues now.. Let's do this the
right way.

Quick Example
-------------

This is really easy to use. If not, file an issue! Here's an overview:

Suppose if we start with a standard flask app with the following directory
structures.

    server.py
    templates/
      - manifest.appcache
    static
      - app.js
      - app.css
      - img.png

Here's server.py:

    from flask import Flask
    from flask.ext.appcache import Appcache

    app = Flask(__name__)

    # initializes the appcache
    # you can also use the standard init_app function instead of initializing
    # class with the app
    appcache = Appcache(app)

    # adds some urls to cache.
    appcache.add_urls("/", "/offline")
    appcache.add_folder("static", base="/static") 

    @app.route("/")
    def main():
      return "Yay I'm cached!"

    @app.route("/offline")
    def offline():
      return "awe i'm offline"

Here's an example manifest.appcache file (actually this is probably good for
most purposes):

    CACHE MANIFEST
    # version {{ hash }} 
    # updated {{ updated }}

    CACHE:
    {% for url in urls %}{{ url }}
    {% endfor %}

    FALLBACK:
    / /offline

    NETWORK:
    *

Flask-Appcache registers a route for you, /manifest.appcache, to render and
serve the template as specified above. Here's an example rendered version of
this file:

    CACHE MANIFEST
    # version ab1a2034bc23a734015d18c06c4d29f2264d7a8e
    # updated 2013-08-28T15:16:34.663515

    CACHE:
    /
    /offline
    /static/app.js
    /static/app.css
    /static/img.png

    FALLBACK:
    / /offline

    NETWORK:
    *

The hash will change if you change any of the files (including the rendered
views like / and /offline). updated will be as well allowing the app to be
updated on the client side.

More advanced features
----------------------

You can exclude URLs from being tracked even if you tell the system to add it
(an example use case would be blacklisting some urls from a folder when you
add a folder). Exclusion URLs are using a prefix scheme. So if there are any
urls that has the prefix of an excluded url, it will be excluded. To use this
feature:

    # This will ignore /static/js/ignored/1.js, /static/js/ignored/2.js and
    # so on. Pretty much anything that starts with /static/js/ignored
    appcache.add_excluded_urls("/static/js/ignored")

You can add folders but specify a different base url. An example usecase would
be if you changed the static folder:

    # This will remap any files under static to have a /media prefix.
    # static/js/1.js => /media/js/1.js
    # static/css/app.css => /media/css/app.css
    appcache.add_folder("static", base="/media")

You can change the url where manifest.appcache is served by specifying a config
before you initialize the appcache.

    # defaults to /manifest.appcache
    app.config["APPCACHE_URL"] = "/my_manifest.appcache"
    appcache = Appcache(app)
    ....

You can also change the template name:

    # make sure that you have the file
    app.config["APPCACHE_TEMPLATE"] = "my_manifest.appcache"
    appcache = Appcache(app)

Some notes here and there
-------------------------

Flask-Appcache registers an `after_request` handler that changes all cache
control to `must-revalidate`. This might not be the ideal behaviour so it could
be changed that that head is only emitted for the manifest.appcache route and
any url routes tracked by appcache.

In order to compute the hash of the current site, Flask-Appcache makes a fake
request to your server to retrieve the content of an appcache'd URL. This makes
it play well with any view. Note, this view should not change often as it will
screw up appcache updates.

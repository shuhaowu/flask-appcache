import hashlib

try:
  import unittest2 as unittest
except ImportError:
  import unittest

from flask import Flask
from flask.ext.appcache import Appcache


class AppcacheTest(unittest.TestCase):

  def test_init_app(self):
    app = Flask(__name__)
    Appcache(app)

    self.assertEquals("manifest.appcache", app.config["APPCACHE_TEMPLATE"])
    self.assertEquals("/manifest.appcache", app.config["APPCACHE_URL"])
    self.assertEquals("http://localhost", app.config["APPCACHE_URL_BASE"])
    self.assertEquals([], app.config["CACHED_URLS"])
    self.assertEquals([], app.config["EXCLUDED_URLS"])

    app = Flask(__name__)
    appcache = Appcache()
    appcache.init_app(app)

    self.assertEquals("manifest.appcache", app.config["APPCACHE_TEMPLATE"])
    self.assertEquals("/manifest.appcache", app.config["APPCACHE_URL"])
    self.assertEquals("http://localhost", app.config["APPCACHE_URL_BASE"])
    self.assertEquals([], app.config["CACHED_URLS"])
    self.assertEquals([], app.config["EXCLUDED_URLS"])

    app = Flask(__name__)
    app.config["APPCACHE_URL"] = "/yay/manifest.appcache"
    Appcache(app)

    self.assertEquals("/yay/manifest.appcache", app.config["APPCACHE_URL"])

  def test_route_registered(self):
    app = Flask(__name__)
    Appcache(app)

    found = False
    for rule in app.url_map.iter_rules():
      if app.config["APPCACHE_URL"] == rule.rule:
        found = True

    self.assertTrue(found)

    app = Flask(__name__)
    app.config["APPCACHE_URL"] = "/yay/manifest.appcache"
    Appcache(app)

    for rule in app.url_map.iter_rules():
      if app.config["APPCACHE_URL"] == rule.rule:
        found = True

    self.assertTrue(found)

  def test_add_cached_urls(self):
    app = Flask(__name__)
    appcache = Appcache(app)

    appcache.add_urls("/")
    self.assertTrue("/" in appcache.urls())

  def test_add_folders(self):
    app = Flask(__name__)
    appcache = Appcache(app)

    appcache.add_folder("static", base="/static")

    urls = appcache.urls()
    self.assertEquals(2, len(urls))
    self.assertTrue("/static/static1.js" in urls)
    self.assertTrue("/static/static2.css" in urls)

    app = Flask(__name__)
    appcache = Appcache(app)

    appcache.add_folder("static", base="/media")

    urls = appcache.urls()
    self.assertEquals(2, len(urls))
    self.assertTrue("/media/static1.js" in urls)
    self.assertTrue("/media/static2.css" in urls)

  def test_all_together(self):
    app = Flask(__name__)
    appcache = Appcache(app)

    appcache.add_folder("static")
    appcache.add_urls("/")
    appcache.add_urls("/test")

    @app.route("/")
    def main():
        return "yay"

    @app.route("/test")
    def test():
        return "yay!!"

    urls = appcache.urls()
    self.assertEquals(4, len(urls))
    self.assertTrue("/" in urls)
    self.assertTrue("/test" in urls)
    self.assertTrue("/static/static1.js" in urls)
    self.assertTrue("/static/static2.css" in urls)

    # so there is a hash..
    hash, updated = appcache.hash()
    self.assertTrue(hash)
    self.assertTrue(updated)

  def test_correct_hash(self):
    app = Flask(__name__)
    appcache = Appcache(app)

    appcache.add_urls("/")

    mode = 1

    @app.route("/")
    def main():
      if mode == 1:
        return "yay"
      else:
        return "yay1"

    hash, updated = appcache.hash()
    self.assertEquals(hashlib.sha1("yay").hexdigest(), hash)

    h, updated_again = appcache.hash()
    self.assertEquals(updated, updated_again)

    mode = 2
    h, updated_again = appcache.hash()
    self.assertEquals(hashlib.sha1("yay1").hexdigest(), h)
    self.assertNotEquals(updated, updated_again)

  def test_route(self):
    app = Flask(__name__)
    appcache = Appcache(app)
    appcache.add_urls("/static/static1.js")

    client = app.test_client()

    response = client.get("/manifest.appcache", follow_redirects=True)
    self.assertEquals(200, response.status_code)
    data = response.data.split("\n")
    self.assertEquals(4, len(data))
    self.assertEquals(hashlib.sha1("Test").hexdigest(), data[1])
    self.assertEquals("/static/static1.js", data[2])

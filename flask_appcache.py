from datetime import datetime
import hashlib
import os

from flask import make_response, render_template


class Appcache(object):
  def __init__(self, app=None):
    self.app = app
    self._get_contents = []
    self._urls = set()
    self._excluded_urls = set()
    self._lasthash = None
    self._lastupdated = None

    if app is not None:
      self.init_app(app)

  def init_app(self, app):
    if self.app is None:
      self.app = app
    app.config.setdefault("APPCACHE_TEMPLATE", "manifest.appcache")
    app.config.setdefault("APPCACHE_URL", "/manifest.appcache")
    app.config.setdefault("APPCACHE_URL_BASE", "http://localhost")

    def after_request(resp):
      resp.cache_control.must_revalidate = True
      return resp

    @app.route(app.config["APPCACHE_URL"])
    def manifest_appcache():
      hash, updated = self.hash()
      response = make_response(
        render_template(app.config["APPCACHE_TEMPLATE"],
                        urls=self.urls(),
                        hash=hash,
                        updated=updated)
      )

      response.mimetype = 'text/cache-manifest'
      return response

  def urls(self):
    return self._urls

  def hash(self):
    file_hashes = hashlib.sha1()
    for f in self._get_contents:
      content = f()
      file_hashes.update(content)

    h = file_hashes.hexdigest()
    if h != self._lasthash:
      self._lasthash = h
      self._lastupdated = datetime.now().isoformat()

    return self._lasthash, self._lastupdated

  def add_excluded_urls(self, *urls):
    for url in urls:
      self._excluded_urls.add(url)

  def add_folder(self, folder, base="/static"):
    l = len(folder)
    for root, subdir, fname in os.walk(folder):
      # we want the path that's inside the folder.
      # TODO: investigate unicode issues
      for filename in fname:
        path = os.path.join(root, filename)[l:].lstrip("/")
        path = base + "/" + path
        self.add_urls(path)

  def add_urls(self, *urls):
    for url in urls:
      skip = False
      for u in self._excluded_urls:
        if url.startswith(u):
          skip = True
          break

      if skip:
        continue

      if url == self.app.config["APPCACHE_URL"]:
        raise ValueError("You should never put your appcache url into the "
                         "appcache")

      def get_content():
        client = self.app.test_client()
        base_url = self.app.config["APPCACHE_URL_BASE"]

        response = client.get(url, follow_redirects=True, base_url=base_url)

        if response.status_code != 200:
          raise ValueError("Appcache is broken: {} is not 200".format(url))

        return response.data

      self._get_contents.append(get_content)
      self._urls.add(url)

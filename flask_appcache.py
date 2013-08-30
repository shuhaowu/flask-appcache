from datetime import datetime
import hashlib
import os

from flask import make_response, render_template


class Appcache(object):
  def __init__(self, app=None):
    """Initializes a new instance of Appcache"""
    self.app = app
    self.urls = set()
    self._get_contents = []
    self._excluded_urls = set()
    self._lasthash = None
    self._lastupdated = None
    self._finalized = False

    if app is not None:
      self.init_app(app)

  def init_app(self, app):
    """Initializes the app.

    Warning: set all the config variables before this so the correct route will
    be registered.
    """

    if self.app is None:
      self.app = app
    app.config.setdefault("APPCACHE_TEMPLATE", "manifest.appcache")
    app.config.setdefault("APPCACHE_URL", "/manifest.appcache")
    app.config.setdefault("APPCACHE_URL_BASE", "http://localhost")

    @app.after_request
    def after_request(resp):
      if app.debug:
        resp.cache_control.no_cache = True
      else:
        resp.cache_control.must_revalidate = True

      resp.headers.remove("Expires")

      return resp

    @app.route(app.config["APPCACHE_URL"])
    def manifest_appcache():
      hash, updated = self.hash()
      response = make_response(
        render_template(app.config["APPCACHE_TEMPLATE"],
                        urls=self.urls,
                        hash=hash,
                        updated=updated)
      )

      response.mimetype = 'text/cache-manifest'
      return response

  def hash(self):
    """Computes the hash and the last updated time for the current appcache

    Returns:
      hash, time updated in isoformat
    """
    if not self._finalized:
      file_hashes = hashlib.sha1()
      for f in self._get_contents:
        content = f()
        file_hashes.update(content)

      h = file_hashes.hexdigest()
      if h != self._lasthash:
        self._lasthash = h
        self._lastupdated = datetime.now().isoformat()

    return self._lasthash, self._lastupdated

  def finalize(self):
    """Finalizes the appcache by precomputing the hash.

    This will cause the hash() function to never compute the hash again."""

    # to compute the hash
    self.hash()
    self._finalized = True

  def _check_finalized(self):
    if self._finalized:
      raise RuntimeError("Appcache has already been finalized.")

  def add_excluded_urls(self, *urls):
    """Adds urls to exclude from appcache.

    Args:
      urls: the urls to cache
    """
    self._check_finalized()

    for url in urls:
      self._excluded_urls.add(url)

  def add_folder(self, folder, base="/static"):
    """Adds a whole folder to appcache.

    Args:
      folder: the folder's content to cache.
      base: The base url.

      As an example, if you have media/ being your static dir and that is
      mapped to the server url of /static, you would do
      add_folder('media', base='/static')
    """
    l = len(folder)
    for root, subdir, fname in os.walk(folder):
      # we want the path that's inside the folder.
      # TODO: investigate unicode issues
      for filename in fname:
        path = os.path.join(root, filename)[l:].lstrip("/")
        path = base + "/" + path
        self.add_urls(path)

  def add_urls(self, *urls):
    """Adds individual urls on appcache.

    Args:
      urls: The urls to be appcached.
    """
    self._check_finalized()

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
      self.urls.add(url)

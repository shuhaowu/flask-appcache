"""
Flask-Appcache
--------------

Semi-automagically setups up appcache for you.
"""

from setuptools import setup


setup(
  name='Flask-Appcache',
  version='0.1.2',
  url='https://github.com/shuhaowu/flask-appcache/',
  license='MPLv2',
  author='Shuhao Wu',
  author_email='shuhao@shuhaowu.com',
  description='Semi-automagically sets up appcache for you',
  long_description=__doc__,
  py_modules=['flask_appcache'],
  zip_safe=False,
  include_package_data=True,
  test_suite="appcache_test",
  platforms='any',
  install_requires=[
    'Flask'
  ],
  classifiers=[
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Software Development :: Libraries :: Python Modules'
  ]
)

import sae
import pylibmc
import sys
from hello import app
sys.modules['memcache'] = pylibmc
application=sae.create_wsgi_app(app)
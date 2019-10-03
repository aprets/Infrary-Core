# noinspection PyPackageRequirements
from google.appengine.ext import vendor
import os
import sys

# Add any libraries installed in the "lib" folder.
vendor.add('lib')

# Hacks to fix windows sandbox follow... [Thanks pallets/click]

on_appengine = os.environ.get('SERVER_SOFTWARE', '').startswith('Development')

if on_appengine and os.name == 'nt':
    sys.platform = 'Not Windows'

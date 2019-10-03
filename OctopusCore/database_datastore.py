# noinspection PyPackageRequirements
from google.appengine.ext import ndb


class Server(ndb.Expando):
    ip = ndb.StringProperty()
    access_token = ndb.TextProperty()
    status = ndb.StringProperty()
    ssh_fgpt = ndb.TextProperty()
    vm_config = ndb.TextProperty()
    is_master = ndb.BooleanProperty()
    is_self_destruct = ndb.BooleanProperty()
    log = ndb.TextProperty()
    metadata = ndb.JsonProperty(repeated=True)


class User(ndb.Model):
    is_active = ndb.BooleanProperty()
    hash = ndb.TextProperty()
    email_key = ndb.StringProperty()
    first_name = ndb.TextProperty()
    last_name = ndb.TextProperty()
    servers = ndb.JsonProperty(repeated=True)
    created_at = ndb.DateTimeProperty()
    master_conf = ndb.JsonProperty()
    compose = ndb.TextProperty()
    compose_completed = ndb.BooleanProperty()
    messages = ndb.JsonProperty(repeated=True)

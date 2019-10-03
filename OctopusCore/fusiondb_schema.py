import fusiondb
from fusiondb.properties import *


class Server(fusiondb.Model):
    owner_email = StringProperty()
    provider = StringProperty()
    id = StringProperty()
    ip = StringProperty()
    access_token = StringProperty()
    status = StringProperty()
    ssh_fgpt = StringProperty()
    vm_config = StringProperty()
    is_master = BooleanProperty()
    is_self_destruct = BooleanProperty()
    log = StringProperty()
    metadata = ListProperty()


class User(fusiondb.Model):
    is_active = BooleanProperty()
    hash = StringProperty()
    email = StringProperty()
    email_key = StringProperty()
    first_name = StringProperty()
    last_name = StringProperty()
    servers = ListProperty()
    created_at = DateTimeProperty()
    master_conf = DictProperty()
    compose = StringProperty()
    compose_completed = BooleanProperty()
    messages = ListProperty()

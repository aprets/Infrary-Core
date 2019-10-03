import os
import sys

IS_DEBUG = True

PROVISIONER_CONTAINER_NAME = 'eu.gcr.io/infrary-main/provisioner'
PROVISIONER_OCTO_CONF_KEY = 'octo_conf'
PROVISIONER_PROPERTIES_KEY = 'properties'
PROVISIONER_ACTION_KEY = 'action'
PROVISIONER_CREATE_ACTION = 'create'
PROVISIONER_DESTROY_ACTION = 'destroy'
PROVISIONER_ACCESS_TOKEN_KEY = 'token'
PROVISIONER_PROVIDER_KEY = 'provider'
PROVISIONER_SERVER_ID_KEY = 'server_id'
PROVISIONER_SSH_KEY_KEY = 'ssh_key'
PROVISIONER_SERVER_LOCATION_KEY = 'location'
PROVISIONER_SERVER_IMAGE_KEY = 'image'
PROVISIONER_SERVER_SIZE_KEY = 'size'
PROVISIONER_SERVER_NAME_KEY = 'name'

DIGITAL_OCEAN_PROVIDER_CODE = "DO"

FAILED_DELETE_PROVIDER_STATUS = 'delete_fail_provider'
FAILED_DELETE_STATUS = 'delete_fail'
DELETED_STATUS = 'deleted'
DOWN_STATUS = "down"
UP_STATUS = "up"
CONFIGURING_STATUS = "configuring"
CREATED_STATUS = "created"
ALL_STATUS_LIST = [FAILED_DELETE_PROVIDER_STATUS, FAILED_DELETE_STATUS, DELETED_STATUS, DOWN_STATUS, UP_STATUS,
                   CONFIGURING_STATUS, CREATED_STATUS]
CANNOT_DELETE_STATUS_LIST = [CREATED_STATUS, CONFIGURING_STATUS]

VMCONF_CONTAINER_NAME = 'eu.gcr.io/infrary-main/vmconf'
VMCONF_OCTO_CONF_KEY = 'octo_conf'
VMCONF_PRIVATE_KEY_KEY = 'private_key'
VMCONF_VMCONF_KEY = 'vm_conf'
VMCONF_SERVER_ID_KEY = "server_id"
VMCONF_SERVER_PROVIDER_KEY = "server_provider"
VMCONF_OCTO_TOKEN_KEY = "octo_token"
VMCONF_SERVER_HOSTNAME_KEY = "server_hostname"
VMCONF_COMMAND_LIST_KEY = "cmd_list"
VMCONF_IS_MASTER_KEY = "is_master"
VMCONF_SELF_DESTRUCT_KEY = "self_destruct"
VMCONF_MASTERCONF_KEY = "master_conf"
VMCONF_COMPOSE_STACKS_KEY = "compose_stacks"

MASTERCONF_SECRET_KEY = 'secret'
MASTERCONF_PASSWORD_KEY = 'password'
MASTERCONF_USER_KEY = 'user'
MASTERCONF_HOST_KEY = 'host'

VM_CONFIGURATION_KEY = "configuration"
SERVER_PROPERTIES_KEY = "properties"
INFRARY_COMPOSE_KEY = 'infrary-compose'
ACTION_KEY = "action"
STATUS_KEY = "status"
FORCE_KEY = 'force'
EMAIL_KEY_KEY = "email_key"
PASSWORD_KEY = "password"
EMAIL_KEY = "email"
LAST_NAME_KEY = "last_name"
FIRST_NAME_KEY = "first_name"
TOKEN_KEY = "token"

SET_STATUS_ACTION = "set_status"

ACCESS_TOKEN_KEY = 'token'
STATUS_DB_KEY = "status"
MASTERCONF_KEY = 'master_conf'
SELF_DESTRUCT_KEY = 'self_destruct'
IS_MASTER_KEY = 'is_master'
VM_CONFIGURATION_DB_KEY = "vm_configuration"
ID_KEY = 'id'
PROVIDER_KEY = 'provider'
IP_KEY = 'ip'
TEMP_SSH_KEY_KEY = 'temp_ssh_key'
LOG_KEY = 'log'
SSH_KEY_FINGERPRINT_KEY = 'ssh_fgpt'

API_VERSION = "v0"
CONTAINER_HANDLER = 'none'
DB_TYPE = 'datastore'
MONGO_URI = 'mongodb://gentleseal:eQi2ZdxZLhf4bc5xJ@ds241065.mlab.com:41065/infrarydev'
MONGO_NAME = 'infrarydev'
# Warn user and exit as DB_TYPE != 'datastore' on GAE may cause unexpected behaviour in production
on_appengine = os.environ.get('SERVER_SOFTWARE', '').startswith('Development')
if on_appengine and DB_TYPE != 'datastore':
    sys.exit('You are running GAE Development Server, but DB_TYPE != \'datastore\'')

TOKEN_USER_ID_KEY = 'uid'
TOKEN_EXPIRY_KEY = 'exp'
# noinspection SpellCheckingInspection
SECRET_TOKEN_ENC_KEY = \
    '''-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEAtYYswqmJNVyHPAhcn+vQKtlV1NbmvhgrfLXUs1A+sw5HeEqI
oA/7OwpE7To52rb1QpVt/WvncrLWR+Nx6ow7jiepi8rLeF/ZYQBfKbjSFrHiOQnb
IZuOoipDzF/pFzI5wlhKtqD1IbjxKUBm5t7hBPPay8Yq7C4+nhHjd0OS0DDgucg7
D5ojXsXsviOpHjmnlWJOC+dozvoEcgSjwUsDPYADsvQualDx8ysCTkKOlkaMUGHn
5ZTMtU7ey8jSSTSSToMcn2rIfvGLsjoy30SM9M4oO5Va2RG5lpRNJilx2SGJfihw
FvfvYRSg3X3ALpNS7lOOLmUqZsG272mTo3/t+QIDAQABAoIBAD0vTqMGlhMAbyzS
/LWCvJXUz9N/5CKq7u2INHuETr330CtBpC+fc2UBHx5/A8Uu6hhZWcuTtV253fQ5
O8p9Hg3aXJGb911JoXHKuEjN3TJ9Hu1u3wfC8R7D9DpNEboZ2dIiBHzuX/HP7qmi
5YxoD5ylvVf2Ib2eEMki6nLmufOmFGPrnNNdRueLqRKU07G0igPkonQ/cpsOFdmH
r5lIOaE0c40+Qoi8B3+iWzpJAi/tLBlnqef1Z2ayTHRBHMX0q9uVxCr3joAih7jN
1m1ND4MuUqve0HSN0lWQIzfx+akqBV96qlk/KmpIP/mNjr2wpyCTgEHjqjjCZS3U
uCN3fQECgYEA5OGKsI12xbS6O/vuRVjt7KT0Sa0/okIUxhwwRgLt4jJ8p5Of+vdQ
E6fR84KViUcCvm9ChjAbo8OA6qTMKCvo1uUNy3mLvhgupQljbY6YPSUHxEhVxFXh
PacQZSciLf95iuNuYDLc77VerK1i1B1IwohZleV4xdn/lWAQOKWT3SkCgYEAywgy
CUHLiqqMjW7E7WUa0/1PI9u5eT8IasWTXLxZbud6/tW30nwJR3rFhTovdeWmirP/
eUMTOx1n13mNPIRT/E6fY0O6Q3IhNq1o/GVUnsyUDLq/IdeZocrRtJYuTRuxm26S
i7Vceu/wVgYuhvlm4MPc5SWf1bj/b/fcAnkp1FECgYAA+zqWATVGKb02rqDZ6USz
5A0sF7MTJgdixhIq6q5Mbvz71vUzpUXRn8GVsrSjbwuC94UogCJONHNkDirV7UJF
UZwaiD3iJcZlbMHhYWAjuvnqjIjZm6iolAPM+zr5SYQi5VC+1tj9qiBqyx+GW03J
j74al25KIuImqM/I/mTA6QKBgQCmqWqRaL4RbOCFdMkYaic0nznooIRGv/RD2T2X
IVF0lXXEXGFR2dmwIFqle1bcO5CTSSBMRUAzBXdpTHEgnStn8I4r6Lusg7I59O06
Sl/FHv/k1yLwP8/wHNI5oBIP38zSX1jScCSjEfTCWL62s2G83Wqle1YSFZMxMVAb
g6RPkQKBgDudtRzelfbNSTJMeJnzZVSd/6l8AhxNOcuy6j2B7HFcEFhVKfKMlnUn
ScmkMeo2MCS5ter3wlJjYz+GiDLK8ATQR/8EF4/VsMHl0l2M0hbd6ZKNINaIwMnA
o3IbAQMisWnZx29DqUtr2iuZKIgRPcAt7lGGrNUvtf+tNFnAsHe0
-----END RSA PRIVATE KEY-----'''
# noinspection SpellCheckingInspection
SECRET_TOKEN_DEC_KEY = \
    '''-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAtYYswqmJNVyHPAhcn+vQ
KtlV1NbmvhgrfLXUs1A+sw5HeEqIoA/7OwpE7To52rb1QpVt/WvncrLWR+Nx6ow7
jiepi8rLeF/ZYQBfKbjSFrHiOQnbIZuOoipDzF/pFzI5wlhKtqD1IbjxKUBm5t7h
BPPay8Yq7C4+nhHjd0OS0DDgucg7D5ojXsXsviOpHjmnlWJOC+dozvoEcgSjwUsD
PYADsvQualDx8ysCTkKOlkaMUGHn5ZTMtU7ey8jSSTSSToMcn2rIfvGLsjoy30SM
9M4oO5Va2RG5lpRNJilx2SGJfihwFvfvYRSg3X3ALpNS7lOOLmUqZsG272mTo3/t
+QIDAQAB
-----END PUBLIC KEY-----'''

DO_BASE_URL = "https://api.digitalocean.com/v2"

# OCTO "Constants" to tell microservices who to talk to (and how)
if IS_DEBUG:
    OCTO_URL = 'http://10.0.75.1:8080'
else:
    OCTO_URL = 'https://api.infrary.com'

if IS_DEBUG:
    CONTMAN_SUBMIT_URL = 'http://127.0.0.1:5555/'
else:
    CONTMAN_SUBMIT_URL = 'https://contman.infrary.com/'

OCTO_SERVER_SUBMIT_PATH = '/{}/servers/provision/configure'.format(API_VERSION)
OCTO_MESSAGE_SUBMIT_PATH = '/{}/user/messages'.format(API_VERSION)
OCTO_SERVER_STATUS_SUBMIT_PATH = '/{}/servers/{{server_provider}}/{{server_id}}'.format(API_VERSION)
OCTO_SERVER_LOG_SUBMIT_PATH = '/{}/servers/{{server_provider}}/{{server_id}}/log'.format(API_VERSION)
OCTO_CONFIGURED_SERVER_SUBMIT_PATH = '/{}/servers/provision/initialise'.format(API_VERSION)

OCTO_TOKEN_KEY = 'OCTO_TOKEN'
OCTO_CONFIGURED_SERVER_SUBMIT_PATH_KEY = 'OCTO_CONFIGURED_SERVER_SUBMIT_PATH'
OCTO_SERVER_STATUS_SUBMIT_PATH_KEY = 'OCTO_SERVER_STATUS_SUBMIT_PATH'
OCTO_SERVER_LOG_SUBMIT_PATH_KEY = 'OCTO_SERVER_LOG_SUBMIT_PATH'
OCTO_MESSAGE_SUBMIT_PATH_KEY = 'OCTO_MESSAGE_SUBMIT_PATH'
OCTO_SERVER_SUBMIT_PATH_KEY = 'OCTO_SERVER_SUBMIT_PATH'
OCTO_URL_KEY = 'OCTO_URL'

# noinspection SpellCheckingInspection
SENDGRID_API_KEY = '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'

FROM_EMAIL_NAME = "Infrary Bot"
FROM_EMAIL = "noreply@infrary.com"
if IS_DEBUG:
    EMAIL_VERIFY_LINK = "http://127.0.0.1:8081/auth/login?emailKey={}"
else:
    EMAIL_VERIFY_LINK = "https://infrary.com/auth/login?emailKey={}"
USER_CREATION_EMAIL_SUBJECT = "Verify your email"

DO_SUPPORTED_IMAGES = [
    {"id": 30875099, "name": "16.04.3 x64", "distribution": "Ubuntu", "slug": "ubuntu-16-04-x64", "public": True,
     "regions": ["nyc1", "sfo1", "nyc2", "ams2", "sgp1", "lon1", "nyc3", "ams3", "fra1", "tor1", "sfo2", "blr1"],
     "created_at": "2018-01-13T00:41:21Z", "min_disk_size": 20, "type": "snapshot", "size_gigabytes": 0.3},
    {"id": 30821337, "name": "14.04.5 x64", "distribution": "Ubuntu", "slug": "ubuntu-14-04-x64", "public": True,
     "regions": ["nyc1", "sfo1", "nyc2", "ams2", "sgp1", "lon1", "nyc3", "ams3", "fra1", "tor1", "sfo2", "blr1"],
     "created_at": "2018-01-11T00:13:37Z", "min_disk_size": 20, "type": "snapshot", "size_gigabytes": 0.27}
]

# Yes, this is a constant.
# > WHY????
# This will almost never change and can be packed with app updates.
# Disk reads can be expensive in ~The cloud~ and are pointless in this case (As this is not too big and is to be used
# quite often). Such code also reduces portability (due some platform native file reads etc.) and makes the app
# less stateless. Additionally, packing email with the app greatly simplifies running multiple app versions
# (eg for "production" or A/B testing) as it is not a file on a common cloud storage bucket.
# noinspection SpellCheckingInspection,PyPep8
USER_CREATION_EMAIL_HTML = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD XHTML 1.0 Transitional //EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><html xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office"><head><!--[if gte mso 9]><xml> <o:OfficeDocumentSettings> <o:AllowPNG/> <o:PixelsPerInch>96</o:PixelsPerInch> </o:OfficeDocumentSettings> </xml><![endif]--> <meta http-equiv="Content-Type" content="text/html; charset=utf-8"> <meta name="viewport" content="width=device-width"> <meta http-equiv="X-UA-Compatible" content="IE=edge"> <title>BF-simple-template</title> <style type="text/css" id="media-query"> body{margin: 0; padding: 0;}table, tr, td{vertical-align: top; border-collapse: collapse;}.ie-browser table, .mso-container table{table-layout: fixed;}*{line-height: inherit;}a[x-apple-data-detectors=true]{color: inherit !important; text-decoration: none !important;}[owa] .img-container div, [owa] .img-container button{display: block !important;}[owa] .fullwidth button{width: 100% !important;}[owa] .block-grid .col{display: table-cell; float: none !important; vertical-align: top;}.ie-browser .num12, .ie-browser .block-grid, [owa] .num12, [owa] .block-grid{width: 500px !important;}.ExternalClass, .ExternalClass p, .ExternalClass span, .ExternalClass font, .ExternalClass td, .ExternalClass div{line-height: 100%;}.ie-browser .mixed-two-up .num4, [owa] .mixed-two-up .num4{width: 164px !important;}.ie-browser .mixed-two-up .num8, [owa] .mixed-two-up .num8{width: 328px !important;}.ie-browser .block-grid.two-up .col, [owa] .block-grid.two-up .col{width: 250px !important;}.ie-browser .block-grid.three-up .col, [owa] .block-grid.three-up .col{width: 166px !important;}.ie-browser .block-grid.four-up .col, [owa] .block-grid.four-up .col{width: 125px !important;}.ie-browser .block-grid.five-up .col, [owa] .block-grid.five-up .col{width: 100px !important;}.ie-browser .block-grid.six-up .col, [owa] .block-grid.six-up .col{width: 83px !important;}.ie-browser .block-grid.seven-up .col, [owa] .block-grid.seven-up .col{width: 71px !important;}.ie-browser .block-grid.eight-up .col, [owa] .block-grid.eight-up .col{width: 62px !important;}.ie-browser .block-grid.nine-up .col, [owa] .block-grid.nine-up .col{width: 55px !important;}.ie-browser .block-grid.ten-up .col, [owa] .block-grid.ten-up .col{width: 50px !important;}.ie-browser .block-grid.eleven-up .col, [owa] .block-grid.eleven-up .col{width: 45px !important;}.ie-browser .block-grid.twelve-up .col, [owa] .block-grid.twelve-up .col{width: 41px !important;}@media only screen and (min-width: 520px){.block-grid{width: 500px !important;}.block-grid .col{vertical-align: top;}.block-grid .col.num12{width: 500px !important;}.block-grid.mixed-two-up .col.num4{width: 164px !important;}.block-grid.mixed-two-up .col.num8{width: 328px !important;}.block-grid.two-up .col{width: 250px !important;}.block-grid.three-up .col{width: 166px !important;}.block-grid.four-up .col{width: 125px !important;}.block-grid.five-up .col{width: 100px !important;}.block-grid.six-up .col{width: 83px !important;}.block-grid.seven-up .col{width: 71px !important;}.block-grid.eight-up .col{width: 62px !important;}.block-grid.nine-up .col{width: 55px !important;}.block-grid.ten-up .col{width: 50px !important;}.block-grid.eleven-up .col{width: 45px !important;}.block-grid.twelve-up .col{width: 41px !important;}}@media (max-width: 520px){.block-grid, .col{min-width: 320px !important; max-width: 100% !important; display: block !important;}.block-grid{width: calc(100% - 40px) !important;}.col{width: 100% !important;}.col > div{margin: 0 auto;}img.fullwidth, img.fullwidthOnMobile{max-width: 100% !important;}.no-stack .col{min-width: 0 !important; display: table-cell !important;}.no-stack.two-up .col{width: 50% !important;}.no-stack.mixed-two-up .col.num4{width: 33% !important;}.no-stack.mixed-two-up .col.num8{width: 66% !important;}.no-stack.three-up .col.num4{width: 33% !important;}.no-stack.four-up .col.num3{width: 25% !important;}}</style></head><body class="clean-body" style="margin: 0;padding: 0;-webkit-text-size-adjust: 100%;background-color: #FFFFFF"> <style type="text/css" id="media-query-bodytag"> @media (max-width: 520px){.block-grid{min-width: 320px!important; max-width: 100%!important; width: 100%!important; display: block!important;}.col{min-width: 320px!important; max-width: 100%!important; width: 100%!important; display: block!important;}.col > div{margin: 0 auto;}img.fullwidth{max-width: 100%!important;}img.fullwidthOnMobile{max-width: 100%!important;}.no-stack .col{min-width: 0!important;display: table-cell!important;}.no-stack.two-up .col{width: 50%!important;}.no-stack.mixed-two-up .col.num4{width: 33%!important;}.no-stack.mixed-two-up .col.num8{width: 66%!important;}.no-stack.three-up .col.num4{width: 33%!important}.no-stack.four-up .col.num3{width: 25%!important}}</style> <table class="nl-container" style="border-collapse: collapse;table-layout: fixed;border-spacing: 0;mso-table-lspace: 0pt;mso-table-rspace: 0pt;vertical-align: top;min-width: 320px;Margin: 0 auto;background-color: #FFFFFF;width: 100%" cellpadding="0" cellspacing="0"><tbody><tr style="vertical-align: top"><td style="word-break: break-word;border-collapse: collapse !important;vertical-align: top"> <div style="background-color:#2C2D37;"> <div style="Margin: 0 auto;min-width: 320px;max-width: 500px;overflow-wrap: break-word;word-wrap: break-word;word-break: break-word;background-color: transparent;" class="block-grid "> <div style="border-collapse: collapse;display: table;width: 100%;background-color:transparent;"> <div class="col num12" style="min-width: 320px;max-width: 500px;display: table-cell;vertical-align: top;"> <div style="background-color: transparent; width: 100% !important;"> <div style="border-top: 0px solid transparent; border-left: 0px solid transparent; border-bottom: 0px solid transparent; border-right: 0px solid transparent; padding-top:5px; padding-bottom:5px; padding-right: 0px; padding-left: 0px;"> <div align="center" class="img-container center fixedwidth" style="padding-right: 0px; padding-left: 0px;"> <a target="_blank"> <img class="center fixedwidth" align="center" border="0" src="https://i.imgur.com/ZG9Rtaj.png" alt="Image" title="Image" style="outline: none;text-decoration: none;-ms-interpolation-mode: bicubic;clear: both;display: block !important;border: none;height: auto;float: none;width: 100%;max-width: 225px" width="225"> </a></div></div></div></div></div></div></div><div style="background-color:#323341;"> <div style="Margin: 0 auto;min-width: 320px;max-width: 500px;overflow-wrap: break-word;word-wrap: break-word;word-break: break-word;background-color: transparent;" class="block-grid "> <div style="border-collapse: collapse;display: table;width: 100%;background-color:transparent;"> <div class="col num12" style="min-width: 320px;max-width: 500px;display: table-cell;vertical-align: top;"> <div style="background-color: transparent; width: 100% !important;"> <div style="border-top: 0px solid transparent; border-left: 0px solid transparent; border-bottom: 0px solid transparent; border-right: 0px solid transparent; padding-top:0px; padding-bottom:0px; padding-right: 0px; padding-left: 0px;"> <table border="0" cellpadding="0" cellspacing="0" width="100%" class="divider" style="border-collapse: collapse;table-layout: fixed;border-spacing: 0;mso-table-lspace: 0pt;mso-table-rspace: 0pt;vertical-align: top;min-width: 100%;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%"> <tbody> <tr style="vertical-align: top"> <td class="divider_inner" style="word-break: break-word;border-collapse: collapse !important;vertical-align: top;padding-right: 10px;padding-left: 10px;padding-top: 10px;padding-bottom: 10px;min-width: 100%;mso-line-height-rule: exactly;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%"> <table class="divider_content" align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="border-collapse: collapse;table-layout: fixed;border-spacing: 0;mso-table-lspace: 0pt;mso-table-rspace: 0pt;vertical-align: top;border-top: 10px solid transparent;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%"> <tbody> <tr style="vertical-align: top"> <td style="word-break: break-word;border-collapse: collapse !important;vertical-align: top;mso-line-height-rule: exactly;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%"> <span></span> </td></tr></tbody> </table> </td></tr></tbody></table> <div style="font-family:Arial, \'Helvetica Neue\', Helvetica, sans-serif;line-height:120%;color:#ffffff; padding-right: 0px; padding-left: 0px; padding-top: 30px; padding-bottom: 30px;"><div style="line-height:14px;font-size:12px;color:#ffffff;font-family:Arial, \'Helvetica Neue\', Helvetica, sans-serif;text-align:left;"><p style="margin: 0;font-size: 14px;line-height: 17px;text-align: center"><strong><span style="font-size: 28px; line-height: 33px;">Welcome to Infrary!</span></strong></p><p style="margin: 0;font-size: 14px;line-height: 17px;text-align: center">&#160;<br></p><p style="margin: 0;font-size: 14px;line-height: 17px;text-align: center">&#160;<br></p><p style="margin: 0;font-size: 14px;line-height: 17px;text-align: center">&#160;<span style="font-size: 24px; line-height: 28px;">Your verification code is:</span><br></p><p style="margin: 0;line-height: 14px;text-align: center;font-size: 12px"><span style="font-size: 24px; line-height: 28px;">**key**</span></p></div></div><div align="center" class="button-container center" style="padding-right: 10px; padding-left: 10px; padding-top:15px; padding-bottom:10px;"> <a href="**url**" target="_blank" style="display: block;text-decoration: none;-webkit-text-size-adjust: none;text-align: center;color: #ffffff; background-color: #C7702E; border-radius: 25px; -webkit-border-radius: 25px; -moz-border-radius: 25px; max-width: 116px; width: 76px;width: auto; border: 0px solid transparent;padding-top: 5px; padding-right: 20px; padding-bottom: 5px; padding-left: 20px; font-family: Arial, \'Helvetica Neue\', Helvetica, sans-serif;mso-border-alt: none"> <span style="font-size:16px;line-height:32px;"><span style="font-size: 14px; line-height: 28px;" data-mce-style="font-size: 14px;">Verify</span></span> </a> </div><table border="0" cellpadding="0" cellspacing="0" width="100%" class="divider" style="border-collapse: collapse;table-layout: fixed;border-spacing: 0;mso-table-lspace: 0pt;mso-table-rspace: 0pt;vertical-align: top;min-width: 100%;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%"> <tbody> <tr style="vertical-align: top"> <td class="divider_inner" style="word-break: break-word;border-collapse: collapse !important;vertical-align: top;padding-right: 10px;padding-left: 10px;padding-top: 10px;padding-bottom: 10px;min-width: 100%;mso-line-height-rule: exactly;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%"> <table class="divider_content" align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="border-collapse: collapse;table-layout: fixed;border-spacing: 0;mso-table-lspace: 0pt;mso-table-rspace: 0pt;vertical-align: top;border-top: 10px solid transparent;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%"> <tbody> <tr style="vertical-align: top"> <td style="word-break: break-word;border-collapse: collapse !important;vertical-align: top;mso-line-height-rule: exactly;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%"> <span></span> </td></tr></tbody> </table> </td></tr></tbody></table> <div align="center" class="img-container center autowidth " style="padding-right: 0px; padding-left: 0px;"> <img class="center autowidth " align="center" border="0" src="https://pro-bee-beepro-assets.s3.amazonaws.com/templates/default/common/bee_rocket.png" alt="Image" title="Image" style="outline: none;text-decoration: none;-ms-interpolation-mode: bicubic;clear: both;display: block !important;border: 0;height: auto;float: none;width: 100%;max-width: 402px" width="402"></div></div></div></div></div></div></div></td></tr></tbody> </table> </body></html>'

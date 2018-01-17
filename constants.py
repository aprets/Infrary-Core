IS_DEBUG = True

PROVISIONER_CONTAINER_NAME = 'provisioner'
PROVISIONER_CREATE_COMMAND = 'create'
PROVISIONER_DESTROY_COMMAND = 'destroy'
PROVISIONER_ACCESS_TOKEN_KEY = 'ACCESS_TOKEN'
PROVISIONER_PROVIDER_KEY = 'SERVER_PROVIDER'
PROVISIONER_SERVER_ID_KEY = 'SERVER_ID'
PROVISIONER_SSH_KEY_KEY = 'SSH_KEY'
PROVISIONER_SERVER_LOCATION_KEY = 'SERVER_LOCATION'
PROVISIONER_SERVER_IMAGE_KEY = 'SERVER_IMAGE'
PROVISIONER_SERVER_SIZE_KEY = 'SERVER_SIZE'
PROVISIONER_SERVER_NAME_KEY = 'SERVER_NAME'

DIGITAL_OCEAN_PROVIDER_CODE = "DO"

FAILED_DELETE_PROVIDER_STATUS = 'deleteFailProvider'
FAILED_DELETE_STATUS = 'deleteFail'
DELETED_STATUS = 'deleted'
DOWN_STATUS = "down"
UP_STATUS = "up"
CONFIGURING_STATUS = "configuring"
CREATED_STATUS = "created"
ALL_STATUS_LIST = [FAILED_DELETE_PROVIDER_STATUS, FAILED_DELETE_STATUS, DELETED_STATUS, DOWN_STATUS, UP_STATUS,
                   CONFIGURING_STATUS, CREATED_STATUS]
CANNOT_DELETE_STATUS_LIST = [CREATED_STATUS, CONFIGURING_STATUS]

VMCONF_CONTAINER_NAME = 'vmconf'
VMCONF_SERVER_ID_KEY = "serverID"
VMCONF_SERVER_PROVIDER_KEY = "serverProvider"
VMCONF_OCTO_TOKEN_KEY = "octoToken"
VMCONF_SERVER_HOSTNAME_KEY = "serverHostname"
VMCONF_COMMAND_LIST_KEY = "cmdList"
VMCONF_IS_MASTER_KEY = "isMaster"
VMCONF_SELF_DESTRUCT_KEY = "selfDestruct"

SERVERS_KEY = "servers"
CREATED_AT_KEY = "createdAt"
HASH_KEY = "hash"

MASTERCONF_SECRET_KEY = 'keySecret'
MASTERCONF_PASSWORD_KEY = 'pass'
MASTERCONF_USER_KEY = 'user'
MASTERCONF_HOST_KEY = 'host'

VM_CONFIGURATION_KEY = "VMConfiguration"
SERVER_PROPERTIES_KEY = "serverProperties"
ACTION_KEY = "action"
STATUS_KEY = "status"
FORCE_KEY = 'force'
EMAIL_KEY_KEY = "emailKey"
PASSWORD_KEY = "password"
EMAIL_KEY = "email"
LAST_NAME_KEY = "lastName"
FIRST_NAME_KEY = "firstName"
TOKEN_KEY = "token"

SET_STATUS_ACTION = "setStatus"

DB_ID_KEY = "_id"
USERS_COLLECTION_NAME = "users"
TMP_USERS_COLLECTION_NAME = "tmpUsers"

ACCESS_TOKEN_EXP_KEY = '__Infrary__AccessToken'
STATUS_EXP_KEY = "__Infrary__Status"
MASTERCONF_EXP_KEY = '__Infrary__MasterConf'
SELF_DESTRUCT_EXP_KEY = '__Infrary__SelfDestruct'
IS_MASTER_EXP_KEY = '__Infrary__IsMaster'
VM_CONFIGURATION_EXP_KEY = "__Infrary__VMConfiguration"
ID_EXP_KEY = '__Infrary__ID'
PROVIDER_EXP_KEY = '__Infrary__Provider'
IP_EXP_KEY = '__Infrary__IP'
TEMP_SSH_KEY_EXP_KEY = '__Infrary__TempSSHKey'
SSH_KEY_FINGERPRINT_EXP_KEY = '__Infrary__SSHKeyFingerprint'

API_VERSION = "v0"
CONTAINER_HANDLER = 'local_win'
DB_URI = 'mongodb://gentleseal:eQi2ZdxZLhf4bc5xJ@ds241065.mlab.com:41065/infrarydev'
DB_NAME = 'infrarydev'

TOKEN_USER_ID_KEY = 'uid'
TOKEN_EXPIRY_KEY = 'exp'
SECRET_TOKEN_ENC_KEY = 'totallysecure'

DO_BASE_URL = "https://api.digitalocean.com/v2"

# OCTO "Constants" to tell microservices who to talk to (and how)
OCTO_DOMAIN = '10.0.75.1'
OCTO_PORT = 5000
OCTO_URL = 'http://{}:{}'.format(OCTO_DOMAIN, OCTO_PORT)
AUTHPATH = "/{}/auth".format(API_VERSION)
OCTO_SERVER_SUBMIT_PATH = '/{}/servers/provision/configure'.format(API_VERSION)
OCTO_SERVER_STATUS_SUBMIT_PATH = '/{}/servers/{}/{}'.format(API_VERSION, '{server_provider}', '{server_id}')
OCTO_CONFIGURED_SERVER_SUBMIT_PATH = '/{}/servers/provision/initialise'.format(API_VERSION)

OCTO_TOKEN_KEY = 'OCTO_TOKEN'
OCTO_CONFIGURED_SERVER_SUBMIT_PATH_KEY = 'OCTOCORE_CONFIGURED_SERVER_SUBMIT_PATH'
OCTO_SERVER_SUBMIT_PATH_KEY = 'OCTOCORE_SERVER_SUBMIT_PATH'
OCTO_PORT_KEY = 'OCTOCORE_PORT'
OCTO_DOMAIN_KEY = 'OCTOCORE_DOMAIN'

SENDGRID_API_KEY = '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'

FROM_EMAIL_NAME = "Infrary Bot"
FROM_EMAIL = "noreply@infrary.tk"
EMAIL_VERIFY_LINK = "http://localhost:8080/auth/login?emailKey={}"
USER_CREATION_EMAIL_SUBJECT = "Verify your email"

DO_SUPPORTED_IMAGES = [
    {"id": 30810927, "name": "17.10 x64", "distribution": "Ubuntu", "slug": "ubuntu-17-10-x64", "public": True,
     "regions": ["nyc1", "sfo1", "nyc2", "ams2", "sgp1", "lon1", "nyc3", "ams3", "fra1", "tor1", "sfo2", "blr1"],
     "created_at": "2018-01-10T13:58:02Z", "min_disk_size": 20, "type": "snapshot", "size_gigabytes": 0.32},
    {"id": 30821337, "name": "14.04.5 x64", "distribution": "Ubuntu", "slug": "ubuntu-14-04-x64", "public": True,
     "regions": ["nyc1", "sfo1", "nyc2", "ams2", "sgp1", "lon1", "nyc3", "ams3", "fra1", "tor1", "sfo2", "blr1"],
     "created_at": "2018-01-11T00:13:37Z", "min_disk_size": 20, "type": "snapshot", "size_gigabytes": 0.27},
    {"id": 30875099, "name": "16.04.3 x64", "distribution": "Ubuntu", "slug": "ubuntu-16-04-x64", "public": True,
     "regions": ["nyc1", "sfo1", "nyc2", "ams2", "sgp1", "lon1", "nyc3", "ams3", "fra1", "tor1", "sfo2", "blr1"],
     "created_at": "2018-01-13T00:41:21Z", "min_disk_size": 20, "type": "snapshot", "size_gigabytes": 0.3}]

USER_CREATION_EMAIL_HTML = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD XHTML 1.0 Transitional //EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><html xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office"><head><!--[if gte mso 9]><xml> <o:OfficeDocumentSettings> <o:AllowPNG/> <o:PixelsPerInch>96</o:PixelsPerInch> </o:OfficeDocumentSettings> </xml><![endif]--> <meta http-equiv="Content-Type" content="text/html; charset=utf-8"> <meta name="viewport" content="width=device-width"> <meta http-equiv="X-UA-Compatible" content="IE=edge"> <title>BF-simple-template</title> <style type="text/css" id="media-query"> body{margin: 0; padding: 0;}table, tr, td{vertical-align: top; border-collapse: collapse;}.ie-browser table, .mso-container table{table-layout: fixed;}*{line-height: inherit;}a[x-apple-data-detectors=true]{color: inherit !important; text-decoration: none !important;}[owa] .img-container div, [owa] .img-container button{display: block !important;}[owa] .fullwidth button{width: 100% !important;}[owa] .block-grid .col{display: table-cell; float: none !important; vertical-align: top;}.ie-browser .num12, .ie-browser .block-grid, [owa] .num12, [owa] .block-grid{width: 500px !important;}.ExternalClass, .ExternalClass p, .ExternalClass span, .ExternalClass font, .ExternalClass td, .ExternalClass div{line-height: 100%;}.ie-browser .mixed-two-up .num4, [owa] .mixed-two-up .num4{width: 164px !important;}.ie-browser .mixed-two-up .num8, [owa] .mixed-two-up .num8{width: 328px !important;}.ie-browser .block-grid.two-up .col, [owa] .block-grid.two-up .col{width: 250px !important;}.ie-browser .block-grid.three-up .col, [owa] .block-grid.three-up .col{width: 166px !important;}.ie-browser .block-grid.four-up .col, [owa] .block-grid.four-up .col{width: 125px !important;}.ie-browser .block-grid.five-up .col, [owa] .block-grid.five-up .col{width: 100px !important;}.ie-browser .block-grid.six-up .col, [owa] .block-grid.six-up .col{width: 83px !important;}.ie-browser .block-grid.seven-up .col, [owa] .block-grid.seven-up .col{width: 71px !important;}.ie-browser .block-grid.eight-up .col, [owa] .block-grid.eight-up .col{width: 62px !important;}.ie-browser .block-grid.nine-up .col, [owa] .block-grid.nine-up .col{width: 55px !important;}.ie-browser .block-grid.ten-up .col, [owa] .block-grid.ten-up .col{width: 50px !important;}.ie-browser .block-grid.eleven-up .col, [owa] .block-grid.eleven-up .col{width: 45px !important;}.ie-browser .block-grid.twelve-up .col, [owa] .block-grid.twelve-up .col{width: 41px !important;}@media only screen and (min-width: 520px){.block-grid{width: 500px !important;}.block-grid .col{vertical-align: top;}.block-grid .col.num12{width: 500px !important;}.block-grid.mixed-two-up .col.num4{width: 164px !important;}.block-grid.mixed-two-up .col.num8{width: 328px !important;}.block-grid.two-up .col{width: 250px !important;}.block-grid.three-up .col{width: 166px !important;}.block-grid.four-up .col{width: 125px !important;}.block-grid.five-up .col{width: 100px !important;}.block-grid.six-up .col{width: 83px !important;}.block-grid.seven-up .col{width: 71px !important;}.block-grid.eight-up .col{width: 62px !important;}.block-grid.nine-up .col{width: 55px !important;}.block-grid.ten-up .col{width: 50px !important;}.block-grid.eleven-up .col{width: 45px !important;}.block-grid.twelve-up .col{width: 41px !important;}}@media (max-width: 520px){.block-grid, .col{min-width: 320px !important; max-width: 100% !important; display: block !important;}.block-grid{width: calc(100% - 40px) !important;}.col{width: 100% !important;}.col > div{margin: 0 auto;}img.fullwidth, img.fullwidthOnMobile{max-width: 100% !important;}.no-stack .col{min-width: 0 !important; display: table-cell !important;}.no-stack.two-up .col{width: 50% !important;}.no-stack.mixed-two-up .col.num4{width: 33% !important;}.no-stack.mixed-two-up .col.num8{width: 66% !important;}.no-stack.three-up .col.num4{width: 33% !important;}.no-stack.four-up .col.num3{width: 25% !important;}}</style></head><body class="clean-body" style="margin: 0;padding: 0;-webkit-text-size-adjust: 100%;background-color: #FFFFFF"> <style type="text/css" id="media-query-bodytag"> @media (max-width: 520px){.block-grid{min-width: 320px!important; max-width: 100%!important; width: 100%!important; display: block!important;}.col{min-width: 320px!important; max-width: 100%!important; width: 100%!important; display: block!important;}.col > div{margin: 0 auto;}img.fullwidth{max-width: 100%!important;}img.fullwidthOnMobile{max-width: 100%!important;}.no-stack .col{min-width: 0!important;display: table-cell!important;}.no-stack.two-up .col{width: 50%!important;}.no-stack.mixed-two-up .col.num4{width: 33%!important;}.no-stack.mixed-two-up .col.num8{width: 66%!important;}.no-stack.three-up .col.num4{width: 33%!important}.no-stack.four-up .col.num3{width: 25%!important}}</style> <table class="nl-container" style="border-collapse: collapse;table-layout: fixed;border-spacing: 0;mso-table-lspace: 0pt;mso-table-rspace: 0pt;vertical-align: top;min-width: 320px;Margin: 0 auto;background-color: #FFFFFF;width: 100%" cellpadding="0" cellspacing="0"><tbody><tr style="vertical-align: top"><td style="word-break: break-word;border-collapse: collapse !important;vertical-align: top"> <div style="background-color:#2C2D37;"> <div style="Margin: 0 auto;min-width: 320px;max-width: 500px;overflow-wrap: break-word;word-wrap: break-word;word-break: break-word;background-color: transparent;" class="block-grid "> <div style="border-collapse: collapse;display: table;width: 100%;background-color:transparent;"> <div class="col num12" style="min-width: 320px;max-width: 500px;display: table-cell;vertical-align: top;"> <div style="background-color: transparent; width: 100% !important;"> <div style="border-top: 0px solid transparent; border-left: 0px solid transparent; border-bottom: 0px solid transparent; border-right: 0px solid transparent; padding-top:5px; padding-bottom:5px; padding-right: 0px; padding-left: 0px;"> <div align="center" class="img-container center fixedwidth" style="padding-right: 0px; padding-left: 0px;"> <a href="https://beefree.io" target="_blank"> <img class="center fixedwidth" align="center" border="0" src="https://i.imgur.com/K8bGnFC.png" alt="Image" title="Image" style="outline: none;text-decoration: none;-ms-interpolation-mode: bicubic;clear: both;display: block !important;border: none;height: auto;float: none;width: 100%;max-width: 225px" width="225"> </a></div></div></div></div></div></div></div><div style="background-color:#323341;"> <div style="Margin: 0 auto;min-width: 320px;max-width: 500px;overflow-wrap: break-word;word-wrap: break-word;word-break: break-word;background-color: transparent;" class="block-grid "> <div style="border-collapse: collapse;display: table;width: 100%;background-color:transparent;"> <div class="col num12" style="min-width: 320px;max-width: 500px;display: table-cell;vertical-align: top;"> <div style="background-color: transparent; width: 100% !important;"> <div style="border-top: 0px solid transparent; border-left: 0px solid transparent; border-bottom: 0px solid transparent; border-right: 0px solid transparent; padding-top:0px; padding-bottom:0px; padding-right: 0px; padding-left: 0px;"> <table border="0" cellpadding="0" cellspacing="0" width="100%" class="divider" style="border-collapse: collapse;table-layout: fixed;border-spacing: 0;mso-table-lspace: 0pt;mso-table-rspace: 0pt;vertical-align: top;min-width: 100%;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%"> <tbody> <tr style="vertical-align: top"> <td class="divider_inner" style="word-break: break-word;border-collapse: collapse !important;vertical-align: top;padding-right: 10px;padding-left: 10px;padding-top: 10px;padding-bottom: 10px;min-width: 100%;mso-line-height-rule: exactly;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%"> <table class="divider_content" align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="border-collapse: collapse;table-layout: fixed;border-spacing: 0;mso-table-lspace: 0pt;mso-table-rspace: 0pt;vertical-align: top;border-top: 10px solid transparent;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%"> <tbody> <tr style="vertical-align: top"> <td style="word-break: break-word;border-collapse: collapse !important;vertical-align: top;mso-line-height-rule: exactly;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%"> <span></span> </td></tr></tbody> </table> </td></tr></tbody></table> <div style="font-family:Arial, \'Helvetica Neue\', Helvetica, sans-serif;line-height:120%;color:#ffffff; padding-right: 0px; padding-left: 0px; padding-top: 30px; padding-bottom: 30px;"><div style="line-height:14px;font-size:12px;color:#ffffff;font-family:Arial, \'Helvetica Neue\', Helvetica, sans-serif;text-align:left;"><p style="margin: 0;font-size: 14px;line-height: 17px;text-align: center"><strong><span style="font-size: 28px; line-height: 33px;">Welcome to Infrary!</span></strong></p><p style="margin: 0;font-size: 14px;line-height: 17px;text-align: center">&#160;<br></p><p style="margin: 0;font-size: 14px;line-height: 17px;text-align: center">&#160;<br></p><p style="margin: 0;font-size: 14px;line-height: 17px;text-align: center">&#160;<span style="font-size: 24px; line-height: 28px;">Your verification code is:</span><br></p><p style="margin: 0;line-height: 14px;text-align: center;font-size: 12px"><span style="font-size: 24px; line-height: 28px;">**key**</span></p></div></div><div align="center" class="button-container center" style="padding-right: 10px; padding-left: 10px; padding-top:15px; padding-bottom:10px;"> <a href="**url**" target="_blank" style="display: block;text-decoration: none;-webkit-text-size-adjust: none;text-align: center;color: #ffffff; background-color: #C7702E; border-radius: 25px; -webkit-border-radius: 25px; -moz-border-radius: 25px; max-width: 116px; width: 76px;width: auto; border: 0px solid transparent;padding-top: 5px; padding-right: 20px; padding-bottom: 5px; padding-left: 20px; font-family: Arial, \'Helvetica Neue\', Helvetica, sans-serif;mso-border-alt: none"> <span style="font-size:16px;line-height:32px;"><span style="font-size: 14px; line-height: 28px;" data-mce-style="font-size: 14px;">Show more</span></span> </a> </div><table border="0" cellpadding="0" cellspacing="0" width="100%" class="divider" style="border-collapse: collapse;table-layout: fixed;border-spacing: 0;mso-table-lspace: 0pt;mso-table-rspace: 0pt;vertical-align: top;min-width: 100%;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%"> <tbody> <tr style="vertical-align: top"> <td class="divider_inner" style="word-break: break-word;border-collapse: collapse !important;vertical-align: top;padding-right: 10px;padding-left: 10px;padding-top: 10px;padding-bottom: 10px;min-width: 100%;mso-line-height-rule: exactly;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%"> <table class="divider_content" align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="border-collapse: collapse;table-layout: fixed;border-spacing: 0;mso-table-lspace: 0pt;mso-table-rspace: 0pt;vertical-align: top;border-top: 10px solid transparent;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%"> <tbody> <tr style="vertical-align: top"> <td style="word-break: break-word;border-collapse: collapse !important;vertical-align: top;mso-line-height-rule: exactly;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%"> <span></span> </td></tr></tbody> </table> </td></tr></tbody></table> <div align="center" class="img-container center autowidth " style="padding-right: 0px; padding-left: 0px;"> <img class="center autowidth " align="center" border="0" src="https://pro-bee-beepro-assets.s3.amazonaws.com/templates/default/common/bee_rocket.png" alt="Image" title="Image" style="outline: none;text-decoration: none;-ms-interpolation-mode: bicubic;clear: both;display: block !important;border: 0;height: auto;float: none;width: 100%;max-width: 402px" width="402"></div></div></div></div></div></div></div></td></tr></tbody> </table> </body></html>'

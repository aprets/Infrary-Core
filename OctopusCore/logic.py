import datetime
import json
import random
import string
import time

import bcrypt
import jwt
import sendgrid
from bson.objectid import ObjectId, InvalidId
from flask import jsonify
from sendgrid.helpers.mail import *

import db
from api import CONTAINER_HANDLER, OCTOCORE_DOMAIN, OCTOCORE_PORT, OCTOCORE_SERVER_SUBMIT_PATH, \
    OCTOCORE_CONFIGURED_SERVER_SUBMIT_PATH


def launch_container(image, cmd, octo_token=None, env=None, detach=False, add_octo=True):
    if env is None:
        env = {}
    if CONTAINER_HANDLER == 'local':
        import docker
        docker = docker.DockerClient(base_url='tcp://127.0.0.1:2375')
        if add_octo:
            env['OCTO_TOKEN'] = octo_token
            env['OCTOCORE_DOMAIN'] = OCTOCORE_DOMAIN
            env['OCTOCORE_PORT'] = OCTOCORE_PORT
            env['OCTOCORE_SERVER_SUBMIT_PATH'] = OCTOCORE_SERVER_SUBMIT_PATH
            env['OCTOCORE_CONFIGURED_SERVER_SUBMIT_PATH'] = OCTOCORE_CONFIGURED_SERVER_SUBMIT_PATH
        name = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(25))
        print cmd, env
        out = docker.containers.run(image, cmd, environment=env, auto_remove=detach, name=name, network_mode='host',
                                    detach=detach)
        if not detach:
            container = docker.containers.get(name)
            container.remove()
        return out
    else:
        exit(1)


html_email = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD XHTML 1.0 Transitional //EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><html xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office"><head><!--[if gte mso 9]><xml> <o:OfficeDocumentSettings> <o:AllowPNG/> <o:PixelsPerInch>96</o:PixelsPerInch> </o:OfficeDocumentSettings> </xml><![endif]--> <meta http-equiv="Content-Type" content="text/html; charset=utf-8"> <meta name="viewport" content="width=device-width"> <meta http-equiv="X-UA-Compatible" content="IE=edge"> <title>BF-simple-template</title> <style type="text/css" id="media-query"> body{margin: 0; padding: 0;}table, tr, td{vertical-align: top; border-collapse: collapse;}.ie-browser table, .mso-container table{table-layout: fixed;}*{line-height: inherit;}a[x-apple-data-detectors=true]{color: inherit !important; text-decoration: none !important;}[owa] .img-container div, [owa] .img-container button{display: block !important;}[owa] .fullwidth button{width: 100% !important;}[owa] .block-grid .col{display: table-cell; float: none !important; vertical-align: top;}.ie-browser .num12, .ie-browser .block-grid, [owa] .num12, [owa] .block-grid{width: 500px !important;}.ExternalClass, .ExternalClass p, .ExternalClass span, .ExternalClass font, .ExternalClass td, .ExternalClass div{line-height: 100%;}.ie-browser .mixed-two-up .num4, [owa] .mixed-two-up .num4{width: 164px !important;}.ie-browser .mixed-two-up .num8, [owa] .mixed-two-up .num8{width: 328px !important;}.ie-browser .block-grid.two-up .col, [owa] .block-grid.two-up .col{width: 250px !important;}.ie-browser .block-grid.three-up .col, [owa] .block-grid.three-up .col{width: 166px !important;}.ie-browser .block-grid.four-up .col, [owa] .block-grid.four-up .col{width: 125px !important;}.ie-browser .block-grid.five-up .col, [owa] .block-grid.five-up .col{width: 100px !important;}.ie-browser .block-grid.six-up .col, [owa] .block-grid.six-up .col{width: 83px !important;}.ie-browser .block-grid.seven-up .col, [owa] .block-grid.seven-up .col{width: 71px !important;}.ie-browser .block-grid.eight-up .col, [owa] .block-grid.eight-up .col{width: 62px !important;}.ie-browser .block-grid.nine-up .col, [owa] .block-grid.nine-up .col{width: 55px !important;}.ie-browser .block-grid.ten-up .col, [owa] .block-grid.ten-up .col{width: 50px !important;}.ie-browser .block-grid.eleven-up .col, [owa] .block-grid.eleven-up .col{width: 45px !important;}.ie-browser .block-grid.twelve-up .col, [owa] .block-grid.twelve-up .col{width: 41px !important;}@media only screen and (min-width: 520px){.block-grid{width: 500px !important;}.block-grid .col{vertical-align: top;}.block-grid .col.num12{width: 500px !important;}.block-grid.mixed-two-up .col.num4{width: 164px !important;}.block-grid.mixed-two-up .col.num8{width: 328px !important;}.block-grid.two-up .col{width: 250px !important;}.block-grid.three-up .col{width: 166px !important;}.block-grid.four-up .col{width: 125px !important;}.block-grid.five-up .col{width: 100px !important;}.block-grid.six-up .col{width: 83px !important;}.block-grid.seven-up .col{width: 71px !important;}.block-grid.eight-up .col{width: 62px !important;}.block-grid.nine-up .col{width: 55px !important;}.block-grid.ten-up .col{width: 50px !important;}.block-grid.eleven-up .col{width: 45px !important;}.block-grid.twelve-up .col{width: 41px !important;}}@media (max-width: 520px){.block-grid, .col{min-width: 320px !important; max-width: 100% !important; display: block !important;}.block-grid{width: calc(100% - 40px) !important;}.col{width: 100% !important;}.col > div{margin: 0 auto;}img.fullwidth, img.fullwidthOnMobile{max-width: 100% !important;}.no-stack .col{min-width: 0 !important; display: table-cell !important;}.no-stack.two-up .col{width: 50% !important;}.no-stack.mixed-two-up .col.num4{width: 33% !important;}.no-stack.mixed-two-up .col.num8{width: 66% !important;}.no-stack.three-up .col.num4{width: 33% !important;}.no-stack.four-up .col.num3{width: 25% !important;}}</style></head><body class="clean-body" style="margin: 0;padding: 0;-webkit-text-size-adjust: 100%;background-color: #FFFFFF"> <style type="text/css" id="media-query-bodytag"> @media (max-width: 520px){.block-grid{min-width: 320px!important; max-width: 100%!important; width: 100%!important; display: block!important;}.col{min-width: 320px!important; max-width: 100%!important; width: 100%!important; display: block!important;}.col > div{margin: 0 auto;}img.fullwidth{max-width: 100%!important;}img.fullwidthOnMobile{max-width: 100%!important;}.no-stack .col{min-width: 0!important;display: table-cell!important;}.no-stack.two-up .col{width: 50%!important;}.no-stack.mixed-two-up .col.num4{width: 33%!important;}.no-stack.mixed-two-up .col.num8{width: 66%!important;}.no-stack.three-up .col.num4{width: 33%!important}.no-stack.four-up .col.num3{width: 25%!important}}</style> <table class="nl-container" style="border-collapse: collapse;table-layout: fixed;border-spacing: 0;mso-table-lspace: 0pt;mso-table-rspace: 0pt;vertical-align: top;min-width: 320px;Margin: 0 auto;background-color: #FFFFFF;width: 100%" cellpadding="0" cellspacing="0"><tbody><tr style="vertical-align: top"><td style="word-break: break-word;border-collapse: collapse !important;vertical-align: top"> <div style="background-color:#2C2D37;"> <div style="Margin: 0 auto;min-width: 320px;max-width: 500px;overflow-wrap: break-word;word-wrap: break-word;word-break: break-word;background-color: transparent;" class="block-grid "> <div style="border-collapse: collapse;display: table;width: 100%;background-color:transparent;"> <div class="col num12" style="min-width: 320px;max-width: 500px;display: table-cell;vertical-align: top;"> <div style="background-color: transparent; width: 100% !important;"> <div style="border-top: 0px solid transparent; border-left: 0px solid transparent; border-bottom: 0px solid transparent; border-right: 0px solid transparent; padding-top:5px; padding-bottom:5px; padding-right: 0px; padding-left: 0px;"> <div align="center" class="img-container center fixedwidth" style="padding-right: 0px; padding-left: 0px;"> <a href="https://beefree.io" target="_blank"> <img class="center fixedwidth" align="center" border="0" src="https://i.imgur.com/K8bGnFC.png" alt="Image" title="Image" style="outline: none;text-decoration: none;-ms-interpolation-mode: bicubic;clear: both;display: block !important;border: none;height: auto;float: none;width: 100%;max-width: 225px" width="225"> </a></div></div></div></div></div></div></div><div style="background-color:#323341;"> <div style="Margin: 0 auto;min-width: 320px;max-width: 500px;overflow-wrap: break-word;word-wrap: break-word;word-break: break-word;background-color: transparent;" class="block-grid "> <div style="border-collapse: collapse;display: table;width: 100%;background-color:transparent;"> <div class="col num12" style="min-width: 320px;max-width: 500px;display: table-cell;vertical-align: top;"> <div style="background-color: transparent; width: 100% !important;"> <div style="border-top: 0px solid transparent; border-left: 0px solid transparent; border-bottom: 0px solid transparent; border-right: 0px solid transparent; padding-top:0px; padding-bottom:0px; padding-right: 0px; padding-left: 0px;"> <table border="0" cellpadding="0" cellspacing="0" width="100%" class="divider" style="border-collapse: collapse;table-layout: fixed;border-spacing: 0;mso-table-lspace: 0pt;mso-table-rspace: 0pt;vertical-align: top;min-width: 100%;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%"> <tbody> <tr style="vertical-align: top"> <td class="divider_inner" style="word-break: break-word;border-collapse: collapse !important;vertical-align: top;padding-right: 10px;padding-left: 10px;padding-top: 10px;padding-bottom: 10px;min-width: 100%;mso-line-height-rule: exactly;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%"> <table class="divider_content" align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="border-collapse: collapse;table-layout: fixed;border-spacing: 0;mso-table-lspace: 0pt;mso-table-rspace: 0pt;vertical-align: top;border-top: 10px solid transparent;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%"> <tbody> <tr style="vertical-align: top"> <td style="word-break: break-word;border-collapse: collapse !important;vertical-align: top;mso-line-height-rule: exactly;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%"> <span></span> </td></tr></tbody> </table> </td></tr></tbody></table> <div style="font-family:Arial, \'Helvetica Neue\', Helvetica, sans-serif;line-height:120%;color:#ffffff; padding-right: 0px; padding-left: 0px; padding-top: 30px; padding-bottom: 30px;"><div style="line-height:14px;font-size:12px;color:#ffffff;font-family:Arial, \'Helvetica Neue\', Helvetica, sans-serif;text-align:left;"><p style="margin: 0;font-size: 14px;line-height: 17px;text-align: center"><strong><span style="font-size: 28px; line-height: 33px;">Welcome to Infrary!</span></strong></p><p style="margin: 0;font-size: 14px;line-height: 17px;text-align: center">&#160;<br></p><p style="margin: 0;font-size: 14px;line-height: 17px;text-align: center">&#160;<br></p><p style="margin: 0;font-size: 14px;line-height: 17px;text-align: center">&#160;<span style="font-size: 24px; line-height: 28px;">Your verification code is:</span><br></p><p style="margin: 0;line-height: 14px;text-align: center;font-size: 12px"><span style="font-size: 24px; line-height: 28px;">**key**</span></p></div></div><div align="center" class="button-container center" style="padding-right: 10px; padding-left: 10px; padding-top:15px; padding-bottom:10px;"> <a href="**url**" target="_blank" style="display: block;text-decoration: none;-webkit-text-size-adjust: none;text-align: center;color: #ffffff; background-color: #C7702E; border-radius: 25px; -webkit-border-radius: 25px; -moz-border-radius: 25px; max-width: 116px; width: 76px;width: auto; border-top: 0px solid transparent; border-right: 0px solid transparent; border-bottom: 0px solid transparent; border-left: 0px solid transparent; padding-top: 5px; padding-right: 20px; padding-bottom: 5px; padding-left: 20px; font-family: Arial, \'Helvetica Neue\', Helvetica, sans-serif;mso-border-alt: none"> <span style="font-size:16px;line-height:32px;"><span style="font-size: 14px; line-height: 28px;" data-mce-style="font-size: 14px;">Show more</span></span> </a> </div><table border="0" cellpadding="0" cellspacing="0" width="100%" class="divider" style="border-collapse: collapse;table-layout: fixed;border-spacing: 0;mso-table-lspace: 0pt;mso-table-rspace: 0pt;vertical-align: top;min-width: 100%;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%"> <tbody> <tr style="vertical-align: top"> <td class="divider_inner" style="word-break: break-word;border-collapse: collapse !important;vertical-align: top;padding-right: 10px;padding-left: 10px;padding-top: 10px;padding-bottom: 10px;min-width: 100%;mso-line-height-rule: exactly;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%"> <table class="divider_content" align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="border-collapse: collapse;table-layout: fixed;border-spacing: 0;mso-table-lspace: 0pt;mso-table-rspace: 0pt;vertical-align: top;border-top: 10px solid transparent;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%"> <tbody> <tr style="vertical-align: top"> <td style="word-break: break-word;border-collapse: collapse !important;vertical-align: top;mso-line-height-rule: exactly;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%"> <span></span> </td></tr></tbody> </table> </td></tr></tbody></table> <div align="center" class="img-container center autowidth " style="padding-right: 0px; padding-left: 0px;"> <img class="center autowidth " align="center" border="0" src="https://pro-bee-beepro-assets.s3.amazonaws.com/templates/default/common/bee_rocket.png" alt="Image" title="Image" style="outline: none;text-decoration: none;-ms-interpolation-mode: bicubic;clear: both;display: block !important;border: 0;height: auto;float: none;width: 100%;max-width: 402px" width="402"></div></div></div></div></div></div></div></td></tr></tbody> </table> </body></html>'


# noinspection SpellCheckingInspection
def send_sendgrid_email_key_email(email_key, email):
    # noinspection SpellCheckingInspection
    sendgrid_client = sendgrid.SendGridAPIClient(
        apikey='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'
    )
    from_email = Email("noreply@infrary.tk", "Infrary Bot")
    to_email = Email(email)
    subject = "Verify your email"
    content = Content("text/plain", "emailKey = {}".format(email_key))
    the_email = Mail()
    the_email.from_email = from_email
    the_email.subject = subject
    personalization = Personalization()
    personalization.add_to(to_email)
    the_email.add_personalization(personalization)
    the_email.add_content(content)
    the_email.add_content(Content
                          ("text/html",html_email.
                           replace("**key**", email_key).
                           replace("**url**", "http://localhost:8080/auth/login?emailKey={}".format(email_key))))
    return sendgrid_client.client.mail.send.post(request_body=the_email.get())

# noinspection PyClassHasNoInit
class User:
    @staticmethod
    def register(first_name, last_name, email, password):
        user_already_exist = db.exists_once_or_not({'email': email}, db_name="users") or db.exists_once_or_not(
            {'email': email},
            db_name="tmpUsers")
        if not user_already_exist:
            email_key = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(72))
            response = send_sendgrid_email_key_email(email_key, email)
            if response.status_code == 202:

                # Hash 'n salt
                hashed = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())
                print hashed

                db.create_document({
                    "firstName": first_name,
                    "lastName": last_name,
                    "email": email,
                    "hash": hashed,
                    "emailKey": email_key,
                    "createdAt": datetime.datetime.utcnow(),
                }, db_name="tmpUsers")

                return "201 Created\n{}\n\n".format("Verify the email address to finish account creation"), 201

            else:
                return "400 Bad Request\n{}\n\n".format("Sending email failed"), 400

        else:
            return "400 Bad Request\n{}\n\n".format("User already exists"), 400

    @staticmethod
    def verify(email_key):
        try:
            tmp_user, does_exist = db.find_one_if_exists({'emailKey': email_key}, db_name="tmpUsers")

            if does_exist:

                db.delete_one_document({'emailKey': email_key}, db_name="tmpUsers")

                tmp_user["servers"] = []
                tmp_user["provisioning"] = []
                tmp_user.pop("emailKey")

                db.create_document(tmp_user, db_name="users")

                return "201 Created\n{}\n\n".format("Account created"), 201
            else:
                return "400 Bad Request\n{}\n\n".format("Invalid emailKey"), 400
        except SystemError:
            return "System Error. Please try creating an account again.", 500

    @staticmethod
    def login(email, password):

        user, does_exist = db.find_one_if_exists({'email': email}, db_name="users")

        if does_exist:
            try:
                does_match = bcrypt.checkpw(password.encode('utf8'), user["hash"].encode('utf8'))
            except ValueError:
                return "System error, please contact support regarding your account", 500
            if does_match:
                exp_time = int(time.time()) + 60 * 60  # expire in an hour
                payload = {'exp': exp_time, 'uid': str(user["_id"])}
                jwt_token = jwt.encode(payload, 'totallysecure', 'HS256')
                return jwt_token, 200
            else:
                return "400 Bad Request\n{}\n\n".format("Invalid credentials"), 400
        else:
            return "400 Bad Request\n{}\n\n".format("Invalid credentials"), 400


# noinspection PyClassHasNoInit
class Server:
    @staticmethod
    def get(provider, server_id, user_id):
        try:
            ObjectId(user_id)
        except InvalidId:
            return "Invalid userID format", 400
        try:
            user, does_exist = db.find_one_if_exists({'_id': ObjectId(user_id)}, db_name="users")

            if not does_exist:
                return "System error, please contact support", 500

            for server in user["servers"]:
                if server["__Infrary__ID"] == server_id and server['__Infrary__Provider'] == provider:
                    return jsonify(server)

            raise ValueError("invalidServerIDorProvider")

        except ValueError:
            return "Incorrect server id or provider", 404

    @staticmethod
    def delete(provider, server_id, force_delete, user_id, octo_token):

        try:
            ObjectId(user_id)
        except InvalidId:
            return "Invalid userID format", 400

        user, does_exist = db.find_one_if_exists({'_id': ObjectId(user_id)}, "users")

        if not does_exist:
            return "System error, please contact support", 500

        else:

            server_list = [server for server in user["servers"]
                           if server["__Infrary__ID"] == server_id and server['__Infrary__Provider'] == provider]

            found_in_servers = not len(server_list) == 0
            found_in_provisioning = False

            prov_server_list = []
            if force_delete:
                prov_server_list = [server for server in user["provisioning"]
                                    if
                                    server["__Infrary__ID"] == server_id and server['__Infrary__Provider'] == provider]
                found_in_provisioning = not len(prov_server_list) == 0

            if len(server_list) == 0 and len(prov_server_list) == 0:
                return "Incorrect server id", 404

            if len(server_list) > 1 and len(prov_server_list) > 1:
                return "System error, please contact support", 500

            response = "Server destroyed", 200

            if found_in_servers:

                server = server_list[0]

                # todo asyncme
                out = launch_container('provisioner', 'destroy', octo_token,
                                       {'SERVER_ID': server_id, 'SERVER_PROVIDER': provider,
                                        'ACCESS_TOKEN': server['__Infrary__AccessToken']})
                out = int(out[0:3])
                if out == 204:
                    # delete from servers

                    db.remove_from_list_param({"_id": ObjectId(user_id)}, "servers",
                                              {"__Infrary__ID": server_id, "__Infrary__Provider": provider},
                                              db_name="users")

                elif out == 404:
                    return 'Provider found no server, please contact support', 500

                else:
                    return 'An error has occurred', 500

            if found_in_provisioning:

                server = prov_server_list[0]

                # todo asyncme
                out = launch_container('provisioner', 'destroy', octo_token,
                                       {'SERVER_ID': server_id, 'SERVER_PROVIDER': provider,
                                        'ACCESS_TOKEN': server['__Infrary__AccessToken']})
                out = int(out[0:3])
                if out == 204:
                    # delete from servers

                    db.remove_from_list_param({"_id": ObjectId(user_id)}, "provisioning",
                                              {"__Infrary__ID": server_id, "__Infrary__Provider": provider},
                                              db_name="users")

                elif out == 404:
                    return 'Provider found no server, please contact support', 500

                else:
                    return 'An error has occurred', 500

            return response

    @staticmethod
    def create(server_properties, vm_configuration, octo_token):
        server_properties["VMConfiguration"] = json.dumps(vm_configuration)
        # todo asyncme
        container = launch_container('provisioner', 'create', octo_token, server_properties)
        return container, 201

    @staticmethod
    def configure(server_dict, temp_key, server_hostname, server_provider, server_id, vm_configuration, user_id,
                  octo_token):

        try:
            ObjectId(user_id)
        except InvalidId:
            return "Invalid userID format", 400

        server_dict.pop('__Infrary__TempSSHKey')

        db.add_to_list_param({'_id': ObjectId(user_id)}, "provisioning", server_dict, db_name="users")

        octo_conf = json.dumps({"serverHostname": server_hostname, "octoToken": octo_token,
                                "serverProvider": server_provider,
                                "serverID": server_id}).replace('"', '\\"')  # todo ITSINTHEVArgs
        vm_configuration = vm_configuration.replace('"', '\\"').replace('\\\\', '\\\\\\')
        container = launch_container('vmconf', '"{}" "{}" "{}"'.format(temp_key, octo_conf, vm_configuration),
                                     octo_token, detach=True)
        return str(container), 200

    @staticmethod
    def initialise(server_id, server_provider, user_id, octo_token, is_master=None, is_self_destruct=None,
                   master_conf=None):

        try:
            ObjectId(user_id)
        except InvalidId:
            return "Invalid userID format", 400

        user, does_exist = db.find_one_if_exists({'_id': ObjectId(user_id)}, "users")

        if not does_exist:
            return "System error, please contact support", 500

        cur_server = []

        for aServer in user["provisioning"]:
            if aServer["__Infrary__ID"] == server_id and aServer['__Infrary__Provider'] == server_provider:
                cur_server.append(aServer)

        if len(cur_server) == 0:
            return "Incorrect server id or provider", 404
        elif len(cur_server) > 1:
            return "System error. Please contact support", 500
        else:
            cur_server = cur_server[0]

        # delete from provisioning
        db.remove_from_list_param({"_id": ObjectId(user_id)}, "provisioning", {
            "__Infrary__ID": server_id,
            "__Infrary__Provider": server_provider
        }, db_name="users")

        if is_master is True:
            cur_server['__Infrary__IsMaster'] = True
            cur_server['__Infrary__MasterConf'] = master_conf
        else:
            cur_server['__Infrary__IsMaster'] = False

        # add to servers
        db.add_to_list_param({"_id": ObjectId(user_id)}, "servers", cur_server, db_name="users")

        tmp = Server.get(server_provider, server_id, user_id)

        if is_self_destruct:
            Server.delete(server_provider, server_id, True, user_id, octo_token)

        return tmp, 200


# noinspection PyClassHasNoInit
class Servers:
    @staticmethod
    def list(user_id):

        try:
            ObjectId(user_id)
        except InvalidId:
            return "Invalid userID format", 400

        user, does_exist = db.find_one_if_exists({'_id': ObjectId(user_id)}, db_name="users")

        if not does_exist:
            return "System error, please contact support", 500

        return jsonify(user["servers"])

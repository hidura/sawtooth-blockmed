# Copyright 2017 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------------
# import base64
#
# import bcrypt
#
# from itsdangerous import BadSignature
from sanic import Blueprint
from sanic import response

# from sawtooth_signing import CryptoFactory

# from rest_api.workflow.authorization import authorized
from rest_api.common.protobuf import payload_pb2
from rest_api.common import helper, transaction
from rest_api.workflow import general, security_messaging
from rest_api.workflow.errors import ApiBadRequest, ApiInternalError
import logging
import requests
from rest_api.GeneralTool import GeneralTool
DOCTORS_BP = Blueprint('doctors')
_client_type_=1

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)
@DOCTORS_BP.get('doctors')
async def get_doctor(request):
    """Fetches complete details of all Accounts in state"""
    idcard = request.headers['idcard']
    headers = {'Content-Type': 'application/json'}
    dataParty = {"username": idcard}
    response_load = requests.post('http://validator:8863/getPrivateKey',
                                  data=GeneralTool().parse2JSON(dataParty),
                                  headers=headers)

    if response_load.status_code != 200:
        raise Exception("There was a problem communicating with the validator.")
    elif response_load.status_code == 200:
        keys = GeneralTool().parseFromJSON(response_load.content.decode())
        public_key = keys['public_key']
        party = await security_messaging.get_party(request.app.config.VAL_CONN, public_key)

        doctorKey = '{}|{}'.format(public_key, '0' + str(_client_type_))

        doctor = await security_messaging.get_doctor(request.app.config.VAL_CONN, doctorKey)
        patient_list_json = []
        patient_list_json.append({
            'name': party.name,
            'lastname': party.lastname,
            'telephone': party.telephone,
            'birthdate': party.birthdate,
            'idcard': party.idcard,
            'sex': doctor.biological_sex,
            'photo': doctor.photo,
            'speciality': doctor.main_speciality
        })

        return response.json(body={'data': patient_list_json},
                             headers=general.get_response_headers())
    else:
        raise Exception("User with no patient registred.")


@DOCTORS_BP.post('doctors')
async def register_new_doctor(request):
    """Updates auth information for the authorized account"""
    # keyfile = common.get_keyfile(request.json.get['signer'])
    """Updates auth information for the authorized account"""
    # keyfile = common.get_keyfile(request.json.get['signer'])
    required_fields = ['first_name', 'last_name', 'idcard_type', 'idcard']
    general.validate_fields(required_fields, request.json)

    name = request.json.get('first_name')
    surname = request.json.get('last_name')
    idcard = request.json.get('idcard')
    idcard_type = int(request.json.get('idcard_type'))
    # private_key = common.get_signer_from_file(keyfile)
    # signer = CryptoFactory(request.app.config.CONTEXT).new_signer(private_key)
    # patient_signer = request.app.config.SIGNER_PATIENT  # .get_public_key().as_hex()

    party_info = {"name": name,
                  "lastname": surname,
                  "idcard": idcard,
                  "telephone": request.json.get('telephone') if 'telephone' in request.json else " ",
                  "birthdate": request.json.get('birthdate') if 'birthdate' in request.json else " ",
                  "idcard_type": idcard_type}

    headers = {'Content-Type': 'application/json'}
    dataParty = {"username": party_info['idcard'], "_client_type_": _client_type_}
    response_load = requests.post('http://validator:8863/getPrivateKey',
                                  data=GeneralTool().parse2JSON(dataParty),
                                  headers=headers)
    batch_lst = []
    if response_load.status_code != 200:
        raise Exception("There was a problem communicating with the validator.")
    elif response_load.status_code == 200 and 'private_key' in GeneralTool().parseFromJSON(
            response_load.content.decode()):
        keys = GeneralTool().parseFromJSON(response_load.content.decode())
        privatekey = keys['private_key']
        public_key = keys['public_key']
    elif response_load.status_code == 200 and 'private_key' not in GeneralTool().parseFromJSON(
            response_load.content.decode()):

        party_txn, privatekey, public_key = general.addParty(party_info, _client_type_)
        batch_lst.append(party_txn)
    else:
        raise Exception("There was a problem communicating with the validator.")

    doctor_signer = GeneralTool().addSigner(GeneralTool().ParsePrivateKey(private_key_str=privatekey))


    doctorKey='{}|{}'.format(public_key, '0'+str(_client_type_))
    doctor_info = {'party_key': public_key,
                    'doctor_key': doctorKey,
                    "main_speciality":request.json.get('main_speciality')
                    if 'main_speciality' in request.json else " ",
                    "photo": request.json.get('photo')
                    if 'photo' in request.json else '/static/pictures/man.svg'
                    if request.json.get('biological_sex') == 'm' else '/static/pictures/woman.svg',
                    "bio": request.json.get('bio') if 'bio' in request.json else " ",
                   'biological_sex': request.json.get('biological_sex')
                    }


    doctor_txn = transaction.create_doctor(
        txn_signer=doctor_signer,
        batch_signer=doctor_signer,
        doctor_info=doctor_info)
    batch_lst.append(doctor_txn)

    batch, batch_id = transaction.make_batch_and_id(batch_lst, doctor_signer)
    await security_messaging.add_doctor(
        request.app.config.VAL_CONN,
        request.app.config.TIMEOUT,
        [batch])

    try:
        await security_messaging.check_batch_status(
            request.app.config.VAL_CONN, [batch_id])
    except (ApiBadRequest, ApiInternalError) as err:
        raise err

    return response.json(body={'status': general.DONE},
                         headers=general.get_response_headers())


@DOCTORS_BP.post('doctors/update')
async def update_doctor(request):
    """Updates auth information for the authorized account"""
    # keyfile = common.get_keyfile(request.json.get['signer'])
    required_fields = ['idcard']
    general.validate_fields(required_fields, request.json)

    idcard = request.json.get('idcard')

    headers = {'Content-Type': 'application/json'}
    dataParty = {"username": idcard}
    response_load = requests.post('http://validator:8863/getPrivateKey',
                                  data=GeneralTool().parse2JSON(dataParty),
                                  headers=headers)

    if response_load.status_code != 200:
        raise Exception("There was a problem communicating with the validator.")
    elif response_load.status_code == 200:
        keys = GeneralTool().parseFromJSON(response_load.content.decode())
        public_key = keys['public_key']
        party = await security_messaging.get_party(request.app.config.VAL_CONN, public_key)

        doctorKey = '{}|{}'.format(public_key, '0' + str(_client_type_))

        doctor = await security_messaging.get_doctor(request.app.config.VAL_CONN, doctorKey)
        party_info = {
            'name': request.json.get('telephone') if 'telephone' in request.json else party.name,
            'lastname': party.lastname,
            'telephone': party.telephone,
            'birthdate': party.birthdate,
            'idcard': party.idcard,
            'sex': party.sex,
            'photo': doctor.photo,
            'speciality': doctor.main_speciality
        }

        batch_lst=[]
        party_txn, privatekey, public_key = general.update_party(party_info)
        batch_lst.append(party_txn)

        doctor_signer = GeneralTool().addSigner(GeneralTool().ParsePrivateKey(private_key_str=privatekey))

        doctorKey='{}|{}'.format(public_key, '0'+str(_client_type_))
        doctor_info = {'party_key': public_key,
                        'doctor_key': doctorKey,
                        "main_speciality":request.json.get('main_speciality')
                        if 'main_speciality' in request.json else " ",
                        "photo": request.json.get('photo')
                        if 'photo' in request.json else '/static/pictures/man.svg'
                        if request.json.get('biological_sex') == 'm' else '/static/pictures/woman.svg',
                        "bio": request.json.get('bio') if 'bio' in request.json else " ",
                       'biological_sex': request.json.get('biological_sex')
                        }


        doctor_txn = transaction.create_doctor(
            txn_signer=doctor_signer,
            batch_signer=doctor_signer,
            doctor_info=doctor_info)
        batch_lst.append(doctor_txn)

        batch, batch_id = transaction.make_batch_and_id(batch_lst, doctor_signer)
        await security_messaging.add_doctor(
            request.app.config.VAL_CONN,
            request.app.config.TIMEOUT,
            [batch])

        try:
            await security_messaging.check_batch_status(
                request.app.config.VAL_CONN, [batch_id])
        except (ApiBadRequest, ApiInternalError) as err:
            raise err

        return response.json(body={'status': general.DONE},
                             headers=general.get_response_headers())
    return response.json(body={'status': general.ERROR},
                             headers=general.get_response_headers())


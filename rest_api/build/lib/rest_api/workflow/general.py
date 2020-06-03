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
import getpass
import os

# from Crypto.Cipher import AES

# from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from sawtooth_signing import ParseError
from sawtooth_signing.secp256k1 import Secp256k1PrivateKey
import requests

from rest_api.common import transaction
from datetime import datetime
import julian
from rest_api.workflow.errors import ApiBadRequest, ApiForbidden
from rest_api.common.exceptions import HealthCareException
from rest_api.workflow import security_messaging
# from rest_api.common.protobuf import payload_pb2 as rule_pb2

from rest_api.GeneralTool import GeneralTool
DONE = 'DONE'
ERROR = 'ERROR'
import logging

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)
def get_response_headers():
    return {
        # 'Access-Control-Allow-Credentials': True,
        # 'Access-Control-Allow-Origin': origin,
        'Connection': 'keep-alive'}

def get_request_key_header(request):
    if 'ClientKey' not in request.headers:
        raise ApiForbidden('Client key not specified')
    return request.headers['ClientKey']

def validate_fields(required_fields, request_json):
    try:
        for field in required_fields:
            if request_json.get(field) is None:
                raise ApiBadRequest("{} is required".format(field))
    except (ValueError, AttributeError):
        raise ApiBadRequest("Improper JSON format")


def get_keyfile(user):
    username = getpass.getuser() if user is None else user
    home = os.path.expanduser("~")
    key_dir = os.path.join(home, ".sawtooth", "keys")

    return '{}/{}.priv'.format(key_dir, username)


def get_signer_from_file(keyfile):
    try:
        with open(keyfile) as fd:
            private_key_str = fd.read().strip()
    except OSError as err:
        raise HealthCareException(
            'Failed to read private key {}: {}'.format(
                keyfile, str(err)))

    try:
        private_key = Secp256k1PrivateKey.from_hex(private_key_str)
    except ParseError as e:
        raise HealthCareException(
            'Unable to load private key: {}'.format(str(e)))

    return private_key
    # self._signer = CryptoFactory(create_context('secp256k1')) \
    #     .new_signer(private_key)


def get_signer(request, client_key):
    headers = {'Content-Type': 'application/json'}
    response_load = requests.post('http://validator:8863/getPrivateKey',
                                  data=GeneralTool().parse2JSON({"username": client_key}), headers=headers)

    if response_load.status_code != 200:
        pass #"Bad request, means that the validator server api is not responding."

    keys = GeneralTool().parseFromJSON(response_load.content.decode())
    if request.app.config.SIGNER_CLINIC.get_public_key().as_hex() == client_key:
        client_signer = request.app.config.SIGNER_CLINIC
    elif request.app.config.SIGNER_PATIENT.get_public_key().as_hex() == client_key:
        client_signer = request.app.config.SIGNER_PATIENT
    elif request.app.config.SIGNER_DOCTOR.get_public_key().as_hex() == client_key:
        client_signer = request.app.config.SIGNER_DOCTOR
    elif request.app.config.SIGNER_LAB.get_public_key().as_hex() == client_key:
        client_signer = request.app.config.SIGNER_LAB
    elif request.app.config.SIGNER_INSURANCE.get_public_key().as_hex() == client_key:
        client_signer = request.app.config.SIGNER_INSURANCE
    elif "error" not in keys:
        #Means that there's a key save with this user.
        client_signer = GeneralTool().addSigner(GeneralTool().ParsePrivateKey(private_key_str=keys['private_key']))
    else:
        raise HealthCareException(
            'Unable to load private key for client_key: {}'.format(str(client_key)))
    return client_signer


def addParty(party_info, _client_type_):
    # This method will create a new party for any new participant.
    headers = {'Content-Type': 'application/json'}
    dataParty={"username": party_info['idcard'], "_client_type_": _client_type_}
    response_load = requests.post('http://validator:8863/regkeygen',
                                  data=GeneralTool().parse2JSON(dataParty),
                                  headers=headers)

    if response_load.status_code != 200:
        raise Exception("There was a problem communicating with the validator.")
    else:
        keys = GeneralTool().parseFromJSON(response_load.content.decode())
        privatekey = keys['private_key']
        publickey = keys['public_key']
        LOGGER.warning('Newly created keys: ' + str(keys))
        patient_signer = GeneralTool().addSigner(GeneralTool().ParsePrivateKey(private_key_str=privatekey))
        party_info['public_key']=publickey
        party_txn = transaction.create_party(
            txn_signer=patient_signer,
            batch_signer=patient_signer,
            party_info=party_info
        )
        return party_txn, privatekey, publickey


def update_party(party_info):
    None

def validate_access(consent, consent_type):
    # Here the doctor will be check if its aviable to add information or request information about the patient
    consenttypes={'READ':0,'WRITE':1, 'READ_WRITE':2}
    current_date=date2julian(datetime.now())
    if consenttypes[consent.permission] in consent_type:
        expire_date = float(consent.expire_date)
        LOGGER.warning("CONSENT DATA: " + str(consent))
        LOGGER.warning("Current date: " + str(current_date))
        LOGGER.warning("Expire date: " + str(expire_date))

        if expire_date >= current_date:
            return True

    return False


def date2julian(gdate=None):
    _time = None
    if gdate == None:
        gdate = datetime.now()
    jd = julian.to_jd(gdate, fmt='jd')
    return float(jd)

def julian2date(jdate):
    dt = julian.from_jd(float(jdate))
    return dt
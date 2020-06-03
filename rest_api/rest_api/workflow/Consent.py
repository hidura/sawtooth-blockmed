# Copyright 2020 DIEGO HIDALGO
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

from sanic import Blueprint
from sanic import response
from rest_api.common.protobuf import payload_pb2
from rest_api.common import helper, transaction
from rest_api.workflow import general, security_messaging
from rest_api.workflow.errors import ApiBadRequest, ApiInternalError
import logging
import requests
from rest_api.GeneralTool import GeneralTool
from datetime import datetime, timedelta

CONSENT_BP = Blueprint('consents')
_client_type_=1

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)

@CONSENT_BP.post('consents')
async def register_new_consent(request):
    """Updates auth information for the authorized account"""
    idcard_doctor = request.json.get('idcard_doctor')
    idcard_patient = request.json.get('idcard_patient')
    headers = {'Content-Type': 'application/json'}
    dataParty = {"usernames": {"doctor":idcard_doctor, "patient":idcard_patient}}
    LOGGER.debug("DATA TO SEND: "+str(dataParty))
    response_load = requests.post('http://validator:8863/getKeyDocPat',
                                  data=GeneralTool().parse2JSON(dataParty),
                                  headers=headers)

    if response_load.status_code != 200:
        raise Exception("There was a problem communicating with the validator.")
    elif response_load.status_code == 200:
        keys = GeneralTool().parseFromJSON(response_load.content.decode())

        doctor_priv_key = keys['doctor']['private_key']
        patient_priv_key = keys['patient']['private_key']

        doctor_pub_key = keys['doctor']['public_key']
        patient_pub_key = keys['patient']['public_key']

        time_exp=request.json.get('time_exp')# The amount of minutes to add
        hour_to_exp=datetime.now()+timedelta(minutes=int(time_exp))
        time_to_exp=general.date2julian(hour_to_exp)
        LOGGER.warning("ORIGINAL TO EXP TIME: " + str(time_to_exp))
        record_id = '{}|{}|{}'.format(doctor_pub_key, patient_pub_key, idcard_doctor+idcard_patient)

        batch_lst = []
        patient_signer = GeneralTool().addSigner(GeneralTool().ParsePrivateKey(private_key_str=patient_priv_key))

        consent_info = {'consent_id': record_id, 'time_exp': str(time_to_exp),
                        'doctor_key': doctor_pub_key, 'patient_key': patient_pub_key}

        if request.json.get('permission')=='read_write':
            consent_info['permission']=payload_pb2.permission_type.Name(2)
        elif request.json.get('permission')=='read':
            consent_info['permission']=payload_pb2.permission_type.Name(0)
        elif request.json.get('permission')=='write':
            consent_info['permission']=payload_pb2.permission_type.Name(1)

        evaluation_record_id = '{}|{}'.format(patient_pub_key, idcard_patient)




        consent_txn = transaction.add_consent_patient(
            txn_signer=patient_signer,
            batch_signer=patient_signer,
            consent_info=consent_info)

        batch_lst.append(consent_txn)

        record_patient_txn = transaction.update_record_patient(
            txn_signer=patient_signer,
            batch_signer=patient_signer,
            record_id=evaluation_record_id,
            record_owner=patient_pub_key,
            records=None,
            consent={doctor_pub_key:record_id}
        )

        batch_lst.append(record_patient_txn)


        batch, batch_id = transaction.make_batch_and_id(batch_lst, patient_signer)
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

    return response.json(body={'status': general.ERROR, "msg":"Sucedio un error en este proceso."},
                         headers=general.get_response_headers())


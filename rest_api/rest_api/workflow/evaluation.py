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
from rest_api.common.protobuf.payload_pb2 import Evaluation
from rest_api.common import helper, transaction
from rest_api.workflow import general, security_messaging
from rest_api.workflow.errors import ApiBadRequest, ApiInternalError
import logging
import requests
from rest_api.GeneralTool import GeneralTool
import datetime


EVALUATION_BP = Blueprint('evaluations')
_client_type_=1

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)

@EVALUATION_BP.get('evaluations')
async def get_evaluation_by_patient(request):
    """Fetches complete details of all Accounts in state"""
    idcard_viewer = request.headers['idcard_viewer']
    idcard_patient = request.headers['idcard_patient']

    headers = {'Content-Type': 'application/json'}
    dataParty = {"usernames": {"doctor": idcard_viewer, "patient": idcard_patient}}
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

        evaluation_record_id = '{}|{}'.format(patient_pub_key, idcard_patient)
        evaluations_lst = await security_messaging.get_recordowner(request.app.config.VAL_CONN,
                                                                   evaluation_record_id)  # Extracting the recordID information

        if doctor_pub_key!=patient_pub_key:
            consent_id = evaluations_lst.consent[doctor_pub_key]

            LOGGER.warning("CONSENT ID: " + str(consent_id))
            consent = await security_messaging.get_consent_patient_doctor(request.app.config.VAL_CONN, consent_id)

            if not general.validate_access(consent,[0,2]):
                return response.json(
                    body={'status': general.ERROR, "msg": "You have not access to this patient information."},
                    headers=general.get_response_headers())

        patient_id='{}|{}'.format(patient_pub_key, '02')
        party = await security_messaging.get_party(request.app.config.VAL_CONN, patient_pub_key) # Patient Main Information
        patient_info = await security_messaging.get_patient(request.app.config.VAL_CONN, patient_id) # Patient Main Information


        evaluations =[]


        for record_id in evaluations_lst.records:

            eval_info=await security_messaging.get_evaluation(request.app.config.VAL_CONN,
                                                                              record_id)
            evaluation_info = {}
            fields = [field.name for field in Evaluation.DESCRIPTOR.fields]
            for field in fields:
                evaluation_info[field]=getattr(eval_info, field)

            evaluations.append(evaluation_info)

        patient_list_json = []
        patient_list_json.append({
            'name': party.name,
            'lastname': party.lastname,
            'telephone': party.telephone,
            'birthdate': party.birthdate,
            'idcard': party.idcard,
            'sex': patient_info.biological_sex,
            'photo': patient_info.photo,
            'insurance': patient_info.current_insurance,
            'blood_type': patient_info.blood_type,
            "evaluations":evaluations
        })

        return response.json(body={'data': patient_list_json},
                             headers=general.get_response_headers())
    else:
        raise Exception("User with no patient registred.")


@EVALUATION_BP.post('evaluations')
async def register_new_evaluation(request):
    """Updates auth information for the authorized account"""
    # keyfile = common.get_keyfile(request.json.get['signer'])
    idcard_doctor = request.json.get('idcard_doctor')
    idcard_patient = request.json.get('idcard_patient')
    headers = {'Content-Type': 'application/json'}
    dataParty = {"usernames": {"doctor":idcard_doctor, "patient":idcard_patient}}
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
        evaluation_record_id = '{}|{}'.format(patient_pub_key, idcard_patient)
        evaluations_lst = await security_messaging.get_recordowner(request.app.config.VAL_CONN,
                                                                   evaluation_record_id)  # Extracting the recordID information
        consent_id = evaluations_lst.consent[doctor_pub_key]
        consent = await security_messaging.get_consent_patient_doctor(request.app.config.VAL_CONN, consent_id)

        if doctor_priv_key == patient_priv_key:
            return response.json(body={'status': general.ERROR, "msg": "A doctor cannot apply itself a consult."},
                                 headers=general.get_response_headers())

        elif not general.validate_access(consent, [1,2]):
            return response.json(body={'status': general.ERROR, "msg": "You have not access to this patient information."},
                                 headers=general.get_response_headers())


        record_id = '{}|{}|{}'.format(doctor_pub_key, patient_pub_key, int(datetime.datetime.now().timestamp() * 1000))

        batch_lst = []
        date_reg=general.date2julian()
        doctor_signer = GeneralTool().addSigner(GeneralTool().ParsePrivateKey(private_key_str=doctor_priv_key))

        fields = [field.name for field in Evaluation.DESCRIPTOR.fields]
        evaluation_info={}
        for field in fields:
            evaluation_info[field] = request.json.get(field) if field in request.json else " "
        evaluation_info['record_id']=record_id
        evaluation_info['patient_key']=patient_pub_key
        evaluation_info['doctor_key']=doctor_pub_key
        evaluation_info['date_time']=str(date_reg)
        doctor_info = await security_messaging.get_party(request.app.config.VAL_CONN, doctor_pub_key)
        evaluation_info['doctor_name']=doctor_info.name+" "+doctor_info.lastname


        evaluation_record_id = '{}|{}'.format(patient_pub_key, idcard_patient)
        evaluations_lst = await security_messaging.get_recordowner(request.app.config.VAL_CONN, evaluation_record_id)  # Extracting the recordID information
        LOGGER.debug("records: "+str(evaluations_lst))
        records=[record_id] # This is like this because when the system update if you dont want to add all the information just send it the necesary
        # In other words, I do not know how to add just the last data and I made this 'force'



        evaluation_txn = transaction.add_evaluation(
            txn_signer=doctor_signer,
            batch_signer=doctor_signer,
            evaluation_info=evaluation_info)

        batch_lst.append(evaluation_txn)




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
        batch_lst=[]

        patient_signer = GeneralTool().addSigner(GeneralTool().ParsePrivateKey(private_key_str=patient_priv_key))
        record_patient_txn = transaction.update_record_patient(
            txn_signer=patient_signer,
            batch_signer=patient_signer,
            record_id=evaluation_record_id,
            record_owner=patient_pub_key,
            records=records,
            consent={doctor_pub_key:consent_id}
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


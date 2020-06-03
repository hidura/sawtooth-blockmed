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

# from sawtooth_sdk.protobuf import client_batch_submit_pb2
import logging

from sawtooth_rest_api.protobuf import client_state_pb2
from sawtooth_rest_api.protobuf import validator_pb2

# from rest_api.common.protobuf import payload_pb2
from rest_api.common import helper
from rest_api.common.protobuf.payload_pb2 import CreateDoctor, CreatePatient, \
    Party, Evaluation, RecordOwner, ConsentDocPat

from rest_api.workflow import messaging
from rest_api.workflow.errors import ApiForbidden, ApiUnauthorized, ApiBadRequest

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)


async def _send(conn, timeout, batches):
    await messaging.send(conn, timeout, batches)


async def check_batch_status(conn, batch_ids):
    await messaging.check_batch_status(conn, batch_ids)


async def get_state_by_address(conn, address_suffix):
    status_request = client_state_pb2.ClientStateListRequest(address=address_suffix)
    validator_response = await conn.send(
        validator_pb2.Message.CLIENT_STATE_LIST_REQUEST,
        status_request.SerializeToString())

    status_response = client_state_pb2.ClientStateListResponse()
    status_response.ParseFromString(validator_response.content)
    # resp = status_response

    return status_response  # resp.entries

async def add_doctor(conn, timeout, batches):
    await _send(conn, timeout, batches)


async def add_evaluation(conn, timeout, batches):
    await _send(conn, timeout, batches)


async def add_patient(conn, timeout, batches):
    await _send(conn, timeout, batches)


async def get_patients(conn, client_key):
    patient_list = {}
    list_patient_address = helper.make_patient_list_address()
    LOGGER.debug('Clients ' + str(list_patient_address))
    # Get Consent
    patient_list_resources = await messaging.get_state_by_address(conn, list_patient_address)
    for entity in patient_list_resources.entries:
        pat = CreatePatient()
        pat.ParseFromString(entity.data)

        patient_list[entity.address] = pat
        LOGGER.debug('patient: ' + str(pat))

    return patient_list



async def get_doctor(conn, doctor_key):
    list_patient_address = helper.make_doctor_address(doctor_key)
    patient_resources = await messaging.get_state_by_address(conn, list_patient_address)
    for entity in patient_resources.entries:
        lt = CreateDoctor()
        lt.ParseFromString(entity.data)
        return lt
    raise ApiBadRequest("No such patient exist: " + str(doctor_key))

async def get_evaluation(conn, record_id):
    list_patient_address = helper.make_evaluation_address(record_id)
    evaluation_resources = await messaging.get_state_by_address(conn, list_patient_address)
    for entity in evaluation_resources.entries:
        lt = Evaluation()
        lt.ParseFromString(entity.data)
        return lt
    raise ApiBadRequest("No such patient exist: " + str(record_id))


async def get_patient(conn, party_key):
    list_patient_address = helper.make_patient_address(party_key)
    patient_resources = await messaging.get_state_by_address(conn, list_patient_address)
    for entity in patient_resources.entries:
        lt = CreatePatient()
        lt.ParseFromString(entity.data)
        return lt
    raise ApiBadRequest("No such patient exist: " + str(party_key))

async def get_party(conn, patient_key):
    list_patient_address = helper.make_party_address(patient_key)
    patient_resources = await messaging.get_state_by_address(conn, list_patient_address)
    for entity in patient_resources.entries:
        lt = Party()
        lt.ParseFromString(entity.data)
        return lt
    raise ApiBadRequest("No such entity exist: " + str(patient_key))

async def get_consent_patient_doctor(conn, recordid):
    list_patient_address = helper.make_record_patient_doctor_conset_address(recordid)
    consent = await messaging.get_state_by_address(conn, list_patient_address)

    LOGGER.debug("CONSENT RECIEN SACADO " + str(consent))
    for entity in reversed(consent.entries):
        lt = ConsentDocPat()
        lt.ParseFromString(entity.data)
        return lt
    raise ApiBadRequest("No such entity exist: " + str(recordid))

async def get_recordowner(conn, recordid):
    list_patient_address = helper.make_record_patient_address(recordid)
    recordowner = await messaging.get_state_by_address(conn, list_patient_address)
    for entity in recordowner.entries:
        lt = RecordOwner()
        lt.ParseFromString(entity.data)
        return lt
    raise ApiBadRequest("No such entity exist: " + str(recordid))


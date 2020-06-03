import hashlib
import random
import time
import logging
from sawtooth_sdk.protobuf.batch_pb2 import BatchHeader, Batch
from sawtooth_sdk.protobuf.transaction_pb2 import Transaction, TransactionHeader

from . import helper as helper
from .protobuf.payload_pb2 import Claim, TransactionPayload, CreateDoctor, CreatePatient, Clinic, CreateLab, \
    AddLabTest, AddPulse, Party, Evaluation, RecordOwner, ConsentDocPat

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)


def _make_transaction(payload, inputs, outputs, txn_signer, batch_signer):
    txn_header_bytes, signature = _transaction_header(txn_signer, batch_signer, inputs, outputs, payload)

    txn = Transaction(
        header=txn_header_bytes,
        header_signature=signature,
        payload=payload.SerializeToString()
    )

    return txn

def make_batch_and_id(transactions, batch_signer):
    batch_header_bytes, signature = _batch_header(batch_signer, transactions)

    batch = Batch(
        header=batch_header_bytes,
        header_signature=signature,
        transactions=transactions
    )

    return batch, batch.header_signature

def _transaction_header(txn_signer, batch_signer, inputs, outputs, payload):
    txn_header_bytes = TransactionHeader(
        family_name=helper.TP_FAMILYNAME,
        family_version=helper.TP_VERSION,
        inputs=inputs,
        outputs=outputs,
        signer_public_key=txn_signer.get_public_key().as_hex(),  # signer.get_public_key().as_hex(),
        # In this example, we're signing the batch with the same private key,
        # but the batch can be signed by another party, in which case, the
        # public key will need to be associated with that key.
        batcher_public_key=batch_signer.get_public_key().as_hex(),  # signer.get_public_key().as_hex(),
        # In this example, there are no dependencies.  This list should include
        # an previous transaction header signatures that must be applied for
        # this transaction to successfully commit.
        # For example,
        # dependencies=['540a6803971d1880ec73a96cb97815a95d374cbad5d865925e5aa0432fcf1931539afe10310c122c5eaae15df61236079abbf4f258889359c4d175516934484a'],
        dependencies=[],
        nonce=random.random().hex().encode(),
        payload_sha512=hashlib.sha512(payload.SerializeToString()).hexdigest()
    ).SerializeToString()

    signature = txn_signer.sign(txn_header_bytes)
    return txn_header_bytes, signature


def _batch_header(batch_signer, transactions):
    batch_header_bytes = BatchHeader(
        signer_public_key=batch_signer.get_public_key().as_hex(),
        transaction_ids=[txn.header_signature for txn in transactions],
    ).SerializeToString()

    signature = batch_signer.sign(batch_header_bytes)

    return batch_header_bytes, signature


def create_doctor(txn_signer, batch_signer, doctor_info):
    LOGGER.debug('doctor_pkey: ' + str(doctor_info['doctor_key']))
    doctor_hex = helper.make_doctor_address(doctor_pkey=doctor_info['doctor_key'])
    LOGGER.debug('doctor_hex: ' + str(doctor_hex))
    # permissions = [payload_pb2.Permission(type=payload_pb2.Permission.READ_DOCTOR),
    #                payload_pb2.Permission(type=payload_pb2.Permission.READ_OWN_DOCTOR)]

    doctor = CreateDoctor(
        doctor_key=doctor_info['doctor_key'],
        party_key=doctor_info['party_key'],
        bio=doctor_info['bio'],
        photo=doctor_info['photo'],
        main_speciality=doctor_info['main_speciality'])

    payload = TransactionPayload(
        payload_type=TransactionPayload.CREATE_DOCTOR,
        create_doctor=doctor)

    return _make_transaction(
        payload=payload,
        inputs=[doctor_hex],
        outputs=[doctor_hex],
        txn_signer=txn_signer,
        batch_signer=batch_signer)


def create_party(txn_signer, batch_signer, party_info):
    patient_pkey = txn_signer.get_public_key().as_hex()
    LOGGER.debug('patient_pkey: ' + str(patient_pkey))
    patient_hex = helper.make_party_address(party_pkey=patient_pkey)
    LOGGER.debug('patient_hex: ' + str(patient_hex))
    party_details = {}
    fields = [field.name for field in Party.DESCRIPTOR.fields]
    for field in fields:
        party_details[field] = party_info[field]
    party = Party(**party_details)

    payload = TransactionPayload(
        payload_type = TransactionPayload.CREATE_PARTY,
        create_party = party)

    LOGGER.debug('payload: ' + str(payload))

    return _make_transaction(
        payload=payload,
        inputs=[patient_hex],
        outputs=[patient_hex],
        txn_signer=txn_signer,
        batch_signer=batch_signer)


def create_patient(txn_signer, batch_signer, patient_info):
    patient_pkey = patient_info['record_id']
    patient_hex = helper.make_patient_address(patient_pkey=patient_pkey)
    # permissions = [payload_pb2.Permission(type=payload_pb2.Permission.READ_PATIENT),
    #                payload_pb2.Permission(type=payload_pb2.Permission.READ_OWN_PATIENT)]
    patient_details={}
    fields = [field.name for field in CreatePatient.DESCRIPTOR.fields]
    for field in fields:
        patient_details[field]=patient_info[field]

    patient_data = CreatePatient(**patient_details)

    payload = TransactionPayload(
        payload_type=TransactionPayload.CREATE_PATIENT,
        create_patient=patient_data)


    return _make_transaction(
        payload=payload,
        inputs=[patient_hex],
        outputs=[patient_hex],
        txn_signer=txn_signer,
        batch_signer=batch_signer)


def add_evaluation(txn_signer, batch_signer, evaluation_info):
    record_hex = helper.make_evaluation_address(evaluation_pkey=evaluation_info['record_id'])
    patient_hex = helper.make_evaluation_patient_address(patient_pkey=evaluation_info['patient_key'])
    doctor_hex = helper.make_evaluation_doctor_address(doctor_pkey=evaluation_info['doctor_key'])

    evaluation_data = {}
    fields = [field.name for field in Evaluation.DESCRIPTOR.fields]
    for field in fields:
        evaluation_data[field] = evaluation_info[field]


    evaluation = Evaluation(**evaluation_data)


    payload = TransactionPayload(
        payload_type=TransactionPayload.CREATE_EVALUATION,
        create_evaluation=evaluation)



    return _make_transaction(
        payload=payload,
        inputs=[record_hex, doctor_hex, patient_hex],
        outputs=[record_hex, doctor_hex, patient_hex],
        txn_signer=txn_signer,
        batch_signer=batch_signer)

def create_clinic(txn_signer, batch_signer, name):
    clinic_pkey = txn_signer.get_public_key().as_hex()
    LOGGER.debug('clinic_pkey: ' + str(clinic_pkey))
    inputs = outputs = helper.make_clinic_address(clinic_pkey=clinic_pkey)
    LOGGER.debug('inputs: ' + str(inputs))
    # permissions = [payload_pb2.Permission(type=payload_pb2.Permission.READ_CLINIC),
    #                payload_pb2.Permission(type=payload_pb2.Permission.READ_OWN_CLINIC)]
    clinic = Clinic(
        public_key=clinic_pkey,
        name=name)

    payload = TransactionPayload(
        payload_type=TransactionPayload.CREATE_CLINIC,
        create_clinic=clinic)

    return _make_transaction(
        payload=payload,
        inputs=[inputs],
        outputs=[outputs],
        txn_signer=txn_signer,
        batch_signer=batch_signer)

def add_record_patient(txn_signer, batch_signer, record_id, record_owner):
    record_hex = helper.make_record_patient_address(record_id)

    recordowner = RecordOwner(
        record_id=record_id,
        owner=record_owner,
        records=[],
        consent={}
    )


    payload = TransactionPayload(
        payload_type=TransactionPayload.CREATE_RECORDOWNER,
        create_record=recordowner)

    return _make_transaction(
        payload=payload,
        inputs=[record_hex],
        outputs=[record_hex],
        txn_signer=txn_signer,
        batch_signer=batch_signer)




def update_record_patient(txn_signer, batch_signer, record_id, record_owner, records, consent):
    record_hex = helper.make_record_patient_address(record_id)

    recordowner = RecordOwner(
        record_id=record_id,
        owner=record_owner,
        records=records,
        consent=consent
    )


    payload = TransactionPayload(
        payload_type=TransactionPayload.UPDATE_RECORDOWNER,
        update_record=recordowner)

    return _make_transaction(
        payload=payload,
        inputs=[record_hex],
        outputs=[record_hex],
        txn_signer=txn_signer,
        batch_signer=batch_signer)


def add_consent_patient(txn_signer, batch_signer, consent_info):
    record_hex = helper.make_record_patient_doctor_conset_address(consent_info['consent_id'])


    consentpatient = ConsentDocPat(
        consent_id=consent_info['consent_id'],
        patient_key=consent_info['patient_key'],
        doctor_key=consent_info['doctor_key'],
        expire_date=str(consent_info['time_exp']),
        permission=str(consent_info['permission'])
    )

    payload = TransactionPayload(
        payload_type=TransactionPayload.CREATE_CONSENT,
        create_consent=consentpatient)

    return _make_transaction(
        payload=payload,
        inputs=[record_hex],
        outputs=[record_hex],
        txn_signer=txn_signer,
        batch_signer=batch_signer)

import hashlib
import time

DISTRIBUTION_NAME = 'sawtooth-healthcare'

DEFAULT_URL = 'http://127.0.0.1:8008'

TP_FAMILYNAME = 'healthcare'
TP_VERSION = '1.0'

CLINIC_ENTITY_CODE = '01'
DOCTOR_ENTITY_CODE = '02'
PATIENT_ENTITY_CODE = '03'
PARTY_ENTITY_CODE = '09'
EVALUATION_ENTITY_CODE = '10'
RECORD_PATIENT_ENTITY_CODE = '11'


PATIENT_DOCTOR_PERMISSION_CODE = "40"

PATIENT_LAB_TEST__RELATION_CODE = "51"
LAB_TEST_PATIENT__RELATION_CODE = "52"

PATIENT_PULSE__RELATION_CODE = "61"
PULSE_PATIENT__RELATION_CODE = "62"

PATIENT_CLAIM__RELATION_CODE = "71"
CLAIM_PATIENT__RELATION_CODE = "72"

CLINIC_CLAIM__RELATION_CODE = "81"
CLAIM_CLINIC__RELATION_CODE = "82"


def _hash(identifier):
    return hashlib.sha512(identifier.encode('utf-8')).hexdigest()


TP_PREFFIX_HEX6 = _hash(TP_FAMILYNAME)[0:6]


def make_party_address(party_pkey):
    return TP_PREFFIX_HEX6 + PARTY_ENTITY_CODE + _hash(party_pkey)[:62]


def make_party_list_address():
    return TP_PREFFIX_HEX6 + PARTY_ENTITY_CODE



def make_clinic_address(clinic_pkey):
    return TP_PREFFIX_HEX6 + CLINIC_ENTITY_CODE + _hash(clinic_pkey)[:62]


def make_clinic_list_address():
    return TP_PREFFIX_HEX6 + CLINIC_ENTITY_CODE


def make_doctor_address(doctor_pkey):
    return TP_PREFFIX_HEX6 + DOCTOR_ENTITY_CODE + _hash(doctor_pkey)[:62]


def make_doctor_list_address():
    return TP_PREFFIX_HEX6 + DOCTOR_ENTITY_CODE


def make_patient_address(patient_pkey):
    return TP_PREFFIX_HEX6 + PATIENT_ENTITY_CODE + _hash(patient_pkey)[:62]


def make_patient_list_address():
    return TP_PREFFIX_HEX6 + PATIENT_ENTITY_CODE

#Evaluation entity

def make_evaluation_address(evaluation_pkey):
    return TP_PREFFIX_HEX6 + EVALUATION_ENTITY_CODE + _hash(evaluation_pkey)[:62]

def make_evaluation_doctor_address(doctor_pkey):
    return TP_PREFFIX_HEX6 + EVALUATION_ENTITY_CODE+ DOCTOR_ENTITY_CODE + _hash(doctor_pkey)[:60]


def make_evaluation_patient_address(patient_pkey):
    return TP_PREFFIX_HEX6 + EVALUATION_ENTITY_CODE+ PATIENT_ENTITY_CODE + _hash(patient_pkey)[:60]


def make_evaluation_list_address():
    return TP_PREFFIX_HEX6 + EVALUATION_ENTITY_CODE


def make_evaluation_patient_list_address():
    return TP_PREFFIX_HEX6 + EVALUATION_ENTITY_CODE+ PATIENT_ENTITY_CODE


def make_evaluation_doctor_list_address():
    return TP_PREFFIX_HEX6 + EVALUATION_ENTITY_CODE+DOCTOR_ENTITY_CODE


# Record Entity
def make_record_patient_address(patient_pkey):
    return TP_PREFFIX_HEX6 + RECORD_PATIENT_ENTITY_CODE + _hash(patient_pkey)[:62]

# Record Entity
def make_record_patient_list_address():
    return TP_PREFFIX_HEX6 + RECORD_PATIENT_ENTITY_CODE


# Record Entity
def make_record_patient_doctor_conset_address(patient_pkey):
    return TP_PREFFIX_HEX6 + PATIENT_ENTITY_CODE+DOCTOR_ENTITY_CODE+PATIENT_DOCTOR_PERMISSION_CODE + _hash(patient_pkey)[:58]

# Record Entity
def make_record_patient_doctor_conset_list_address():
    return TP_PREFFIX_HEX6 + PATIENT_ENTITY_CODE+DOCTOR_ENTITY_CODE+PATIENT_DOCTOR_PERMISSION_CODE



def get_current_timestamp():
    return int(round(time.time() * 1000))


from processor.common import helper
from processor.common.protobuf import payload_pb2
import logging

# from processor.common.protobuf.payload_pb2 import Claim

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)


class HealthCareState(object):
    TIMEOUT = 3

    def __init__(self, context):
        """Constructor.
        Args:
            context (sawtooth_sdk.processor.context.Context): Access to
                validator state from within the transaction processor.
        """

        self._context = context

    def create_clinic(self, clinic):
        op = self._load_clinic(public_key=clinic.public_key)

        if op is None:
            self._store_clinic(clinic)

    def create_doctor(self, doctor):
        op = self._load_doctor(doctor_key=doctor.doctor_key)

        if op is None:
            self._store_doctor(doctor)

    def create_patient(self, patient):
        op = self._load_patient(patient_key=patient.record_id)

        if op is None:
            self._store_patient(patient)

    def create_party(self, party):
        op = self._load_party(public_key=party.public_key)

        if op is None:
            self._store_party(party)

    def create_lab(self, lab):
        op = self._load_lab(public_key=lab.public_key)

        if op is None:
            self._store_lab(lab)

    def create_evaluation(self, evaluation):
        op = self._load_evaluation(record_id=evaluation.record_id)

        if op is None:
            self._store_evaluation(evaluation)

    def create_evaluation_record(self, evaluation):

        op = self._load_evaluation_record(record_id=evaluation.record_id)

        if op is None:
            self._store_evaluation_record(evaluation)


    def create_consent(self, consent):

        op = self._load_consent(consent_id=consent.consent_id)

        if op is None:
            self._store_consent(consent)


    def assign_doctor(self, claim_id, clinic_pkey, description, event_time):
        self._store_event(claim_id=claim_id, clinic_pkey=clinic_pkey, description=description,
                          event_time=event_time, event=payload_pb2.ActionOnClaim.ASSIGN)

    def first_visit(self, claim_id, clinic_pkey, description, event_time):
        self._store_event(claim_id=claim_id, clinic_pkey=clinic_pkey, description=description,
                          event_time=event_time, event=payload_pb2.ActionOnClaim.FIRST_VISIT)

    def pass_tests(self, claim_id, clinic_pkey, description, event_time):
        self._store_event(claim_id=claim_id, clinic_pkey=clinic_pkey, description=description,
                          event_time=event_time, event=payload_pb2.ActionOnClaim.PASS_TEST)

    def attend_procedures(self, claim_id, clinic_pkey, description, event_time):
        self._store_event(claim_id=claim_id, clinic_pkey=clinic_pkey, description=description,
                          event_time=event_time, event=payload_pb2.ActionOnClaim.PASS_PROCEDURE)

    def eat_pills(self, claim_id, clinic_pkey, description, event_time):
        self._store_event(claim_id=claim_id, clinic_pkey=clinic_pkey, description=description,
                          event_time=event_time, event=payload_pb2.ActionOnClaim.EAT_PILLS)

    def next_visit(self, claim_id, clinic_pkey, description, event_time):
        self._store_event(claim_id=claim_id, clinic_pkey=clinic_pkey, description=description,
                          event_time=event_time, event=payload_pb2.ActionOnClaim.NEXT_VISIT)

    def add_lab_test(self, lab_test):
        self._store_lab_test(lab_test=lab_test)

    def add_evaluation(self, evaluation):
        self._store_evaluation(evaluation=evaluation)

    def add_pulse(self, pulse):
        self._store_pulse(pulse=pulse)

    def create_claim(self, claim):
        self._store_claim(claim=claim)

    def update_claim(self, claim):
        self._update_claim(claim=claim)

    def update_evaluation_record(self, evaluation_record):
        self._update_evaluation_record(evaluation_record=evaluation_record)

    def close_claim(self, claim):
        self._close_claim(claim=claim)

    def get_consent(self, consent_id):
        consent = self._load_consent(consent_id=consent_id)
        return consent

    def get_evaluation(self, record_id):
        evaluation = self._load_evaluation(record_id=record_id)
        return evaluation

    def get_evaluation_record(self, record_id):
        # This is the storage of ids of all the evaluation records
        evaluation_record = self._load_evaluation_record(record_id=record_id)
        return evaluation_record

    def get_clinic(self, public_key):
        clinic = self._load_clinic(public_key=public_key)
        return clinic

    def get_doctor(self, doctor_key):
        doctor = self._load_doctor(doctor_key=doctor_key)
        return doctor

    def get_party(self, public_key):
        party = self._load_party(public_key=public_key)
        return party

    def get_patient(self, patient_key):
        patient = self._load_patient(patient_key=patient_key)
        return patient

    def get_lab(self, public_key):
        lab = self._load_lab(public_key=public_key)
        return lab

    def get_claim(self, claim_id, clinic_pkey):
        od = self._load_claim(claim_id=claim_id, clinic_pkey=clinic_pkey)
        return od

    def get_claim2(self, claim_id):
        od = self._load_claim2(claim_id=claim_id)
        return od

    def _load_clinic(self, public_key):
        clinic = None
        clinic_hex = helper.make_clinic_address(public_key)
        state_entries = self._context.get_state(
            [clinic_hex],
            timeout=self.TIMEOUT)
        if state_entries:
            clinic = payload_pb2.CreateClinic()
            clinic.ParseFromString(state_entries[0].data)
        return clinic

    def _load_doctor(self, doctor_key):
        doctor = None
        doctor_hex = helper.make_doctor_address(doctor_key)
        state_entries = self._context.get_state(
            [doctor_hex],
            timeout=self.TIMEOUT)
        if state_entries:
            doctor = payload_pb2.CreateDoctor()
            doctor.ParseFromString(state_entries[0].data)
        return doctor

    def _load_party(self, public_key):
        party = None
        party_hex = helper.make_party_address(public_key)
        state_entries = self._context.get_state(
            [party_hex],
            timeout=self.TIMEOUT)
        if state_entries:
            party = payload_pb2.CreateParty()
            party.ParseFromString(state_entries[0].data)
        return party


    def _load_consent(self, consent_id):
        consent = None
        consent_hex = helper.make_record_patient_doctor_conset_address(consent_id)
        state_entries = self._context.get_state(
            [consent_hex],
            timeout=self.TIMEOUT)
        if state_entries:
            consent = payload_pb2.ConsentDocPat()
            consent.ParseFromString(state_entries[0].data)
        return consent


    def _load_evaluation(self, record_id):
        evaluation = None
        evaluation_hex = helper.make_evaluation_address(record_id)
        state_entries = self._context.get_state(
            [evaluation_hex],
            timeout=self.TIMEOUT)
        if state_entries:
            evaluation = payload_pb2.Evaluation()
            evaluation.ParseFromString(state_entries[0].data)
        return evaluation


    def _load_evaluation_record(self, record_id):
        evaluation_record = None
        evaluation_record_hex = helper.make_record_patient_address(record_id)
        state_entries = self._context.get_state(
            [evaluation_record_hex],
            timeout=self.TIMEOUT)
        if state_entries:
            evaluation_record = payload_pb2.RecordOwner()
            evaluation_record.ParseFromString(state_entries[0].data)
        return evaluation_record

    def _load_lab(self, public_key):
        lab = None
        lab_hex = helper.make_lab_address(public_key)
        state_entries = self._context.get_state(
            [lab_hex],
            timeout=self.TIMEOUT)
        if state_entries:
            lab = payload_pb2.CreateLab()
            lab.ParseFromString(state_entries[0].data)
        return lab

    def _load_patient(self, patient_key):
        patient = None
        patient_hex = helper.make_patient_address(patient_pkey=patient_key)
        state_entries = self._context.get_state(
            [patient_hex],
            timeout=self.TIMEOUT)

        if state_entries:
            patient = payload_pb2.CreatePatient()
            patient.ParseFromString(state_entries[0].data)
        return patient


    def _load_claim2(self, claim_id):
        claim = None
        claim_hex = helper.make_claim_address(claim_id)
        state_entries = self._context.get_state(
            [claim_hex],
            timeout=self.TIMEOUT)
        if state_entries:
            claim = payload_pb2.Claim()
            claim.ParseFromString(state_entries[0].data)
        return claim

    def _load_claim(self, claim_id, clinic_pkey):
        claim = None
        claim_hex = [] if clinic_pkey is None and claim_id is None \
            else [helper.make_claim_address(claim_id, clinic_pkey)]
        state_entries = self._context.get_state(
            claim_hex,
            timeout=self.TIMEOUT)
        if state_entries:
            claim = payload_pb2.CreateClaim()
            claim.ParseFromString(state_entries[0].data)
        return claim

    def _store_clinic(self, clinic):
        address = helper.make_clinic_address(clinic.public_key)


        state_data = clinic.SerializeToString()
        self._context.set_state(
            {address: state_data},
            timeout=self.TIMEOUT)

    def _store_consent(self, consent):
        address = helper.make_record_patient_doctor_conset_address(consent.consent_id)


        state_data = consent.SerializeToString()
        self._context.set_state(
            {address: state_data},
            timeout=self.TIMEOUT)


    def _store_evaluation_record(self, evaluation_record):
        address = helper.make_record_patient_address(evaluation_record.record_id)

        state_data = evaluation_record.SerializeToString()
        self._context.set_state(
            {address: state_data},
            timeout=self.TIMEOUT)

    def _update_evaluation_record(self, evaluation_record):
        evaluation_address = helper.make_record_patient_address(evaluation_record.record_id)
        evaluation_data = evaluation_record.SerializeToString()
        states = {
            evaluation_address: evaluation_data
        }
        LOGGER.debug("_update_evaluation_record: " + str(states))
        self._context.set_state(
            states,
            timeout=self.TIMEOUT)


    def _store_evaluation(self, evaluation):
        evaluation_address = helper.make_evaluation_address(evaluation.record_id)
        doctor_hex = helper.make_evaluation_doctor_address(evaluation.doctor_key)
        patient_hex = helper.make_evaluation_patient_address(evaluation.patient_key)

        LOGGER.debug('patient_hex in store evaluation: ' + str(patient_hex))
        state_data = evaluation.SerializeToString()
        LOGGER.debug('Store Data: ' + str(state_data))
        states = {
            evaluation_address: state_data,
            doctor_hex: str.encode(evaluation.doctor_key),
            patient_hex: str.encode(evaluation.patient_key)
        }
        self._context.set_state(
            states,
            timeout=self.TIMEOUT)


    def _store_doctor(self, doctor):
        address = helper.make_doctor_address(doctor.doctor_key)

        state_data = doctor.SerializeToString()
        self._context.set_state(
            {address: state_data},
            timeout=self.TIMEOUT)

    def _store_patient(self, patient):
        address = helper.make_patient_address(patient.record_id)

        state_data = patient.SerializeToString()
        self._context.set_state(
            {address: state_data},
            timeout=self.TIMEOUT)

    def _store_party(self, party):
        address = helper.make_party_address(party.public_key)

        state_data = party.SerializeToString()
        self._context.set_state(
            {address: state_data},
            timeout=self.TIMEOUT)

    def _store_lab(self, lab):
        address = helper.make_lab_address(lab.public_key)
        state_data = lab.SerializeToString()
        self._context.set_state(
            {address: state_data},
            timeout=self.TIMEOUT)

    def _store_event(self, claim_id, clinic_pkey, description, event_time, event):
        address = helper.make_event_address(claim_id, clinic_pkey, event_time)
        ev = payload_pb2.ActionOnClaim()
        ev.claim_id = claim_id
        ev.clinic_pkey = clinic_pkey
        ev.description = description
        ev.event_time = event_time
        ev.event = event

        state_data = ev.SerializeToString()
        self._context.set_state(
            {address: state_data},
            timeout=self.TIMEOUT)

    def _store_lab_test(self, lab_test):
        lab_test_address = helper.make_lab_test_address(lab_test.id)
        lab_test_patient_relation_address = helper.make_lab_test_patient__relation_address(lab_test.id,
                                                                                           lab_test.client_pkey)
        patient_lab_test_relation_address = helper.make_patient_lab_test__relation_address(lab_test.client_pkey,
                                                                                           lab_test.id)

        lab_test_data = lab_test.SerializeToString()
        states = {
            lab_test_address: lab_test_data,
            lab_test_patient_relation_address: str.encode(lab_test.client_pkey),
            patient_lab_test_relation_address: str.encode(lab_test.id)
        }
        LOGGER.debug("_store_lab_test: " + str(states))
        self._context.set_state(
            states,
            timeout=self.TIMEOUT)


    def _update_claim(self, claim):
        claim_address = helper.make_claim_address(claim.id)
        claim_data = claim.SerializeToString()
        states = {
            claim_address: claim_data
        }
        LOGGER.debug("_update_claim: " + str(states))
        self._context.set_state(
            states,
            timeout=self.TIMEOUT)

    def _close_claim(self, claim):
        claim_address = helper.make_claim_address(claim.id)
        claim_data = claim.SerializeToString()
        states = {
            claim_address: claim_data
        }
        LOGGER.debug("_close_claim: " + str(states))
        self._context.set_state(
            states,
            timeout=self.TIMEOUT)

    def _store_claim(self, claim):
        claim_address = helper.make_claim_address(claim.id)
        claim_patient_relation_address = helper.make_claim_patient__relation_address(claim.id,
                                                                                     claim.client_pkey)
        patient_claim_relation_address = helper.make_patient_claim__relation_address(claim.client_pkey,
                                                                                     claim.id)

        claim_data = claim.SerializeToString()
        states = {
            claim_address: claim_data,
            claim_patient_relation_address: str.encode(claim.client_pkey),
            patient_claim_relation_address: str.encode(claim.id)
        }
        LOGGER.debug("_store_claim: " + str(states))
        self._context.set_state(
            states,
            timeout=self.TIMEOUT)

    def _store_pulse(self, pulse):
        pulse_address = helper.make_pulse_address(pulse.id)
        pulse_patient_relation_address = helper.make_pulse_patient__relation_address(pulse.id,
                                                                                     pulse.client_pkey)
        patient_pulse_relation_address = helper.make_patient_pulse__relation_address(pulse.client_pkey,
                                                                                     pulse.id)

        pulse_data = pulse.SerializeToString()
        states = {
            pulse_address: pulse_data,
            pulse_patient_relation_address: str.encode(pulse.client_pkey),
            patient_pulse_relation_address: str.encode(pulse.id)
        }
        LOGGER.debug("_store_pulse: " + str(states))
        # state_data = p.SerializeToString()
        self._context.set_state(
            states,
            timeout=self.TIMEOUT)

from sanic import Blueprint
from sanic import response

# from rest_api.common.protobuf import payload_pb2
from rest_api.common import transaction
from rest_api.workflow import general, security_messaging
from rest_api.workflow.errors import ApiInternalError, ApiBadRequest
import requests
import logging
import hashlib
from rest_api.GeneralTool import GeneralTool

PATIENTS_BP = Blueprint('patients')
_client_type_=2


logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)


@PATIENTS_BP.get('patients')
async def get_patient_basic_info(request):
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

        patientKey='{}|{}'.format(public_key, '0'+str(_client_type_))


        patient = await security_messaging.get_patient(request.app.config.VAL_CONN, patientKey)
        patient_list_json = []
        patient_list_json.append({
            'name': party.name,
            'lastname':party.lastname,
            'telephone':party.telephone,
            'birthdate':party.birthdate,
            'idcard':party.idcard,
            'sex': patient.biological_sex,
            'photo': patient.photo,
            'insurance': patient.current_insurance,
            'blood_type':patient.blood_type
        })

        return response.json(body={'data': patient_list_json},
                             headers=general.get_response_headers())
    else:
        raise Exception("User with no patient registred.")

@PATIENTS_BP.post('patients')
async def register_new_patient(request):
    """Updates auth information for the authorized account"""
    # keyfile = common.get_keyfile(request.json.get['signer'])
    required_fields = ['first_name', 'last_name', 'idcard_type','idcard']
    general.validate_fields(required_fields, request.json)

    name = request.json.get('first_name')
    surname = request.json.get('last_name')
    idcard = request.json.get('idcard')
    idcard_type = int(request.json.get('idcard_type'))


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
    batch_lst=[]
    if response_load.status_code != 200:
        raise Exception("There was a problem communicating with the validator.")
    elif response_load.status_code == 200 and 'private_key' in GeneralTool().parseFromJSON(response_load.content.decode()):
        keys = GeneralTool().parseFromJSON(response_load.content.decode())
        privatekey=keys['private_key']
        public_key=keys['public_key']
    elif response_load.status_code == 200 and 'private_key' not in GeneralTool().parseFromJSON(
            response_load.content.decode()):

        party_txn, privatekey, public_key = general.addParty(party_info, _client_type_)
        batch_lst.append(party_txn)
    else:
        raise Exception("There was a problem communicating with the validator.")

    patient_signer = GeneralTool().addSigner(GeneralTool().ParsePrivateKey(private_key_str=privatekey))


    patientKey='{}|{}'.format(public_key, '0'+str(_client_type_))

    patient_info={'party_key':public_key,
                  'record_id':patientKey,
                  'biological_sex':request.json.get('biological_sex'),
                  "blood_type":request.json.get('blood_type') if 'blood_type' in request.json else " ",
                  "critical_info": request.json.get('critical_info') if 'critical_info' in
                                                                        request.json else " ",
                  "current_insurance":request.json.get('current_insurance') if 'current_insurance' in
                                                                        request.json else " ",
                  "disability_kind": request.json.get('disability_kind') if 'disability_kind' in
                                                                        request.json else " ",
                  "disabled_person": request.json.get('disability_kind') if 'disability_kind' in
                                                                        request.json else '0',
                  "familiar_antecedents": request.json.get('familiar_antecedents') if 'familiar_antecedents' in
                                                                        request.json else " ",
                  "general_info": request.json.get('general_info') if 'general_info' in
                                                                        request.json else " ",
                  "history_information": request.json.get('general_info') if 'general_info' in
                                                                        request.json else {},
                  "alcohol": request.json.get('alcohol') if 'alcohol' in request.json else '0',
                  "anticonceptive": request.json.get('anticonceptive')
                  if 'anticonceptive' in request.json else '0',
                  "car_child_safety": request.json.get('car_child_safety')
                  if 'car_child_safety' in request.json else '0',
                  "car_revision": request.json.get('car_revision')
                  if 'car_revision' in request.json else '0',
                  "car_seat_belt": request.json.get('car_seat_belt')
                  if 'car_seat_belt' in request.json else '0',
                  "coffee": request.json.get('coffee')
                  if 'coffee' in request.json else '0',
                  "diet": request.json.get('diet')
                  if 'diet' in request.json else '0',
                  "drug_iv": request.json.get('drug_iv')
                  if 'drug_iv' in request.json else '0',
                  "drug_usage": request.json.get('drug_usage')
                  if 'drug_usage' in request.json else '0',
                  "eats_alone": request.json.get('eats_alone')
                  if 'eats_alone' in request.json else '0',
                  "ex_alcoholic": request.json.get('ex_alcoholic')
                  if 'ex_alcoholic' in request.json else '0',
                  "ex_drug_addict": request.json.get('ex_drug_addict')
                  if 'ex_drug_addict' in request.json else '0',
                  "ex_smoker": request.json.get('ex_smoker')
                  if 'ex_smoker' in request.json else '0',
                  "exercise": request.json.get('exercise')
                  if 'exercise' in request.json else '0',
                  "helmet": request.json.get('helmet')
                  if 'helmet' in request.json else '0',
                  "home_safety": request.json.get('home_safety')
                  if 'home_safety' in request.json else '0',
                  "motorcycle_rider": request.json.get('motorcycle_rider')
                  if 'motorcycle_rider' in request.json else '0',
                  "prostitute": request.json.get('prostitute')
                  if 'prostitute' in request.json else '0',
                  "salt": request.json.get('salt')
                  if 'salt' in request.json else '0',
                  "second_hand_smoker": request.json.get('second_hand_smoker')
                  if 'second_hand_smoker' in request.json else '0',
                  "smoking": request.json.get('smoking')
                  if 'smoking' in request.json else '0',
                  "soft_drinks": request.json.get('soft_drinks')
                  if 'soft_drinks' in request.json else '0',
                  "traffic_laws": request.json.get('traffic_laws')
                  if 'traffic_laws' in request.json else '0',
                  "photo": request.json.get('photo')
                  if 'photo' in request.json else '/static/pictures/man.svg'
                  if request.json.get('biological_sex') == 'm' else '/static/pictures/woman.svg'
                  }

    patient_txn = transaction.create_patient(
        txn_signer=patient_signer,
        batch_signer=patient_signer,
        patient_info=patient_info
    )
    batch_lst.append(patient_txn)

    evaluation_record_id='{}|{}'.format(patient_info['party_key'], party_info['idcard'])
    record_patient_txn = transaction.add_record_patient(
        txn_signer=patient_signer,
        batch_signer=patient_signer,
        record_id=evaluation_record_id,
        record_owner=public_key
    )

    batch_lst.append(record_patient_txn)
    batch, batch_id = transaction.make_batch_and_id(batch_lst, patient_signer)



    await security_messaging.add_patient(
        request.app.config.VAL_CONN,
        request.app.config.TIMEOUT,
        [batch])


    # try:
    #     await security_messaging.check_batch_status(
    #         request.app.config.VAL_CONN, [batch_id])
    # except (ApiBadRequest, ApiInternalError) as err:
    #     # await auth_query.remove_auth_entry(
    #     #     request.app.config.DB_CONN, request.json.get('email'))
    #     raise err

    return response.json(body={'status': general.DONE},
                         headers=general.get_response_headers())


@PATIENTS_BP.get('patients/revoke/<doctor_pkey>')
async def revoke_access(request, doctor_pkey):
    """Updates auth information for the authorized account"""
    client_key = general.get_request_key_header(request)
    client_signer = general.get_signer(request, client_key)
    revoke_access_txn = consent_transaction.revoke_access(
        txn_signer=client_signer,
        batch_signer=client_signer,
        doctor_pkey=doctor_pkey)

    batch, batch_id = transaction.make_batch_and_id([revoke_access_txn], client_signer)

    await security_messaging.revoke_access(
        request.app.config.VAL_CONN,
        request.app.config.TIMEOUT,
        [batch], client_key)

    try:
        await security_messaging.check_batch_status(
            request.app.config.VAL_CONN, [batch_id])
    except (ApiBadRequest, ApiInternalError) as err:
        # await auth_query.remove_auth_entry(
        #     request.app.config.DB_CONN, request.json.get('email'))
        raise err

    return response.json(body={'status': general.DONE},
                         headers=general.get_response_headers())


@PATIENTS_BP.get('patients/grant/<doctor_pkey>')
async def grant_access(request, doctor_pkey):
    """Updates auth information for the authorized account"""
    client_key = general.get_request_key_header(request)
    client_signer = general.get_signer(request, client_key)
    grant_access_txn = consent_transaction.grant_access(
        txn_signer=client_signer,
        batch_signer=client_signer,
        doctor_pkey=doctor_pkey)

    batch, batch_id = transaction.make_batch_and_id([grant_access_txn], client_signer)

    await security_messaging.grant_access(
        request.app.config.VAL_CONN,
        request.app.config.TIMEOUT,
        [batch], client_key)

    try:
        await security_messaging.check_batch_status(
            request.app.config.VAL_CONN, [batch_id])
    except (ApiBadRequest, ApiInternalError) as err:
        # await auth_query.remove_auth_entry(
        #     request.app.config.DB_CONN, request.json.get('email'))
        raise err

    return response.json(body={'status': general.DONE},
                         headers=general.get_response_headers())

# @ACCOUNTS_BP.get('accounts/<key>')
# async def get_account(request, key):
#     """Fetches the details of particular Account in state"""
#     try:
#         auth_key = common.deserialize_auth_token(
#             request.app.config.SECRET_KEY,
#             request.token).get('public_key')
#     except (BadSignature, TypeError):
#         auth_key = None
#     account_resource = await accounts_query.fetch_account_resource(
#         request.app.config.DB_CONN, key, auth_key)
#     return response.json(account_resource)
#

# @ACCOUNTS_BP.patch('accounts')
# @authorized()
# async def update_account_info(request):
#     """Updates auth information for the authorized account"""
#     token = common.deserialize_auth_token(
#         request.app.config.SECRET_KEY, request.token)
#
#     update = {}
#     if request.json.get('password'):
#         update['hashed_password'] = bcrypt.hashpw(
#             bytes(request.json.get('password'), 'utf-8'), bcrypt.gensalt())
#     if request.json.get('email'):
#         update['email'] = request.json.get('email')
#
#     if update:
#         updated_auth_info = await auth_query.update_auth_info(
#             request.app.config.DB_CONN,
#             token.get('email'),
#             token.get('public_key'),
#             update)
#         new_token = common.generate_auth_token(
#             request.app.config.SECRET_KEY,
#             updated_auth_info.get('email'),
#             updated_auth_info.get('publicKey'))
#     else:
#         updated_auth_info = await accounts_query.fetch_account_resource(
#             request.app.config.DB_CONN,
#             token.get('public_key'),
#             token.get('public_key'))
#         new_token = request.token
#
#     return response.json(
#         {
#             'authorization': new_token,
#             'account': updated_auth_info
#         })

#
# def _create_account_dict(body, public_key):
#     keys = ['label', 'description', 'email']
#
#     account = {k: body[k] for k in keys if body.get(k) is not None}
#
#     account['publicKey'] = public_key
#     account['holdings'] = []
#
#     return account


# def _create_auth_dict(request, public_key, private_key):
#     auth_entry = {
#         'public_key': public_key,
#         'email': request.json['email']
#     }
#
#     auth_entry['encrypted_private_key'] = common.encrypt_private_key(
#         request.app.config.AES_KEY, public_key, private_key)
#     auth_entry['hashed_password'] = bcrypt.hashpw(
#         bytes(request.json.get('password'), 'utf-8'), bcrypt.gensalt())
#
# return auth_entry

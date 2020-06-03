from sawtooth_signing import create_context
from sawtooth_signing import ParseError
# from sawtooth_signing.secp256k1 import Secp256k1PrivateKey
from sawtooth_signing import CryptoFactory

from rest_api.common.exceptions import HealthCareException
from sawtooth_signing.secp256k1 import Secp256k1PrivateKey

import json
class GeneralTool:

    def __init__(self):
        self.CONTEXT = create_context('secp256k1')

    def ParsePrivateKey(self, private_key_str):
        try:
            private_key = Secp256k1PrivateKey.from_hex(private_key_str)
        except ParseError as e:
            raise HealthCareException(
                'Unable to load private key: {}'.format(str(e)))

        return private_key

    def addSigner(self, privatekey):
        return CryptoFactory(self.CONTEXT).new_signer(privatekey)

    def parseFromJSON(self, msg):
        return json.loads(msg)


    def parse2JSON(self, msg):
        return json.dumps(msg)
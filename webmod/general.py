import json


from passlib.hash import sha256_crypt as crypt
import julian
from datetime import datetime

class general:
    def gen_hash(self, data):
        """ generate the hashes for the passwords """
        password_gen = crypt.encrypt(data)
        return password_gen

    def date2julian(self, gdate=None):
        _time = None
        if gdate == None:
            gdate = datetime.now()
        jd = julian.to_jd(gdate, fmt='jd')
        return float(jd)

    def julian2date(self, jdate):
        dt = julian.from_jd(float(jdate))
        return dt

class RequestProc:
    """This class is building to take the information from
    the byte."""
    def merge_two_dicts(self, x, y):
        """Given two dicts, merge them into a new dict as a shallow copy."""
        z = x.copy()
        z.update(y)
        return z


    def __init__(self, request):
        self.dataPckg = {}
        if request.method == 'GET':
            self.dataPckg = request.args.to_dict()
        elif request.method == 'POST':


            if len(request.form.to_dict()):
                self.dataPckg = request.form.to_dict()
            if request.json != None:
                self.dataPckg = request.json
            if request.data.decode()!='':
                self.dataPckg = json.loads(request.data.decode())

            if len(request.files.to_dict())>0:
                newdict = self.merge_two_dicts(request.files.to_dict(), self.dataPckg)
                self.dataPckg=newdict



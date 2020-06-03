import json
from flask_mail import Message, Mail

class General:
    def sendMail(self, bodyMsg, receiptment, subject=None):
        # This function, send an email to a client.
        # from app import app  # Have to do it here.
        from app import app
        msg = Message(subject, sender="codeservicecorp@gmail.com", recipients=[receiptment])
        msg.html = bodyMsg
        print(app)
        mail = Mail(app)
        mail.send(msg)


    def merge_two_dicts(self, x, y):
        """Given two dicts, merge them into a new dict as a shallow copy."""
        z = x.copy()
        z.update(y)
        return z



class RequestProc:
    """This class is building to take the information from
    the byte."""

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
                newdict = General().merge_two_dicts(request.files.to_dict(), self.dataPckg)
                self.dataPckg=newdict



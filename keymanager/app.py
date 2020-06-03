import json
import sys
import os


sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from bs4 import BeautifulSoup



from flask import Flask, request, render_template, session, url_for, redirect, flash
from flask_login import LoginManager

app = Flask(__name__)
login_manager = LoginManager()
UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__))+'/static/'


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
with open("keymanager/params.json") as f:
    config = json.loads(f.read())
    app.secret_key = config["secret_key"]
    app.config["SQLALCHEMY_DATABASE_URI"] = config["postgres"]
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # This is by default don't touch it.
    app.config["MAIL_SERVER"] = config["mail"]["host"]
    app.config["MAIL_PORT"] = int(config["mail"]["port"])
    app.config["MAIL_USE_SSL"] = True
    app.config["MAIL_USERNAME"] = config["mail"]["username"]
    app.config["mail"] = config["mail"]["mail"]
    app.config["MAIL_PASSWORD"] = config["mail"]["password"]

with app.app_context():
    from tools.DataBase.Base import db
    from general import RequestProc
    db.init_app(app)


    static_file_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static')
db.init_app(app)

application = app


@app.route("/regkeygen", methods=['POST','GET'])
def keygen():
    arguments = RequestProc(request).dataPckg
    username=arguments['username']
    keygen_name=username.replace('_','')
    os.system("sawtooth keygen {}".format(keygen_name))

    private_key = ""
    public_key  = ""
    with open('/root/.sawtooth/keys/{}.priv'.format(keygen_name), 'r') as f:
        private_key = f.read()

    with open('/root/.sawtooth/keys/{}.pub'.format(keygen_name), 'r') as f:
        public_key = f.read()


    if request.method == 'GET':
        return {'public_key':public_key.replace("\n",""), "private_key":private_key.replace("\n", "")}
    if request.method == 'POST':
        return {'public_key':public_key.replace("\n",""), "private_key":private_key.replace("\n", "")}



@app.route("/getPrivateKey", methods=['POST'])
def getPrivateKey():
    arguments = RequestProc(request).dataPckg
    username = arguments['username']
    keygen_name = username.replace('_','')
    try:

        with open('/root/.sawtooth/keys/{}.priv'.format(keygen_name), 'r') as f:
            private_key = f.read()
            keys={'private_key':private_key.replace("\n","")}
            with open('/root/.sawtooth/keys/{}.pub'.format(keygen_name), 'r') as f:
                keys['public_key'] = f.read().replace("\n", "")
            return keys
    except:
        return {"error": "No private key"}



@app.route("/getKeyDocPat", methods=['POST'])
def getPrivateKeyMult():
    arguments = RequestProc(request).dataPckg
    username = arguments['usernames']
    keylist= {}
    for piece in username:
        keygen_name = username[piece].replace('_','')
        try:

            with open('/root/.sawtooth/keys/{}.priv'.format(keygen_name), 'r') as f:
                private_key = f.read()
                keys={'private_key':private_key.replace("\n","")}
                with open('/root/.sawtooth/keys/{}.pub'.format(keygen_name), 'r') as f:
                    keys['public_key'] = f.read().replace("\n", "")
                keylist[piece]=keys
        except:
            return {"error": "No private key"}
    return keylist

@app.route("/getPublickey", methods=['POST'])
def getPublickey():
    arguments = RequestProc(request).dataPckg
    username = arguments['username']
    keygen_name = username.replace('_','')

    private_key = ""

    with open('/root/.sawtooth/keys/{}.pub'.format(keygen_name), 'r') as f:
        public_key = f.read().replace("\n", "")

        if request.method == 'GET':
            return {'public_key':public_key.replace("\n","")}
        if request.method == 'POST':
            return {'public_key':public_key.replace("\n","")}
    return {"error":"Key not found or user not registred"}




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8863)
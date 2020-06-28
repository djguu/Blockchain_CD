import os.path
from os import path

from Crypto.PublicKey import RSA

import binascii
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

# from blockchain import *

import flask
from flask import Flask
from flask import request
import requests

app = Flask(__name__)


class Transaction:
    def __init__(self, sender_pk, sender_sk, receiver_pk, message):
        self.sender_pk = sender_pk
        self.sender_sk = sender_sk
        self.receiver_pk = receiver_pk
        self.message = message
        self.signature = None

    def to_dict(self):
        return {'sender_address': binascii.hexlify(self.sender_pk.export_key()).decode('ascii'),
                'recipient_address': binascii.hexlify(self.receiver_pk.export_key()).decode('ascii'),
                'message': self.message}

    def sign_transaction(self):
        h = SHA256.new(str(self.to_dict()).encode('utf-8'))
        signer = pkcs1_15.new(self.sender_sk)
        self.signature = binascii.hexlify(signer.sign(h)).decode('ascii')


class User:
    def __init__(self, username):
        # self.message = message
        self.user = username
        self.pk_file = 'keys/' + username + '.pk.pem'
        self.sk_file = 'keys/' + username + '.sk.pem'
        self.sk = None
        self.pk = None

        if not self.keys_exist():
            self.create_keys()

        self.set_keys()

    # Checks if the keys already exist or not
    def keys_exist(self):
        if not os.path.exists('keys'):
            os.makedirs('keys')
        if not path.exists(self.pk_file) or not path.exists(self.sk_file):
            return False
        return True

    # This function creates public and secret keys for user
    def create_keys(self):
        key = RSA.generate(2048)
        private_key = key.export_key()
        file_out = open(self.sk_file, "wb")
        file_out.write(private_key)
        file_out.close()

        public_key = key.publickey().export_key()
        file_out = open(self.pk_file, "wb")
        file_out.write(public_key)
        file_out.close()

    # This function sets the keys of the current user
    def set_keys(self):
        # Secret key of the user
        self.sk = RSA.import_key(open(self.sk_file).read())
        # Public key of the user
        self.pk = RSA.import_key(open(self.pk_file).read())


client1 = User("testUser")
client2 = User("testeUser2")

transaction = Transaction(client1.pk, client1.sk, client2.pk, "User 1 sent X to User 2")
transaction.sign_transaction()


@app.route('/submit', methods=['GET', 'POST'])
def submit_textarea():
    """
    Endpoint to create a new transaction via our application.
    """
    post_object = {
        "contents": transaction.to_dict(),
        "signature": transaction.signature
    }

    # Submit a transaction
    if request.method == 'GET':
        new_tx_address = "http://127.0.0.1:8000/new_transaction"
    else:
        port_nb = request.get_json()
        new_tx_address = "http://127.0.0.1:" + str(port_nb) + "/new_transaction"

    requests.post(new_tx_address,
                  json=post_object,
                  headers={'Content-type': 'application/json'})

    return "Success", 201


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=6000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(debug=True, host='127.0.0.1', port=port)

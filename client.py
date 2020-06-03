from collections import OrderedDict

from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
import os.path
from os import path
import binascii
from blockchain import *


class Transaction:
    def __init__(self, sender_pk, sender_sk, receiver_pk, message):
        self.sender_pk = sender_pk
        self.sender_sk = sender_sk
        self.receiver_pk = receiver_pk
        self.message = message

    def to_dict(self):
        return OrderedDict({'sender_address': binascii.hexlify(self.sender_pk.export_key()).decode('ascii'),
                            'recipient_address':  binascii.hexlify(self.receiver_pk.export_key()).decode('ascii'),
                            'message': self.message})

    def sign_transaction(self):
        h = SHA256.new(str(self.to_dict()).encode('utf-8'))
        signer = pkcs1_15.new(self.sender_sk)
        self.signature = binascii.hexlify(signer.sign(h)).decode('ascii')


class User:
    def __init__(self, user):
        # self.message = message
        self.user = user
        self.pk_file = 'keys/' + user + '.pk.pem'
        self.sk_file = 'keys/' + user + '.sk.pem'

        if not self.keys_exist():
            self.create_keys()

        self.get_keys()

    def keys_exist(self):
        if not os.path.exists('keys'):
            os.makedirs('keys')
        if not path.exists(self.pk_file) or not path.exists(self.sk_file):
            return False
        return True

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

    def get_keys(self):
        # Secret key of the user
        self.sk = RSA.import_key(open(self.sk_file).read())
        # self.sk = binascii.hexlify(secret_key.export_key())

        # Public key of the user
        self.pk = RSA.import_key(open(self.pk_file).read())
        # self.pk = binascii.hexlify(public_key.export_key())


# Initializing blockchain
bc = Blockchain()

# Initializing users
client1 = User("testUser")
client2 = User("testeUser2")

transaction = Transaction(client1.pk, client1.sk, client2.pk, "User A sent X to User B")
transaction.sign_transaction()

bc.add_new_transaction(transaction)

transaction = Transaction(client1.pk, client1.sk, client2.pk, "User x sent X to User y")
transaction.sign_transaction()

bc.add_new_transaction(transaction)

mine = bc.mine()



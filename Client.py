from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
import os.path
from os import path


class Client:
    def __init__(self, user, message):
        self.message = message.encode()
        self.user = user
        self.pk_file = 'keys/' + user + '.pk.pem'
        self.sk_file = 'keys/' + user + '.sk.pem'
        if self.keys_exist():
            self.sign()
            self.verify()

    def sign(self):
        key = RSA.import_key(open(self.sk_file).read())
        self.h = SHA256.new(self.message)
        self.signature = pkcs1_15.new(key).sign(self.h)
        print(self.signature)

    def verify(self):
        key = RSA.import_key(open(self.pk_file).read())
        h = SHA256.new(self.message)
        try:
            pkcs1_15.new(key).verify(self.h, self.signature)
            print("The signature is valid.")
        except (ValueError, TypeError):
            print("The signature is not valid.")

    def keys_exist(self):
        if not os.path.exists('keys'):
            os.makedirs('keys')
        if not path.exists(self.pk_file) or not path.exists(self.sk_file):
            self.create_keys()
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

# cl = Client("djguu", "teste")
# print(type(cl.message))



import binascii
from hashlib import sha256

from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

import json
import time


class Block:
    def __init__(self, index, transactions, timestamp, previous_hash, nonce=0):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash  # Adding the previous hash field
        self.nonce = nonce

    def compute_hash(self):
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()


class Blockchain:
    # difficulty of PoW algorithm
    difficulty = 2

    def __init__(self):
        self.unconfirmed_transactions = []  # data yet to get into blockchain
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block(0, [], 0, "0")
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def proof_of_work(block):
        block.nonce = 0

        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * Blockchain.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()
            # print("Current nonce: " + str(block.nonce))

        return computed_hash

    def add_block(self, block, proof):
        previous_hash = self.last_block.hash
        if previous_hash != block.previous_hash:
            return False
        if not Blockchain.is_valid_proof(block, proof):
            return False

        block.hash = proof
        self.chain.append(block)
        return True

    @staticmethod
    def is_valid_proof(block, block_hash):
        return (block_hash.startswith('0' * Blockchain.difficulty) and
                block_hash == block.compute_hash())

    @staticmethod
    def verify_transaction(transaction):
        public_key = RSA.import_key(binascii.unhexlify(transaction["contents"]["sender_address"]).decode())
        h = SHA256.new(str(transaction["contents"]).encode('utf-8'))
        try:
            verifier = pkcs1_15.new(public_key)
            verifier.verify(h, binascii.unhexlify(transaction["signature"]))
            # print("The signature is valid.")
            return True
        except (ValueError, TypeError):
            print("The signature is not valid.")
            return False

    def add_new_transaction(self, transaction):
        if self.verify_transaction(transaction):
            self.unconfirmed_transactions.append(json.dumps(transaction))

    def mine(self):
        if not self.unconfirmed_transactions:
            return False

        last_block = self.last_block

        new_block = Block(index=last_block.index + 1,
                          transactions=self.unconfirmed_transactions,
                          timestamp=time.time(),
                          previous_hash=last_block.hash)

        proof = self.proof_of_work(new_block)

        self.add_block(new_block, proof)

        self.unconfirmed_transactions = []

        return True

    def check_chain_validity(self):
        result = True
        previous_hash = "0"

        # Iterate through every block
        for block in self.chain:
            block_hash = block.hash
            # remove the hash field to recompute the hash again
            # using `compute_hash` method.
            delattr(block, "hash")

            if block.index != 0 and (not self.is_valid_proof(block, block_hash) or
                                     previous_hash != block.previous_hash):
                result = False
                break

            block.hash, previous_hash = block_hash, block_hash

        return result

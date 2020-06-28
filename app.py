from flask import Flask, request
import requests
from time_tester import start_timer, end_timer

import json

from blockchain import Blockchain, Block

app = Flask(__name__)

# the node's copy of blockchain
blockchain = Blockchain()

# the address to other participating members of the network
peers = set()


# endpoint to submit a new transaction. This will be used by
# our application to add new data (posts) to the blockchain
@app.route('/new_transaction', methods=['POST'])
def new_transaction():
    tx_data = request.json
    required_fields = ["sender_address", "recipient_address", "message"]

    for field in required_fields:
        if not tx_data["contents"].get(field):
            return "Invalid transaction data", 404

    blockchain.add_new_transaction(tx_data)

    return "Success", 201


# endpoint to request the node to mine the unconfirmed
# transactions (if any). We'll be using it to initiate
# a command to mine from our application itself.
@app.route('/mine', methods=['GET'])
def mine_unconfirmed_transactions():
    result = blockchain.mine()
    if not result:
        return "No transactions to mine"
    else:
        # Making sure we have the longest chain before announcing to the network
        chain_length = len(blockchain.chain)
        start_timer()
        consensus()
        print(end_timer())
        if chain_length == len(blockchain.chain):
            # announce the recently mined block to the network
            announce_new_block(blockchain.last_block)
        return "Block #{} is mined.".format(blockchain.last_block.index)


@app.route('/chain_check', methods=['POST'])
def chain_check():
    global blockchain

    # Add the node to the peer list
    peers.update(request.get_json()["peers"])
    if blockchain.check_chain_validity():
        # Return the consensus blockchain to the newly registered node
        # so that he can sync
        return get_chain(), 200
    return "Error with chain validity", 400


@app.route('/register')
def register():
    """
    Internally calls the `register_node` endpoint to
    register current node with the node specified in the
    request, and sync the blockchain as well as peer data.
    """
    global peers
    dns_address = "http://127.0.0.1:4000"
    if not dns_address:
        return "DNS unavailable", 400

    data = {'node_address': request.host_url, 'current_peers': list(peers)}
    headers = {'Content-Type': "application/json"}

    # Make a request to register with remote node and obtain information
    response = requests.post(dns_address + "/get_peers",
                             data=json.dumps(data), headers=headers)
    peers.update(response.json()['peers'])
    if response.status_code == 200:
        other_nodes = False
        for node in peers:
            if request.host_url != node:
                other_nodes = True
                data = {'peers': list(peers)}
                response = requests.post("{}/chain_check".format(node),
                                         data=json.dumps(data), headers=headers)
                if response.status_code == 200:
                    global blockchain

                    # update chain and the peers
                    chain_dump = response.json()['chain']
                    if len(blockchain.chain) < len(chain_dump):
                        blockchain = create_chain_from_dump(chain_dump)
                    else:
                        start_timer()
                        consensus()
                        print(end_timer())
                    return "Registration successful", 200
        if not other_nodes:
            return "No other nodes", 200
    else:
        # if something goes wrong, pass it on to the API response
        return response.content, response.status_code


def create_chain_from_dump(chain_dump):
    generated_blockchain = Blockchain()
    # generated_blockchain.create_genesis_block()
    for idx, block_data in enumerate(chain_dump):
        if idx == 0:
            continue  # skip genesis block
        block = Block(block_data["index"],
                      block_data["transactions"],
                      block_data["timestamp"],
                      block_data["previous_hash"],
                      block_data["nonce"])
        proof = block_data['hash']
        added = generated_blockchain.add_block(block, proof)
        if not added:
            raise Exception("The chain dump is tampered!!")
    return generated_blockchain


def announce_new_block(block):
    """
    A function to announce to the network once a block has been mined.
    Other blocks can simply verify the proof of work and add it to their
    respective chains.
    """
    for peer in peers:
        url = "{}add_block".format(peer)
        headers = {'Content-Type': "application/json"}
        requests.post(url,
                      data=json.dumps(block.__dict__, sort_keys=True),
                      headers=headers)


# endpoint to add a block mined by someone else to
# the node's chain. The block is first verified by the node
# and then added to the chain.
@app.route('/add_block', methods=['POST'])
def verify_and_add_block():
    block_data = request.get_json()
    block = Block(block_data["index"],
                  block_data["transactions"],
                  block_data["timestamp"],
                  block_data["previous_hash"],
                  block_data["nonce"])

    proof = block_data['hash']
    added = blockchain.add_block(block, proof)

    if not added:
        start_timer()
        consensus()
        print(end_timer())
        return "The block was discarded by the node", 400

    return "Block added to the chain", 201


# endpoint to query unconfirmed transactions
@app.route('/pending_tx')
def get_pending_tx():
    return json.dumps(blockchain.unconfirmed_transactions)


# endpoint to return the node's copy of the chain.
# Our application will be using this endpoint to query
# all the posts to display.
@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.__dict__)
    return json.dumps({"length": len(chain_data),
                       "chain": chain_data,
                       "peers": list(peers)})


def consensus():
    """
    Our naive consnsus algorithm. If a longer valid chain is
    found, our chain is replaced with it.
    """
    global blockchain
    dns_address = "http://127.0.0.1:4000"
    if not dns_address:
        return "DNS unavailable", 400

    longest_chain = None
    current_len = len(blockchain.chain)
    response = requests.get(dns_address + "/get_peers")
    peers.update(response.json()["peers"])
    for node in peers:
        data = {'peers': list(peers)}
        headers = {'Content-Type': "application/json"}

        response = requests.post("{}chain_check".format(node),
                                 data=json.dumps(data), headers=headers)

        length = response.json()['length']
        chain_dump = response.json()['chain']

        if length > current_len:
            current_len = length
            longest_chain = create_chain_from_dump(chain_dump)

    if longest_chain:
        blockchain = longest_chain
        return True
    return False


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=8000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(debug=True, host='127.0.0.1', port=port)

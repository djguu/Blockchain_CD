from flask import Flask, request
import requests

app = Flask(__name__)

known_clients = set()


@app.route('/get_peers', methods=["POST", "GET"])
def get_peers():
    if request.method == "POST":
        known_clients.add(request.get_json()['node_address'])
        known_clients.update(request.get_json()['current_peers'])
    # print(known_clients)
    response = {'peers': list(known_clients)}
    return response, 200


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=4000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(debug=True, host='127.0.0.1', port=port)
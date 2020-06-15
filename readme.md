# My Distribuited Computation Project

#### Using python 3.7

---

### Install Dependencies

```
 pip3 install -r requirements.txt
```
---
### Run Nodes

````
python blockchain.py -p 8000
````
##### New nodes:
````
python blockchain.py -p 8001
````
````
python blockchain.py -p ....
````

#### Start client
````
python client.py
````
---
New transaction:(use this for now)
````
curl -X GET http://127.0.0.1:5000/submit
````

Later transaction method (DONT USE THIS, DOESNT WORK)
````
curl -X POST http://127.0.0.1:5000/submit_transaction -H 'Content-Type: application/json' -d '{"sender_addr": "", ....}'
````

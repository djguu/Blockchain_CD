# My Distributed Computation Project

#### Using python 3.7

---

### Install Dependencies

```
 pip3 install -r requirements.txt
```
---
### Run Nodes

````
python app.py -p 8000
````
##### New nodes:
````
python app.py -p 8001

python app.py -p ....
````

#### Start client
````
python client.py
````

#### Start DNS
````
python dns.py
````
---
Register nodes:
````
curl -X GET http://127.0.0.1:8000/register
curl -X GET http://127.0.0.1:8001/register
````
New transaction: (change 8000 for port number of node)
````
curl -X POST http://127.0.0.1:6000/submit -H "Content-Type: application/json" -d "8000"
````
Check pending transactions:
````
curl -X GET http://127.0.0.1:8000/pending_tx
````
Mine transactions:
````
curl -X GET http://127.0.0.1:8000/mine
````
Check chains:
````
curl -X GET http://127.0.0.1:8000/chain
````
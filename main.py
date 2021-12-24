import json
from itertools import cycle

from flask import Flask, jsonify, request

import requests

app = Flask(__name__)


catCycle = cycle(["http://192.168.56.104:7777","http://192.168.56.101:7000"])
ordCycle = cycle(["http://192.168.56.105:9999","http://192.168.56.103:9000"])


@app.route('/searchTopic/<string:topic>', methods=['GET'])
def searchByBookTopic(topic):
    f = open('cache.json', 'r')
    data = json.load(f)

    if topic in data["srchTopic"]:
        for i in data["srchTopic"][topic]:
             if data["srchTopic"][topic] != None:
                   return jsonify(data["srchTopic"][topic])

    req=requests.get("{}/search/{}".format(next(catCycle),topic)) #send to catalog
    f.close()
    if req.status_code == 200:
        result=req.json() #content of json as dictionary

        f3 = open('cache.json', 'r')
        data = json.load(f3)
        for x in range(len(result)):
            if result[x]["id"] in data["srchTopic"]:
                return jsonify(result)

        data["srchTopic"][topic] = result
        f3.close()

        f2 = open('cache.json', 'w')
        json.dump(data, f2)
        f2.close()


        return jsonify(result)

    elif req.status_code == 404:
        return 'The server has not found anything matching the given URL',404

    else:
        return 'Status code '+ str(req.status_code) +' indicates to something ERROR!',req.status_code


@app.route('/searchID/<int:id>', methods=['GET'])
def searchByBookId(id):

    f = open('cache.json','r')
    data = json.load(f)

    if id in data["ids"]:
        if data["ids"][id] != None:
            return jsonify(data["ids"])

    req=requests.get("{}/info/{}".format(next(catCycle),id))
    f.close()

    if req.status_code == 200:
        result=req.json() #content of json as dictionary

        f = open('cache.json', 'r')
        data = json.load(f)

        if str(result["id"]) in data["ids"]:
            return jsonify(result)

        data["ids"][result["id"]] = result
        f.close()

        f = open('cache.json', 'w')
        json.dump(data, f)
        f.close()
        return jsonify(result)

    elif req.status_code == 404:
        return 'The server has not found anything matching the given URL',404

    else:
        return 'Status code '+ str(req.status_code) +' indicates to something ERROR!',req.status_code

@app.route('/purchase/<int:id>', methods=['POST'])
def purchase(id):
    x=next(ordCycle)
    req = requests.get("{}/purchase/{}".format(x,id))

    if req.status_code == 200:
        result = req.json()  # content of json as dictionary
        req2 = requests.get("{}/purchase/{}".format(next(ordCycle), id))
        if req2.status_code == 200:
            return '',req.status_code
        else:
            return jsonify(result)

    elif req.status_code == 404:
        return 'The server has not found anything matching the URI given',404

    else:
        return 'Status code '+ str(req.status_code) +' indicates to something ERROR!',req.status_code


@app.route('/invalidate', methods=['POST'])
def InvalidCache():
    res = request.get_json()

    f= open("cache.json", "r")
    data = json.load(f)
    print(res[0]["id"])
    data["ids"].pop(str(res[0]["id"]),None)
    data["srchTopic"].pop(str(res[0]["topic"]),None)
    f.close()
    f1=open("cache.json", "w")
    json.dump(data, f1)
    f1.close()

    return '',200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=6000)

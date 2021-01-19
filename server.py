#!/usr/bin/env python

import os
import requests
from flask import Flask, Response, render_template
app = Flask(__name__)


@app.route("/")
def index():
    return render_template('index.html')

@app.route("/graphql-query-test")
def graphql_query_test():
    headers = {}
    query = """
    {
      allCinemaDetails(before: "2017-10-04", after: "2010-01-01") {
        edges {
          node {
            slug
            hallName
          }
        }
      }
    }
    """
    request = requests.post('https://etmdb.com/graphql',
        json={'query': query}, headers=headers)
    return Response(request.text)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))

@app.route("/graph-api-query-test")
def graph_api_query_test():
    headers = {}
    query = """
    {
      tokens(first: 5) {
        id
        symbol,
        name,
        decimals,
        tradeVolume,
      }
    }
    """
    request = requests.post('https://api.thegraph.com/subgraphs/name/1inch-exchange/one-inch-v2/graphql',
        json={'query': query}, headers=headers)
    return Response(request.text)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))




if __name__ == "__main__":
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 3000), debug=True)

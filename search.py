import logging
from google.appengine.api import search
from model import token_from_pair_name, token_from_pair_symbol

def create_document(id, search_fields):
    def formatValue(field):
        value = token_from_pair_symbol((token_from_pair_name(field['value'])))
        formatted_value = ','.join(tokenize_autocomplete(value)) if field.get('tokenize') else value
        logging.info('formatted value: %s' % formatted_value)
        return formatted_value

    fields = [
        search.TextField(name=field['name'], value=formatValue(field)) for field in search_fields
    ]
    document = search.Document(
        # Setting the doc_id is optional. If omitted, the search service will
        # create an identifier.
        doc_id=id,
        fields=fields)
    return document

def add_documents_to_index(index, documents):
    index = search.Index(index)
    index.put(documents)

def get_document_by_id(index, id):
    index = search.Index(index)

    # Get a single document by ID.
    document = index.get(id)

    # Get a range of documents starting with a given ID.
    documents = index.get_range(start_id=id, limit=100)

    return document, documents

def query_index(index, query):
    index = search.Index(index)
    #example: query = 'product: piano AND price < 5000'
    #example query = 'piano' # searches all fields
    return index.search(query)

def tokenize_autocomplete(phrase):
    a = []
    for word in phrase.split():
        j = 1
        while True:
            for i in range(len(word) - j + 1):
                phrase = word[i:i + j]
                if len(phrase) > 2:
                    a.append(phrase)
            if j == len(word):
                break
            j += 1
    return a

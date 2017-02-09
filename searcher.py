from elasticsearch import Elasticsearch

es = Elasticsearch()


def search(query, indexer=es):
    result = ['{} ({})\n{}'.format(rank['_source']['title'], rank['_source']['category'], rank['_source']['article'])
              for rank in indexer.search(index='news-index', q=query)['hits']['hits']]
    return result


'''
for rank in search('зенит')['hits']['hits']:
    result = rank['_source']
    print('{} ({})\n{}\n\n'.format(result['title'], result['category'], result['article']))

'''


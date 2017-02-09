import pickle
from elasticsearch import Elasticsearch

es = Elasticsearch()
titles = pickle.load(open("title_base.pickle", 'rb'))
texts = pickle.load(open("text_base.pickle", 'rb'))


es.indices.create(index='news-index', ignore=400)  # ERROR 400 - IndexAlreadyExistsException
for cat in titles.keys():
    for i, n in enumerate(titles[cat]):
        es.index(index='news-index', doc_type='news', id=i, body={'title': titles[cat][i], 'article': texts[cat][i],
                                                                  'category': cat})


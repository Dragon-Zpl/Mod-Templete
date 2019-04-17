from elasticsearch import Elasticsearch
from config.read import *

try:
    es = Elasticsearch('{}:{}'.format(configs.es["ip"],configs.es["port"]))
except:
    print("connec to es fail")
    es = None


class Google_download_log:
    index = configs.es["index"]
    doc_type = configs.es["doc_type"]

    @classmethod
    def create_mapping(cls):
        mappings = {
            "mappings": {
                "doc_type": {
                    "properties": {
                        "info": {
                            "properties": {
                                "download": {
                                    "type": "keyword"
                                },
                                "download_using_time": {
                                    "type": "double"
                                },
                                "insert_apptb": {
                                    "type": "keyword"
                                },
                                "post_bg": {
                                    "type": "keyword"
                                }
                            }
                        },
                        "pkgname": {
                            "type": "keyword"
                        },
                        "type": {
                            "type": "keyword"
                        },
                        "update_time": {
                            "type": "date",
                            "format": "yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||epoch_millis"
                        },
                        "version": {
                            "type": "keyword"
                        }
                    }
                }
            }
        }
        rs = es.indices.create(index=cls.index, body=mappings)
        return rs

    @classmethod
    def insert_info(cls, body):
        rs = es.index(index=cls.index, doc_type=cls.doc_type, body=body)
        return rs

    @classmethod
    def update_info(cls, body):
        rs = es.update_by_query(index=cls.index, doc_type=cls.doc_type, body=body)
        return rs['updated']

    @classmethod
    def delete_info(cls, body):
        rs = es.delete_by_query(index=cls.index, doc_type=cls.doc_type, body=body)
        return rs['deleted']

    @classmethod
    def query_info(cls, body):
        rs = es.search(index=cls.index, doc_type=cls.doc_type, body=body)
        return rs['hits']['total']


if __name__ == '__main__':
    Google_download_log.create_mapping()

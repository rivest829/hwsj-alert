#!/usr/bin/python
# coding:utf-8

import elasticsearch

es = elasticsearch.Elasticsearch(hosts="*:9200")

#time_range:
#unit:m for minutes ,h for hours
#  example:12h,1m
def count_error_log(time_range):
    error_log_raw_result = es.count(
        body={
            "query": {
                "bool": {
                    "must": {
                        "query_string": {
                            "query": "error"
                        }
                    },
                    "filter": {
                        "range": {
                            "@timestamp": {
                                "gt": "now-" + time_range
                            }
                        }
                    }
                }
            }
        }
    )
    error_log_num = error_log_raw_result["count"]
    return error_log_num

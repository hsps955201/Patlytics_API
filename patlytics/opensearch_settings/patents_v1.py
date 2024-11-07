INDEX_SETTINGS = {
    "settings": {
        "index": {
            "number_of_shards": 1,
            "number_of_replicas": 0,
            "max_ngram_diff": 19
        },
        "analysis": {
            "analyzer": {
                "autocomplete_analyzer": {
                    "type": "custom",
                    "tokenizer": "autocomplet_tokenizer",
                    "filter": ["lowercase"]
                },
                "pinyin_analyzer": {
                    "type": "custom",
                    "tokenizer": "my_pinyin"
                }
            },
            "tokenizer": {
                "autocomplet_tokenizer": {
                    "type": "ngram",
                    "min_gram": 1,
                    "max_gram": 20,
                    "token_chars": ["letter", "digit"]
                },
                "my_pinyin": {
                    "type": "pinyin",
                    "keep_first_letter": False,
                    "keep_full_pinyin": True,
                    "keep_original": False,
                    "limit_first_letter_length": 16,
                    "lowercase": True
                }
            }
        }
    },
    "mappings": {
        "properties": {
            "id": {"type": "integer"},
            "publication_number": {"type": "keyword"},
            "title": {
                "type": "text",
                "analyzer": "autocomplete_analyzer",
                "fields": {
                    "pinyin": {"type": "text", "analyzer": "pinyin_analyzer"},
                    "keyword": {"type": "keyword"}
                }
            },
            "ai_summary": {"type": "text", "analyzer": "standard"},
            "raw_source_url": {"type": "keyword"},
            "assignee": {"type": "text", "analyzer": "standard"},
            "inventors": {
                "type": "nested",
                "properties": {
                    "first_name": {"type": "text", "analyzer": "standard"},
                    "last_name": {"type": "text", "analyzer": "standard"}
                }
            },
            "priority_date": {"type": "date", "format": "yyyy-MM-dd"},
            "application_date": {"type": "date", "format": "yyyy-MM-dd"},
            "grant_date": {"type": "date", "format": "yyyy-MM-dd"},
            "abstract": {"type": "text", "analyzer": "standard"},
            "description": {"type": "text", "analyzer": "standard"},
            "claims": {
                "type": "nested",
                "properties": {
                    "num": {"type": "keyword"},
                    "text": {"type": "text", "analyzer": "standard"}
                }
            },
            "jurisdictions": {"type": "keyword"},
            "classifications": {
                "properties": {
                    "ipcr": {
                        "type": "nested",
                        "properties": {
                            "code": {"type": "keyword"},
                            "date": {"type": "date", "format": "yyyyMMdd"},
                            "extra_info": {"type": "text"}
                        }
                    },
                    "cpc": {
                        "type": "nested",
                        "properties": {
                            "code": {"type": "keyword"},
                            "date": {"type": "date", "format": "yyyyMMdd"},
                            "extra_info": {"type": "text"}
                        }
                    }
                }
            },
            "application_events": {"type": "text", "analyzer": "standard"},
            "citations": {
                "type": "nested",
                "properties": {
                    "root": {"type": "keyword"},
                    "ucids": {
                        "type": "object",
                        "properties": {
                            "published": {"type": "date", "format": "yyyyMMdd"},
                            "assignee": {"type": "text"},
                            "applicant": {"type": "text"},
                            "inventor": {"type": "text"},
                            "cpc": {"type": "keyword"}
                        }
                    }
                }
            },
            "image_urls": {"type": "keyword"},
            "landscapes": {"type": "text", "analyzer": "standard"},
            # "created_at": {"type": "date","format": 'yyyy-MM-dd HH:mm:ss.SSSSS||yyyy-MM-dd HH:mm:ss||yyyy-MM-dd HH:mm:ss.SSSSSSSSS'},
            # "updated_at": {"type": "date", "format": 'yyyy-MM-dd HH:mm:ss.SSSSS||yyyy-MM-dd HH:mm:ss||yyyy-MM-dd HH:mm:ss.SSSSSSSSS'},
            # "publish_date": {"type": "date", "format": "yyyy-MM-dd"},
            "citations_non_patent": {"type": "text", "analyzer": "standard"},
            "provenance": {"type": "keyword"},
            "attachment_urls": {"type": "keyword"}
        }
    }
}

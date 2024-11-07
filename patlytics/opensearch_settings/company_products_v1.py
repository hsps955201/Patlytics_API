INDEX_SETTINGS ={
  "settings": {
    "index": {
      "number_of_shards": 1,
      "number_of_replicas": 0
    },
    "analysis": {
      "analyzer": {
        "autocomplete_analyzer": {
          "type": "custom",
          "tokenizer": "autocomplete_tokenizer",
          "filter": ["lowercase"]
        },
        "pinyin_analyzer": {
          "type": "custom",
          "tokenizer": "my_pinyin_tokenizer",
          "filter": ["lowercase"]
        }
      },
      "tokenizer": {
        "autocomplete_tokenizer": {
          "type": "edge_ngram",
          "min_gram": 1,
          "max_gram": 20,
          "token_chars": ["letter", "digit"]
        },
        "my_pinyin_tokenizer": {
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
      "name": {
        "type": "text",
        "analyzer": "autocomplete_analyzer",
        "fields": {
          "pinyin": {
            "type": "text",
            "analyzer": "pinyin_analyzer"
          },
          "keyword": {
            "type": "keyword"
          }
        }
      },
      "products": {
        "type": "nested",
        "properties": {
          "name": {
            "type": "text",
            "analyzer": "autocomplete_analyzer",
            "fields": {
              "pinyin": {
                "type": "text",
                "analyzer": "pinyin_analyzer"
              },
              "keyword": {
                "type": "keyword"
              }
            }
          },
          "description": {
            "type": "text",
            "analyzer": "standard"
          }
        }
      }
    }
  }
}

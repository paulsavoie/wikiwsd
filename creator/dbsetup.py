import pymongo


db_host = 'localhost'
db_port = 27017

client = pymongo.MongoClient(db_host, db_port)
db = client.wikiwsd

article_collection = db.articles
article_collection.create_index([("title", 'hashed')])

redirect_collection = db.redirects
redirect_collection.create_index([("source", 'hashed')])

meaning_collection = db.redirects
meaning_collection.create_index([("string", 'hashed')])

import pymongo

class DBSetup():
    def __init__(self, host, port):
        self.__host = host
        self.__port = port

    def run(self):
        client = pymongo.MongoClient(self.__host, self.__port)
        db = client.wikiwsd

        db.drop_collection('articles')
        db.drop_collection('redirects')
        db.drop_collection('meanings')

        article_collection = db.articles
        article_collection.create_index([("title", 'hashed')])

        redirect_collection = db.redirects
        redirect_collection.create_index([("source", 'hashed')])

        meaning_collection = db.meanings
        meaning_collection.create_index([("string", 'hashed')])

if __name__ == '__main__':
    setup = DBSetup('localhost', 27017)
    setup.run()
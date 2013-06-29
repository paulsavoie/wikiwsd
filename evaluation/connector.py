class EvaluationConnector():
    def __init__(self, db_connector, sample):
        self.__db_connector = db_connector
        self.__sample = sample

    def get_article_by_title(self, title):
        if title == self.__sample['title']:
            return None 
        article = self.__db_connector.get_article_by_title(title)
        if article == None:
            return article
        for link in self.__sample['links']:
            if link == article['title']:
                if article['articleincount'] > 0: # necessary to du errors in creating database
                    article['articleincount'] -= 1
        return article

    def get_article_by_id(self, id):
        if id == self.__sample['id']:
            return None 
        article = self.__db_connector.get_article_by_id(id)
        if article == None:
            return article
        for link in self.__sample['links']:
            if link == article['title']:
                if article['articleincount'] > 0: # necessary to du errors in creating database
                    article['articleincount'] -= 1
        return article

    def resolve_redirect(self, name):
        return self.__db_connector.resolve_redirect(name)

    def retrieve_number_of_common_articles(self, id1, id2):
        num = self.__db_connector.retrieve_number_of_common_articles(id1, id2)
        # if this sample article links to both, reduce the number of links accordingly
        article1 = self.__db_connector.get_article_by_id(id1)
        article2 = self.__db_connector.get_article_by_id(id2)
        linkcounter = 0
        for link in self.__sample['links']:
            if link == article1['title'] or link == article2['title']:
                linkcounter += 1
        
        if linkcounter == 2: # sample article links to both other articles
            num -= 1
        if num < 0: # should not happen, but can due to problems in building database
            num = 0
        return num

    def retrieve_meanings(self, name):
        meanings = self.__db_connector.retrieve_meanings(name)
        for meaning in meanings:
            for link in self.__sample['links']:
                if link == meaning['name']:
                    meaning['articleincount'] -= 1
                    meaning['occurrences'] -= self.__sample['links'][link]
                    if meaning['articleincount'] == 0 or meaning['occurrences'] == 0:
                        meanings.remove(meaning)
        return meanings
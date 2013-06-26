class DBConnector():
    def __init__(self):
        pass

    def get_article(self, title):
        raise NotImplementedError('Method not implemented')

    def resolve_redirect(self, name):
        raise NotImplementedError('Method not implemented')

    def retrieve_number_of_common_articles(self, id1, id2):
        raise NotImplementedError('Method not implemented')

    def retrieve_meanings(self, name):
        raise NotImplementedError('Method not implemented')


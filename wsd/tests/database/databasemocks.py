class WorkViewMock:
    def __init__(self):
        self.redirects = {}
        self.articles = {}
        self.meanings = {}
        self.query_counter = 0
        self.commons = []
        self.occurrences = {}

    def resolve_title(self, title):
        if title in self.articles:
            return self.articles[title]

        if title in self.redirects:
            if self.redirects[title] in self.articles:
                return self.articles[self.redirects[title]]
        self.query_counter+= 1
        return None

    def retrieve_meanings(self, term):
        self.query_counter+= 1
        if term in self.meanings:
            return self.meanings[term]
        return []

    def retrieve_number_of_common_articles(self, id1, id2):
        self.query_counter+= 1
        for item in self.commons:
            if (item['id1'] == id1 and item['id2'] == id2) or (item['id1'] == id2 and item['id2'] == id1):
                return item['num']
        return 0

    def retrieve_occurrences(self, phrase):
        self.query_counter += 1
        if phrase in self.occurrences:
            return self.occurrences[phrase]

        return { 'occurrences': 0, 'as_link': 0 }

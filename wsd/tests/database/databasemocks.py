class WorkViewMock:
    def __init__(self):
        self.redirects = {}
        self.articles = {}
        self.meanings = {}
        self.query_counter = 0

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

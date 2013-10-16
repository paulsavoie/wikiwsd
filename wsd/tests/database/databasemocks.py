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

class BuildViewMock:
    def __init__(self):
        self.articles = []
        self.redirects = []
        self.links = []
        self.disambiguations = []
        self.ngrams = []
        self.commited = 0
        self.cache_reset = 0

    def insert_article(self, id, title):
        self.articles.append((id, title))

    def insert_redirect(self, source, target):
        self.redirects.append((source, target))

    def insert_link(self, source_id, target_name):
        self.links.append((source_id, target_name))

    def insert_disambiguation(self, string, target_name):
        self.disambiguations.append((string, target_name))

    def insert_ngrams(self, ngrams):
        self.ngrams.extend(ngrams)

    def commit(self):
        self.commited+= 1

    def reset_cache(self):
        self.cache_reset += 1
class WorkViewMock:
    def __init__(self):
        self.redirects = {}
        self.articles = {}

    def resolve_title(self, title):
        if title in self.articles:
            return self.articles[title]

        if title in self.redirects:
            if self.redirects[title] in self.articles:
                return self.articles[self.redirects[title]]

        return None
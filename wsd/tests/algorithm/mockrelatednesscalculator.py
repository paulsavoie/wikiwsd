class MockRelatednessCalculator():
    def __init__(self):
        self.commons = []
        self.called = 0

    def calculate_relatedness(self, link1, link2):
        self.called += 1
        for common in self.commons:
            if (link1['target_article_id'] == common['id1'] and link2['target_article_id'] == common['id2']) or (link1['target_article_id'] == common['id2'] and link2['target_article_id'] == common['id1']):
                return common['num']
        return 0.0
import os

class HTMLOutputter():
    '''outputter which creates user-readable html file
    '''

    '''constructor
    '''
    def __init__(self):
        self._header = None
        self._footer = None

    '''creates the output file 

        @param article the article to be outputted
        @param output_path the path of the output html file
    '''
    def output(self, article, output_path):
        # load html tepmlates
        header_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'header.html')
        footer_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'footer.html')

        header_html = 'There was an error loading the header HTML template'
        footer_html = 'There was an error loading the footer HTML template'
        with open(header_path, 'r') as header_f:
            header_html = header_f.read()
        with open(footer_path, 'r') as footer_f:
            footer_html = footer_f.read()


        html = ''
        text = article['text']
        tokens = text.split(' ')
        link_index = 0
        current_link = None
        link_html = ''
        for token in tokens:
            link_html = ''
            if token[0:2] == '[[':
                html += '<span class="noun">'
                token = token[2:]
                current_link = article['links'][link_index]
                link_index+= 1

            html+= token + ' '

            if token[-2:] == ']]':
                token = token[:-2]
                link_html += '<div class="disambiguations"><ul>'
                link_html += '<li class="header"><span class="label">Meaning</span><span class="percentage">Overall</span><span class="percentage">Rel.</span><span class="percentage">Comm.</span></li>'
                first_meaning = True
                for meaning in current_link['meanings']:
                    link_html += '<li'
                    if first_meaning:
                        link_html += ' class="selected"'
                        first_meaning = False
                    link_html += ('><span class="label">%s</span><span class="id">%s</span><span class="percentage">%d%%</span><span class="percentage">%d%%</span><span class="percentage">%d%%</span></li>' %
                        (meaning['target_article_name'],
                        meaning['target_article_id'],
                        round(meaning['overallMatch']*100),
                        round(meaning['relatedness']*100),
                        round(meaning['commonness']*100)))
                link_html += '</ul></div>'

                html = html[:-3] + ' ' + link_html + '</span>'

        # write output
        with open(output_path, 'w') as output_f:
            output_f.write(header_html)
            output_f.write(html.encode('utf-8', 'ignore'))
            output_f.write(footer_html)

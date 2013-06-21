""" Outputs the results as nice html
"""

class HTMLOutputter():
    def __init__(self):
        self.__header = None
        self.__footer = None

    def output(self, tokens, output_path):
        # load html tepmlates
        header_html = 'There was an error loading the header HTML template'
        footer_html = 'There was an error loading the footer HTML template'
        with open('header.html', 'r') as header_f:
            header_html = header_f.read()
        with open('footer.html', 'r') as footer_f:
            footer_html = footer_f.read()

        # concatenate actual html
        html = ""
        for token in tokens:
            if token.has_key('disambiguations'):
                disambiguations_html = '<div class="disambiguations"><ul>'
                for disambiguation in token['disambiguations']:
                    disambiguations_html += '<li><span class="label">%s</span><span class="percentage">%d%%</span></li>' % (disambiguation['meaning'].encode('ascii', 'ignore'), 
                        round(disambiguation['percentage']*100))
                disambiguations_html += '</ul></div>'
                html += ' <span class="noun">%s%s</span>' % (token['token'], disambiguations_html)
            else:
                html += ' %s' % token['token']

        # write output
        with open(output_path, 'w') as output_f:
            output_f.write(header_html)
            output_f.write(html)
            output_f.write(footer_html)

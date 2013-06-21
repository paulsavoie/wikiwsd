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
                disambiguations_html += '<li class="header"><span class="label">Meaning</span><span class="percentage">Overall</span><span class="percentage">Rel.</span><span class="percentage">Comm.</span></li>'
                index = 0
                for disambiguation in token['disambiguations']:
                    className = ''
                    if index == token['finalIndex']:
                        className = 'selected'
                    disambiguations_html += '<li class="%s"><span class="label">%s</span><span class="id">%s</span><span class="percentage">%d%%</span><span class="percentage">%d%%</span><span class="percentage">%d%%</span></li>' % ( 
                        className,
                        disambiguation['meaning'].encode('ascii', 'ignore'), 
                        disambiguation['id'],
                        round(disambiguation['overallMatch']*100),
                        round(disambiguation['averageRelatedness']*100),
                        round(disambiguation['percentage']*100))
                    index = index + 1
                disambiguations_html += '</ul></div>'
                html += ' <span class="noun">%s%s</span>' % (token['token'], disambiguations_html)
            else:
                html += ' %s' % token['token']

        # write output
        with open(output_path, 'w') as output_f:
            output_f.write(header_html)
            output_f.write(html)
            output_f.write(footer_html)

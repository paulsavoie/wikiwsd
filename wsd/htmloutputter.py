# -*- coding: utf-8 -*-
'''
This file contains the code to output a user-friendly
html file which displays the results of the word-sense-disambiguation
algorithm

Author: Paul Laufer
Date: Jun 2013

'''

import os

class HTMLOutputter():
    '''outputter which creates user-friendly html file
    '''

    '''constructor
    '''
    def __init__(self):
        self.__header = None
        self.__footer = None

    '''creates the output file 

    Arguments:
        tokens --- a list of dictionaries containing the following fields:
            finalIndex --- the index of the finally selected meaning 
            token --- the actual word 
            disambiguations --- a list of dictionaries listing all meanings with the following fields:
                meaning --- the textual representation of the meaning
                overallMatch --- the overall probability of the meaning being the correct one
                averageRelatedness --- the overall probability of the meaning being the correct one based on relatedness alone
                percentage --- the overall probability of the meaning being the correct one based on commonness alone 
                id --- the id of the referenced article
        output_path --- the path of the file that shall be written to
    '''
    def output(self, tokens, output_path):
        # load html tepmlates
        header_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'header.html')
        footer_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'footer.html')

        header_html = 'There was an error loading the header HTML template'
        footer_html = 'There was an error loading the footer HTML template'
        with open(header_path, 'r') as header_f:
            header_html = header_f.read()
        with open(footer_path, 'r') as footer_f:
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
            output_f.write(html.encode('utf-8', 'ignore'))
            output_f.write(footer_html)

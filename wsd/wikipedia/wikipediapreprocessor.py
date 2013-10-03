import threading
import Queue
import logging

WAIT_QUEUE_TIMEOUT = 2 # in seconds

class WikipediaPreProcessor(threading.Thread):
    '''The WikipediaPreProcessor class preprocesses text and removes tags, unnecessary links and
       other information and keeps the text only
    '''

    '''constructor

       @param input_queue if the preprocessor is used as a thread, articles are read from this queue [optional]
       @param output_queue if the preprocessor is used as a thread, articles are written to this queue [optional]
    '''
    def __init__(self, input_queue=None, output_queue=None):
        threading.Thread.__init__(self)
        self._input_queue = input_queue
        self._output_queue = output_queue
        self._end = False

        self._REMOVE_PAIRS=(
            (u'{{', u'}}'),
            (u'=====', u'====='),
            (u'====', u'===='),
            (u'===', u'==='),
            (u'==', u'=='),
            (u'[http', u']'),
            (u'[File:', u']'),
            (u'[Category:', u']'),
        )
        # html tags can end with /> or </tag-name> and needs to be handled separately
        # <!-- --> comments also as they can spread multiple lines

    '''processes a single article and cleans the text

       @param article a dictionary with a text field that contains the text (will be modified to hold the new text)

       @return the article with clean text only containing valid links
    '''
    def process(self, article):
        new_text = ''

        next_line_starts_in_comment = False
        line_starts_in_comment = False
        next_line_in_tag = 0
        line_in_tag = 0
        html_tags = []

        # iterate over lines
        lines = article['text'].strip().split('\n')
        for line in lines:
            line = line.strip()

            # STEP 1 - remove hyphens
            line = line.replace("'''", "")
            line = line.replace("''", "")

            # check if the line starts in a comment
            line_starts_in_comment = next_line_starts_in_comment
            next_line_starts_in_comment = False

            # check if the line starts in a tag
            line_in_tag = next_line_in_tag
            next_line_in_tag = 0

            # STEP 2 - remove comments
            while line.find('<!--') != -1 or line_starts_in_comment:
                start = 0
                if not line_starts_in_comment:
                    start = line.find('<!--')
                line_starts_in_comment = False
                end = line.find('-->')
                if end == -1:
                    next_line_starts_in_comment = True
                    line = line[0:start]
                else:
                    line = line[0:start] + line[end+3:]

            # STEP 3 - remove html tags
            index = 0
            outer_start_tag = line.find('<')
            # if the line already starts within an html tag
            if len(html_tags) != 0:
                outer_start_tag = 0
            while line.find('<', index) != -1:
                start = False
                index = line.find('<', index)+1
                end_tag = line.find('>', index)
                # if tag is a closing tag
                if line[index] == '/':
                    # this query is necessary as some invalid close tags appear on wikipedia - nothging to be done about that
                    if len(html_tags) != 0:
                        html_tags.pop()
                    # this is the outermost html tag
                    if len(html_tags) == 0:
                        line = line[:outer_start_tag] + line[end_tag+1:]
                        # start with next tag
                        outer_start_tag = line.find('<')
                        index = 0
                # not a closing tag
                else:
                    # a simple tag without an ending one, just remove it
                    if line[end_tag-1] == '/':
                        line = line[0:index-1] + line[end_tag+1:]
                        index-= 1
                        # if this was the outermost tag, start from the next tag
                        if index == outer_start_tag:
                            outer_start_tag = line.find('<')
                    # a normal tag is simply pushed to the stack
                    else:
                        html_tags.append(line[index:end_tag-1])

            # TODO: refactor
            if len(html_tags) > 0:
                # there is an opening tag somewhere
                if line.find('<') != -1:
                    line = line[:line.find('<')]
                else: # everything is already within a tag
                    line = ''

            # STEP 4 - remove invalid lines
            # simply ignore too short lines and those that start with an incorrect token
            if len(line) > 4 and line[0:2] != ' |' and line[0] != '|' and line[0] != '!':

                # STEP 5 - remove incorrect links
                line = self._remove_incorrect_links(line)

                # STEP 6 - remove pairs
                for pair in self._REMOVE_PAIRS:
                    line = self._remove_pairs(line, pair)

                # STEP 7 - remove end of line if { in it
                line = self._remove_box(line)

                # STEP 8 - remove emtpy brackets and double spaces that remained
                line = self._remove_empty_brackets(line)

                # STEP 9 - strip the line
                line = line.strip(' *\r\n')

                # append the cleaned line to the new text
                if len(line) > 0:
                    new_text += line + '\n'

        # set the cleaned text in the article and return it
        article['text'] = new_text
        return article

    '''the main thread method - should not be called, use start() instead
    '''
    def run(self):
        while not self._end:
            try:
                # retrieve a new article from the queue
                article = self._input_queue.get(True, WAIT_QUEUE_TIMEOUT)
                # process the article
                logging.info('preprocessing article %s' % (article['title'].encode('ascii', 'ignore')))
                self.process(article)
                # add the cleaned article to the output queue
                self._output_queue.put(article)
                # mark the task as done
                self._input_queue.task_done()
            except Queue.Empty:
                pass

    '''ends the thread 
    '''
    def end(self):
        self._end = True

    def _remove_pairs(self, line, pair):
        length = len(pair[0])
        start = line.find(pair[0])
        end = line.find(pair[1], start+length)
        
        while start != -1 and end != -1 and start < end:
            inner = line.find(pair[0], start+length)
            if inner != -1 and inner < end: # there is an inner pair, remove first
                line = line[0:start] + self._remove_pairs(line[start+length:], pair)
            else: # remove pair itself
                line = line[0:start] + line[end+len(pair[1]):]
            start = line.find(pair[0])
            end = line.find(pair[1], start + length)
        return line

    def _remove_incorrect_links(self, line):
        # iterate over all links
        next_link = line.find('[[')
        while next_link != -1:
            following_link = line.find('[[', next_link+2)
            next_colon = line.find(':', next_link)
            next_separator = line.find('|', next_link)
            next_end = line.find(']]', next_link)
            # the next link is invalid if it contains a colon
            if next_colon != -1 and (next_colon < next_end and (following_link == -1 or following_link > next_end or following_link > next_colon)):
                # remove the opening link target
                remove_characters_start = 2
                # if there is a separator in the invalid link
                if next_separator != -1 and (next_separator < next_end and (following_link == -1 or following_link > next_end or following_link > next_separator)):
                    # remove everything until the separator
                    remove_characters_start = (next_separator-next_link)+1

                # find matching end brackets
                # if there are inner links
                if following_link != -1 and following_link < next_end:
                    # count inner links
                    inner_link_counter = 0
                    next_inner_link = following_link
                    while next_inner_link == -1 or next_inner_link > next_end:
                        inner_link_counter+= 1
                        next_inner_link = line.find('[[', next_inner_link+2)

                    # find matching end brackets
                    end_link = next_end
                    while inner_link_counter > 0:
                        end_link = line.find(']]', end_link+2)
                        inner_link_counter-= 1
                # if there is no inner_link
                else:
                    end_link = next_end

                # remove the ending tag first
                line = line[:end_link] + line[end_link+2:]
                # then remove the beginning of the link
                line = line[:next_link] + line[next_link + remove_characters_start:]

                # start at the removed link position
                next_link = line.find('[[', next_link)

            # if the link is valid
            else:
                # just continue to the next link
                next_link = following_link

        return line

    def _remove_box(self, line):
        if line.find('{') != -1:
            line = line[0:line.find('{')]
        return line

    def _remove_empty_brackets(self, line):
        line = line.replace('()', '')
        line = line.replace('[]', '')
        line = line.replace('  ', ' ')
        line = line.replace(' .', '.')
        line = line.replace(' ,', ',')
        line = line.replace(' :', ':')
        line = line.replace(' !', '!')
        line = line.replace('&nbsp;', ' ')

        return line
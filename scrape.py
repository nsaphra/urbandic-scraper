"""
Scrape everything from urbandictionary.
Run as a script to extract all spelling variants ("way of spelling *").
"""

from bs4 import BeautifulSoup
import urllib
import json
import re
import sys

url_base = "http://www.urbandictionary.com"
url_start = url_base + "/browse.php?word=aa"
url_define = 'http://api.urbandictionary.com/v0/define?term='
word_link_prefix = "/define.php?term="

def find_next_url(page):
    next_page = page.find(rel="next").get("href")
    if next_page:
        return url_base + next_page

def find_words(page):
    for link in page.find_all("a"):
        link_url = link.get("href")
        if link_url and link_url.startswith(word_link_prefix):
            yield link_url.split("=")[1]

def query_word_definitions(word):
    response = urllib.urlopen(url_define + word)
    data = json.loads(response.read().decode('utf-8', 'ignore'))
    for x in data['list']:
        yield (x['word'], x['definition'])

def find_definitions(url=url_start):
    while url:
        print >> sys.stderr, url
        result = urllib.urlopen(url).read().decode('utf-8', 'ignore')
        page = BeautifulSoup(result, "lxml")
        for word in find_words(page):
            if '+' in word:
                continue # only interested in unigrams right now
            for (w, d) in query_word_definitions(word):
                yield (w, d)
        url = find_next_url(page)

def get_spelling_variants(definition):
    variants = set()
    for d in definitions:
        m = re.search(ur"spelling[^\.,]*( of| for|)[^\.,]* ('|\"|\[)(?P<respelled>\w+)('|\"|\])",
                      definition)
        if m:
            variant = m.group(2)
            yield variant

if __name__ == "__main__":
    url = url_start
    if len(sys.argv) > 1:
        url = sys.argv[1]
    for (word, definitions) in find_definitions(url=url):
        for variant in get_spelling_variants(definitions):
            # just so I don't have to deal with unicode issues later ...
            try:
                print u'%s\t%s' % (word, variant)
                sys.stdout.flush()
            except UnicodeEncodeError:
                print >> sys.stderr, "UnicodeEncodeError"
                continue

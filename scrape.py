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
    data = json.loads(response.read())
    return [x['definition'] for x in data['list']]

def find_definitions(url=url_start):
    while url:
        print >> sys.stderr, url
        page = BeautifulSoup(urllib.urlopen(url), "lxml")
        for word in find_words(page):
            yield (word, query_word_definitions(word))
        url = find_next_url(page)

def get_spelling_variants(definitions):
    for d in definitions:
        m = re.search(r"way of spelling (.*)(\.|\b|$)", d)
        if m:
            yield m.group(1)

if __name__ == "__main__":
    for (word, definitions) in find_definitions():
        for variant in get_spelling_variants(definitions):
            print "%s\t%s" % (word, variant)

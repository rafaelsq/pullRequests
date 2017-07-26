#!/usr/bin/env PYTHONIOENCODING=UTF-8 /usr/local/bin/python
# -*- coding: utf-8 -*-

#
# API completa aqui para plugins em:
# https://github.com/matryer/bitbar/blob/master/README.md
#

import urllib2
from bs4 import BeautifulSoup

opener = urllib2.build_opener()

# 1. no console, digite o script a seguir sem dar enter; ``.split(/\n/g).map(l => l.split(/\s+/g).slice(0, 2).join("=")).join("; ")
# 2. abre o `application` e vai em cookies; dê ctrl+c em tudo
# 3. cole o os cookies entre os `` do passo 1 e dê enter.
# 4. cole o resultado abaixo ;)
opener.addheaders.append(('Cookie', 'COLE OS COOKIES AQUI'))

colors = dict(nop='#660000', ok='#006600', title='#444444', link='#AAAAAA', link_me='#222222')
base_url = "https://github.com/"
projects = ("PalcoMP3", "PalcoMP3FrontEnd", "CifraClubID")
ignore_labels = ("wip",)
me = "<USER>"

def fetch(url):
    f = opener.open(base_url + url).read()
    s = BeautifulSoup(f, "html.parser")
    lis = s.find_all("li", class_="js-issue-row")
    regs = [l for l in lis if not l.find_all("a", class_="text-red") and not [x for x in l.find_all("a", class_="label") if x.get_text().lower().strip() in ignore_labels]]
    out = []
    for r in regs:
        a = r.find("a", class_="h4")
        out.append((a.get_text().strip(), a.get("href"), r.find("a", class_="muted-link").get_text()))

    return out

ends = {}
count = 0
for end in projects:
    ends[end] = fetch("StudioSol/%s/pulls" % end)
    count += len([True for (_, _, user) in ends[end] if user != me])

print "PRs %d | color=%s" % (count, colors['nop'] if count > 0 else colors['ok'])
print "---"
for k, v in ends.iteritems():
    print "%s | color=%s href=%sStudiosol/%s/pulls" % (k, colors['title'], base_url, k)
    if v:
        for (title, href, user) in v:
            print " %s (@%s) | color=%s href=%s%s" % (title, user, colors['link_me'] if me == user else colors['link'], base_url, href)
    print "---"

print "Refresh | refresh=true"

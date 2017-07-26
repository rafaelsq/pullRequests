#!/usr/bin/env PYTHONIOENCODING=UTF-8 /usr/local/bin/python
# -*- coding: utf-8 -*-

#
# API completa aqui para plugins em:
# https://github.com/matryer/bitbar/blob/master/README.md
#

import urllib2
from bs4 import BeautifulSoup

opener = urllib2.build_opener()
opener.addheaders.append(('Cookie', 'seus cookies aqui :P'))

base_url = "https://github.com/"
projects = ("PalcoMP3", "PalcoMP3FrontEnd", "CifraClubID")

def fetch(url):
    f = opener.open(base_url + url).read()
    s = BeautifulSoup(f, "html.parser")
    lis = s.find_all("li", class_="js-issue-row")
    regs = [l for l in lis if not l.find_all("a", class_="text-red") and not [x for x in l.find_all("a", class_="label") if x.get_text().lower().strip() == "wip"]]
    out = []
    for r in regs:
        a = r.find("a", class_="h4")
        out.append((a.get_text().strip(), a.get("href")))

    return out

ends = {}
count = 0
for end in projects:
    ends[end] = fetch("StudioSol/%s/pulls" % end)
    count += len(ends[end])

cr = ['#666666', '#660000', '#006600']
print "PRs %d | color=%s" % (count, cr[1 if count > 0 else 2])
print "---"
for k, v in ends.iteritems():
    if v:
        print "%s | color=%s href=%sStudiosol/%s/pulls" % (k, cr[0], base_url, k)
        for (title, href) in v:
            print "%s | href=%s%s" % (title, base_url, href)
        print "---"

print "Refresh | refresh=true"

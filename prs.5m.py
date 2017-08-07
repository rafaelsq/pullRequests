#!/usr/bin/env PYTHONIOENCODING=UTF-8 /usr/local/bin/python
# -*- coding: utf-8 -*-


import urllib2
from bs4 import BeautifulSoup

# 1. no console, digite o script a seguir sem dar enter; ``.split(/\n/g).map(l => l.split(/\s+/g).slice(0, 2).join("=")).join("; ")
# 2. abre o `application` e vai em cookies; dê ctrl+c em tudo
# 3. cole o os cookies entre os `` do passo 1 e dê enter.
# 4. cole o resultado abaixo ;)
COOKIES = 'MY_COOKIES'
me = "MY_USER_NAME"

projects = ("PalcoMP3", "PalcoMP3FrontEnd", "CifraClubID")
ignore_labels = ("wip",)
owner = 'StudioSol'

colors = dict(nop='#660000', ok='#006600', title='#FFFFFF', link='#666666', link_me='#222222')
imgs = dict(
    red='iVBORw0KGgoAAAANSUhEUgAAAAoAAAAQCAYAAAAvf+5AAAAA1klEQVQoU83Ry03DQBRA0TOWsocOUoLpIHTgEhwJR+ycVEDoIOxQzCIdQAekBJfgPhAeNDiJDGLhJW81nzvvcyeYGOEvriJvaMd3YUURqQPtnk1FibJh8QOs6D7IZxzQBeoR0PUsXziGiiNeUxYsw/BgHmkDeSQ2XIc7FhnvkaeGdcnVjG1aV+xShcjNBcTjnu24r9Wwf+i5/Q/geZhxj+dhvntMegJvSU9G8UyX4Hvm/XB+iBQJvAiP7JLcBJ601Rmbz5Ts9IVrtMnd79LIw+BzWkwGvwAVBlT6zNjR1wAAAABJRU5ErkJggg==',
    green='iVBORw0KGgoAAAANSUhEUgAAAAoAAAAQCAYAAAAvf+5AAAAA2UlEQVQoU83SzW3CQBBA4W8tcU86oASnA9KBSwApRrkZKgjpwLlFOAc6IB2EElyC+4jijbwIYSIOHLOn/Xm7M/N2ghtHuMqVco12fBYsFaJK0NpaK80x15hdgqXOt9zEDp2gGgGd3sKHQ1A6YJ9eYSGkC1NRK8hFUeM+eDKT+RK9aazM3ZnYpHmpThGihzPIq63NRXHLtH7Re/wX4KmYcZKnYlKOg57gM+nJFN51iX021af9nagYwLPwqB7kJvCorZJZ+xmEH79whTa5+xuaXFBfb4ornXIz+AvvblT6LJdT/QAAAABJRU5ErkJggg=='
)
base_url = "https://github.com/"

opener = urllib2.build_opener()

opener.addheaders.append(('Cookie', COOKIES))

def fetch(url):
    f = opener.open(base_url + url).read()
    s = BeautifulSoup(f, "html.parser")
    lis = s.find_all("li", class_="js-issue-row")
    out = []
    for r in lis:
        a = r.find("a", class_="h4")

        out.append(dict(
            title=a.get_text().strip(),
            href=a.get("href"),
            green=bool(r.find("a", class_="text-green")),
            red=bool(r.find("a", class_="text-red")),
            user=r.find("a", class_="muted-link").get_text(),
            tags=[x.get_text().lower().strip() for x in r.find_all("a", class_="label")]
        ))

    return out

ends = {}
count = 0
for end in projects:
    ends[end] = fetch("%s/%s/pulls" % (owner, end))
    count += len([True for r in ends[end] if r['user'] != me])

print "%s | color=%s image=%s" % (count if count else '', colors['nop'] if count > 0 else colors['ok'], imgs['red' if count else 'green'])
print "---"
for k, v in ends.iteritems():
    print "%s | color=%s href=%s%s/%s/pulls" % (k, colors['title'], base_url, owner, k)
    if v:
        for r in v:
            color = colors['link']
            u = " (@%s)" % r['user']
            if me == r['user']:
                u = ""
                if r['green']:
                    color = colors['ok']
                elif r['red']:
                    color = colors['nop']
                else:
                    color = colors['link_me'] 
            elif r['red'] or set(r['tags']).intersection(ignore_labels):
                continue

            print "%s%s | color=%s href=%s%s" % (r['title'], u, color, base_url, r['href'])
    print "---"

print "Refresh | refresh=true"
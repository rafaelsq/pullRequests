#!/usr/bin/env PYTHONIOENCODING=UTF-8 python
# -*- coding: utf-8 -*-

import json
import urllib2

# https://github.com/settings/tokens with 'repo' perms
github_api_key = 'TOKEN'

me = 'USER'
ignore_labels = ('WIP',)
owner = 'StudioSol'
repositories = ('PalcoMP3', 'PalcoMP3FrontEnd', 'CifraClubID')
colors = dict(nop='#660000', ok='#006600', title='#FFFFFF', link='#666666', link_me='#222222')

imgs = dict(
    red='iVBORw0KGgoAAAANSUhEUgAAAAoAAAAQCAYAAAAvf+5AAAAA1klEQVQoU83Ry03DQBRA0TOWsocOUoLpIHTgEhwJR+ycVEDoIOxQzCIdQAekBJfgPhAeNDiJDGLhJW81nzvvcyeYGOEvriJvaMd3YUURqQPtnk1FibJh8QOs6D7IZxzQBeoR0PUsXziGiiNeUxYsw/BgHmkDeSQ2XIc7FhnvkaeGdcnVjG1aV+xShcjNBcTjnu24r9Wwf+i5/Q/geZhxj+dhvntMegJvSU9G8UyX4Hvm/XB+iBQJvAiP7JLcBJ601Rmbz5Ts9IVrtMnd79LIw+BzWkwGvwAVBlT6zNjR1wAAAABJRU5ErkJggg==',
    green='iVBORw0KGgoAAAANSUhEUgAAAAoAAAAQCAYAAAAvf+5AAAAA2UlEQVQoU83SzW3CQBBA4W8tcU86oASnA9KBSwApRrkZKgjpwLlFOAc6IB2EElyC+4jijbwIYSIOHLOn/Xm7M/N2ghtHuMqVco12fBYsFaJK0NpaK80x15hdgqXOt9zEDp2gGgGd3sKHQ1A6YJ9eYSGkC1NRK8hFUeM+eDKT+RK9aazM3ZnYpHmpThGihzPIq63NRXHLtH7Re/wX4KmYcZKnYlKOg57gM+nJFN51iX021af9nagYwLPwqB7kJvCorZJZ+xmEH79whTa5+xuaXFBfb4ornXIz+AvvblT6LJdT/QAAAABJRU5ErkJggg=='
)

query = '''
{%s}

fragment comparisonFields on Repository {
  url
  pullRequests(last: 100, states: OPEN) {
    edges {
      node {
        title
        url
        author {
          login
        }
        labels(first: 10) {
          edges {
            node {
              name
            }
          }
        }
        commits(last: 1) {
          edges {
            node {
              commit {
                status {
                  state
                }
              }
            }
          }
        }
      }
    }
  }
}
''' % (' '.join(['%s: repository(owner: "%s", name: "%s") { ...comparisonFields }' % (repository, owner, repository) for repository in repositories]), )

def make_github_request(url, query):
    request = urllib2.Request(url, headers={'Authorization': 'token ' + github_api_key})
    response = urllib2.urlopen(request, json.dumps(dict(query=query)))
    return json.load(response) if response.headers.get('content-length', 0) > 0 else {}

repos = make_github_request("https://api.github.com/graphql", query=query)['data']

lines = [u"---"]
countPRs = 0
for repository, repo in repos.iteritems():
    lines.append(u"%s | color=%s href=%s/pulls" % (repository, colors['title'], repo['url']))

    for pr in repo['pullRequests']['edges']:
        color = colors['link']
        u = u" (@%s)" % pr['node']['author']['login']
        status = pr['node']['commits']['edges'][0]['node']['commit']['status']
        tags = [l['node']['name'] for l in pr['node']['labels']['edges']]

        if me == pr['node']['author']['login']:
            u = ""
            color = colors['link_me'] 
            if status and status['state'] == "SUCCESS":
                color = colors['ok']
            elif status and status['state'] in ("FAILURE", "ERROR"):
                color = colors['nop']
        elif (not status or status['state'] in ("FAILURE", "ERROR")) or set(tags).intersection(ignore_labels):
            continue

        countPRs += 1
        lines.append(u"%s%s | color=%s href=%s" % (pr['node']['title'], u, color, pr['node']['url']))
    lines.append(u"---")

lines.append(u"Refresh | refresh=true")

lines.insert(0, u"%s | color=%s image=%s" % (
    countPRs if countPRs else '', colors['nop'] if countPRs > 0 else colors['ok'], imgs['red' if countPRs else 'green']))

print u"\n".join(lines)
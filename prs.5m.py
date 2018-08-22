#!/usr/bin/env PYTHONIOENCODING=UTF-8 python
# -*- coding: utf-8 -*-

# <bitbar.title>GitHub Pull Requests</bitbar.title>
# <bitbar.version>v1.0</bitbar.version>
# <bitbar.author>Rafael Quintela</bitbar.author>
# <bitbar.author.github>rafaelsq</bitbar.author.github>
# <bitbar.desc>Show github pull requests for the projects you follow</bitbar.desc>
# <bitbar.image></bitbar.image>
# <bitbar.dependencies>python</bitbar.dependencies>
# <bitbar.abouturl></bitbar.abouturl>

import re
import json
import urllib2


# https://github.com/settings/tokens with 'repo' perms
github_api_key = 'TOKEN'

me = 'USER'
ignore_labels = ('WIP',)

# to use github Approvals; repositories = (('rafaelsq/pullRequests', True), ...)
repositories = ('rafaelsq/pullRequests', )
colors = dict(nop='#660000', ok='#006600', normal='#666666', title='#FFFFFF', link='#666666', link_me='#222222', wait='#DBAB09')

imgs = dict(
    red='iVBORw0KGgoAAAANSUhEUgAAAAoAAAAQCAYAAAAvf+5AAAAA1klEQVQoU83Ry03DQBRA0TOWsocOUoLpIHTgEhwJR+ycVEDoIOxQzCIdQAekBJfgPhAeNDiJDGLhJW81nzvvcyeYGOEvriJvaMd3YUURqQPtnk1FibJh8QOs6D7IZxzQBeoR0PUsXziGiiNeUxYsw/BgHmkDeSQ2XIc7FhnvkaeGdcnVjG1aV+xShcjNBcTjnu24r9Wwf+i5/Q/geZhxj+dhvntMegJvSU9G8UyX4Hvm/XB+iBQJvAiP7JLcBJ601Rmbz5Ts9IVrtMnd79LIw+BzWkwGvwAVBlT6zNjR1wAAAABJRU5ErkJggg==',
    green='iVBORw0KGgoAAAANSUhEUgAAAAoAAAAQCAYAAAAvf+5AAAAA2UlEQVQoU83SzW3CQBBA4W8tcU86oASnA9KBSwApRrkZKgjpwLlFOAc6IB2EElyC+4jijbwIYSIOHLOn/Xm7M/N2ghtHuMqVco12fBYsFaJK0NpaK80x15hdgqXOt9zEDp2gGgGd3sKHQ1A6YJ9eYSGkC1NRK8hFUeM+eDKT+RK9aazM3ZnYpHmpThGihzPIq63NRXHLtH7Re/wX4KmYcZKnYlKOg57gM+nJFN51iX021af9nagYwLPwqB7kJvCorZJZ+xmEH79whTa5+xuaXFBfb4ornXIz+AvvblT6LJdT/QAAAABJRU5ErkJggg==',
    grey='iVBORw0KGgoAAAANSUhEUgAAAAgAAAAOCAYAAAASVl2WAAAA6UlEQVQoU62QPUoEQRCF3+vIxNDIA4gXMDDSSFNBNh5humaEFTQxWMFcIwMVpoeRwcyfAxgIxh5B8BATCtL9pIU12A02scKqj3o/xILh7L0oiqW+77+me5pZCWDbOXeaUloGMA4hjP8A7/07yUNJ5wA2Sa4A+JZ0PwxDlT88SlqTdOKc25e0DuCa5LOkDXrvRyQfQgi/fqqq2m2a5sXMBGA0B0y1/xEws0tJeyQnIYSnLFGW5ZZz7krSR07xCuBMUt227UEGzOyW5F1K6Sab3CF5HGM86rruMwN1Xa/GGC8kvc1VPVv9QuAH2FB08Dh1TaoAAAAASUVORK5CYII='
)

reps = dict([(r, False) if not isinstance(r, tuple) else r for r in repositories])
query = '''
{%s}

fragment comparisonFields on Repository {
  owner {
    login
  }
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
        mergeable
        reviews(first:10, states:APPROVED) {
            edges {
                node {
                    state
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
''' % (' '.join(['%s: repository(owner: "%s", name: "%s") { ...comparisonFields }' % (
    (repository.split("/")[1], ) + tuple(repository.split("/"))) for repository in reps.keys()]), )

def make_github_request(url, query):
    request = urllib2.Request(url, headers={'Authorization': 'token ' + github_api_key})
    response = urllib2.urlopen(request, json.dumps(dict(query=query)))
    return json.load(response) if response.headers.get('content-length', 0) > 0 else {}

repos = make_github_request("https://api.github.com/graphql", query=query)['data']

lines = [u"---"]
countPRs = 0
countPRsApproved = 0
showGreenIco = False
showRedIco = False
for repository, repo in repos.iteritems():
    lines.append(u"%s | color=%s href=%s/pulls" % (repository, colors['title'], repo['url']))
    own = repo['owner']['login'] + '/' + repository

    for pr in repo['pullRequests']['edges']:
        color = colors['link']
        u = u" (@%s)" % pr['node']['author']['login']
        status = pr['node']['commits']['edges'][0]['node']['commit']['status']
        tags = [l['node']['name'] for l in pr['node']['labels']['edges']]
        ico = False

        brokenHeart = [':broken_heart: ', ''][pr['node']['mergeable'] == "MERGEABLE"]
        approvals = len(pr['node']['reviews']['edges'])
        if me == pr['node']['author']['login']:
            countPRs += 1
            u = ""
            color = colors['link_me']
            if status and status['state'] == "SUCCESS":
                color = colors['ok']
                if approvals < 2:
                    color = colors['wait']
                elif approvals > 1:
                    countPRsApproved += 1
                    showGreenIco = True
            elif (status and status['state'] in ("FAILURE", "ERROR")) or (status and not status['context']):
                color = colors['nop']
                showRedIco = True

            if brokenHeart:
                color = colors['nop']
                showRedIco = True
        elif (not status or status['state'] in ("FAILURE", "ERROR")) or set(tags).intersection(ignore_labels):
            continue
        elif status and status['state'] == "SUCCESS" and approvals > 1:
            ico = True

        lines.append(u"%s%s%s | color=%s href=%s image=%s" % (brokenHeart, pr['node']['title'].replace("|", " "), u, color, pr['node']['url'], imgs['green'] if ico else ''))
    lines.append(u"---")

lines.append(u"Refresh | refresh=true")

lines.insert(0, u"%s%d| color=%s image=%s" % (
    countPRsApproved + "/" if countPRsApproved else "",
    countPRs or "",
    colors['nop'] if showRedIco else (colors['ok'] if showGreenIco else colors['normal']),
    imgs['red']  if showRedIco else (imgs['gree'] if showGreenIco else imgs['grey']),
))

print u"\n".join(lines)

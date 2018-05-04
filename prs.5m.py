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

# to force LGTM(it has a bug); repositories = (('rafaelsq/pullRequests', True), ...)
repositories = ('rafaelsq/pullRequests', )
colors = dict(nop='#660000', ok='#006600', title='#FFFFFF', link='#666666', link_me='#222222', wait='#DBAB09')

imgs = dict(
    red='iVBORw0KGgoAAAANSUhEUgAAAAoAAAAQCAYAAAAvf+5AAAAA1klEQVQoU83Ry03DQBRA0TOWsocOUoLpIHTgEhwJR+ycVEDoIOxQzCIdQAekBJfgPhAeNDiJDGLhJW81nzvvcyeYGOEvriJvaMd3YUURqQPtnk1FibJh8QOs6D7IZxzQBeoR0PUsXziGiiNeUxYsw/BgHmkDeSQ2XIc7FhnvkaeGdcnVjG1aV+xShcjNBcTjnu24r9Wwf+i5/Q/geZhxj+dhvntMegJvSU9G8UyX4Hvm/XB+iBQJvAiP7JLcBJ601Rmbz5Ts9IVrtMnd79LIw+BzWkwGvwAVBlT6zNjR1wAAAABJRU5ErkJggg==',
    green='iVBORw0KGgoAAAANSUhEUgAAAAoAAAAQCAYAAAAvf+5AAAAA2UlEQVQoU83SzW3CQBBA4W8tcU86oASnA9KBSwApRrkZKgjpwLlFOAc6IB2EElyC+4jijbwIYSIOHLOn/Xm7M/N2ghtHuMqVco12fBYsFaJK0NpaK80x15hdgqXOt9zEDp2gGgGd3sKHQ1A6YJ9eYSGkC1NRK8hFUeM+eDKT+RK9aazM3ZnYpHmpThGihzPIq63NRXHLtH7Re/wX4KmYcZKnYlKOg57gM+nJFN51iX021af9nagYwLPwqB7kJvCorZJZ+xmEH79whTa5+xuaXFBfb4ornXIz+AvvblT6LJdT/QAAAABJRU5ErkJggg=='
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
        comments(first: 100) {
            edges {
                node {
                    bodyText
                }
            }
        }
        commits(last: 1) {
          edges {
            node {
              commit {
                status {
                  state
                  context(name: "approvals/lgtm") {
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
showGreenIco = False
showRedIco = False
LGTM = re.compile(r'(^|\s|[,\.])lgtm($|\s|[,\.])', re.I)
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
        lgtm = 0
        if reps[own]:
            for msg in pr['node']['comments']['edges']:
                if LGTM.search(msg['node']['bodyText']):
                    lgtm += 1
        if me == pr['node']['author']['login']:
            u = ""
            color = colors['link_me']
            if status and status['state'] == "SUCCESS":
                color = colors['ok']
                if lgtm < 2:
                    color = colors['wait']
                showGreenIco = True
            elif (status and status['state'] in ("FAILURE", "ERROR")) or not status or not status['context']:
                color = colors['nop']
                showRedIco = True

            if brokenHeart:
                color = colors['nop']
                showRedIco = True
        elif (not status or status['state'] in ("FAILURE", "ERROR")) or set(tags).intersection(ignore_labels):
            continue
        elif status and status['state'] == "SUCCESS" and lgtm > 1:
            ico = True

        countPRs += 1
        lines.append(u"%s%s%s | color=%s href=%s image=%s" % (brokenHeart, pr['node']['title'].replace("|", " "), u, color, pr['node']['url'], imgs['green'] if ico else ''))
    lines.append(u"---")

lines.append(u"Refresh | refresh=true")

if showRedIco or showGreenIco:
    lines.insert(0, u"%s | color=%s image=%s" % (countPRs, colors['nop'] if showRedIco else colors['ok'], imgs['red' if showRedIco else 'green']))
else:
    lines.insert(0, u"PRs %s | color=%s image=" % (countPRs, colors['ok']))

print u"\n".join(lines)

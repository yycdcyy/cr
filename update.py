import json
import os
import re
import requests
import settings
import time


def api(url):
    headers = {
        'auth': settings.TOKEN,
    }
    response = requests.request("GET", url, headers=headers)
    assert 200 == response.status_code, url
    data = response.json()
    return data


def clan():
    url = "https://api.royaleapi.com/clan/{:s}".format(settings.CLAN)
    return api(url)


def history(days=7):
    url = "https://api.royaleapi.com/clan/{:s}/history?days={:d}".format(settings.CLAN, days)
    return api(url)


def war_log():
    url = "https://api.royaleapi.com/clan/{}/warlog".format(settings.CLAN)
    return api(url)


def history_local():
    t2fn = dict()
    r = re.compile(r'^clan-(\d+).json$')
    for filename in os.listdir('history'):
        m = r.match(filename)
        if m:
            t2fn[int(m.group(1))] = os.path.join('history', filename)
    all_t = sorted(t2fn.keys())
    ts = list()
    for t in all_t:
        if t < time.time() - 86400 * 14:
            continue
        if len(ts) == 0 or t > ts[-1] + 10 * 60:
            ts.append(t)

    member_struct = {
        'tag': str,
        'trophies': int,
        'donations': int,
        'donationsReceived': int,
        'donationsPercent': float,
    }

    def cleanup(d, target):
        if isinstance(target, type):
            assert isinstance(d, target)
        else:
            assert type(d) is type(target)
            if isinstance(target, dict):
                for key in list(d.keys()):
                    if key in target:
                        cleanup(d[key], target[key])
                    else:
                        del d[key]
            elif isinstance(target, list):
                for v in d:
                    cleanup(v, target[0])
        return d

    def read(filename):
        with open(filename) as f:
            data = json.load(f)
        print(data.keys())
        return cleanup(data, {
            'members': [member_struct],
        })

    return [{
        'time': t,
        'clan': read(t2fn[t]),
    } for t in ts]


if __name__ == '__main__':
    data = {
        'now': time.time(),
        'clan': clan(),
        'history': history_local(),
        'war_log': war_log(),
    }
    with open(os.path.join('www', 'data', 'data.js'), 'w') as f:
        f.write('/**/;var data = ')
        json.dump(data, f)
        f.write(';')

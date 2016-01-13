#!/usr/bin/env python
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import json
import sys
import yaml

parser = argparse.ArgumentParser(description='Merge and convert yaml to json.')
parser.add_argument('files', metavar='F', type=str, nargs='+',
                    help='file to process')

args = parser.parse_args()


def dict_merge(a, b):
    for k, v in b.items():
        if isinstance(v, dict):
            n = a.setdefault(k, {})
            dict_merge(n, v)
        else:
            a[k] = v
    return a

merge = {}
for f in args.files:
    merge = dict_merge(merge, yaml.load(open(f))['assets'])

y = yaml.load(sys.stdin)
for a in y['assets']:
    s = a['service']
    if s['type'] == 'heat':
        if 'environment' in s:
            s['environment'] = yaml.dump(s['environment'])
    if a['name'] in merge:
        dict_merge(a, merge[a['name']])
y = [a for a in y['assets'] if a.get('active', True)]
y = {'assets': y}
json.dump(y, sys.stdout)

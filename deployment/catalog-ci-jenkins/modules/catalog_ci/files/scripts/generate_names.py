#!/usr/bin/python
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import itertools
import re
from sys import argv
import yaml


def yaml_to_dict(infile, k):
    stream = open(infile, 'r')
    rdict = yaml.load(stream)[k]
    return rdict


def diff_images_config(images1, images2):
    if images1 == images2:
        return ''
    intersec = [item for item in images1 if item in images2]
    sym_diff = [item for item in itertools.chain(
        images1, images2) if item not in intersec]
    name = ''
    d_size = len(sym_diff)
    if d_size <= 2:
        i = d_size - 1
    else:
        return ''

    if 'name' in sym_diff[i].keys() and 'format' in sym_diff[i].keys():
        i_name = re.sub('[(){}<>]', '', sym_diff[i]['name'])
        i_type = sym_diff[i]['format']
        name = i_name + '.' + i_type
        name = name.lower().replace(" ", "_")
    return name

if __name__ == '__main__':
    if argv[1] == 'glance':
        images1 = yaml_to_dict(argv[2], 'images')
        images2 = yaml_to_dict(argv[3], 'images')
        print(diff_images_config(images1, images2))

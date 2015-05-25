#!/usr/bin/python

import re
import yaml
from sys import argv


def yaml_to_dict(infile, k):
    stream = open(infile, 'r')
    rdict = yaml.load(stream)[k]
    return rdict


def diff_images_config(images1, images2):
    if images1 == images2:
        return
    import itertools
    import re
    intersec = [item for item in images1 if item in images2]
    sym_diff = [item for item in itertools.chain(images1,images2) if item not in intersec]
    name = ''
    d_size = len(sym_diff)
    if d_size <= 2:
      i = d_size -1
    else:
      return ''

    if 'name' in sym_diff[i].keys() and 'format' in sym_diff[i].keys():
       i_name  = re.sub('[(){}<>]', '', sym_diff[i]['name'])
       i_type  = sym_diff[i]['format']
       name = i_name + '.' + i_type
       name = name.lower().replace (" ", "_")
    return name

if __name__ == '__main__':
    if argv[1] == 'glance':
        images1 = yaml_to_dict(argv[2], 'images')
        images2 = yaml_to_dict(argv[3], 'images')
        print(diff_images_config(images1, images2))

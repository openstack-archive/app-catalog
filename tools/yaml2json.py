#!/usr/bin/env python

import sys
import json
import yaml

json.dump(yaml.load(sys.stdin), sys.stdout)

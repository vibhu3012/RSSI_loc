'''
Core package for RSSI indoor localization
Sampler.py
APseletor.py
RPcluster.py
Discrete.py
'''

import logging as lg
from logging import debug, info, warning, error, critical
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
DATE_FORMAT = "%H:%M:%S"
lg.basicConfig(level = DEBUG, format=LOG_FORMAT, datefmt=DATE_FORMAT)

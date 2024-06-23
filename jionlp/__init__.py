__version__ = '1.5.12'

import os

from jionlp.util.logger import set_logger
from jionlp.util.zip_file import unzip_file, UNZIP_FILE_LIST

logging = set_logger(level='INFO', log_dir_name='.cache/jionlp_logs')

# unzip dictionary files
DIR_PATH = os.path.dirname(os.path.abspath(__file__))
for file_name in UNZIP_FILE_LIST:
    if not os.path.exists(os.path.join(DIR_PATH, 'dictionary', file_name)):
        zip_file = '.'.join(file_name.split('.')[:-1]) + '.zip'
        unzip_file(zip_file)

from jionlp.util import *
from jionlp.dictionary import *
from jionlp.rule import *

from jionlp.gadget import *
from jionlp.textaug import *
from jionlp.algorithm import *

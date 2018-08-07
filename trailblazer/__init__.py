import os
import logging

log = logging.getLogger('trailblazer')
log.setLevel(os.environ.get('TRAILBLAZER_LOG_LEVEL', 'DEBUG'))

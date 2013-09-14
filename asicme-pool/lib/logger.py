from __future__ import print_function

import datetime
import time
import settings


scope_to_f = {}

def log(scope, *args):
    if(settings.LOG_ROLL):
        if(scope != 'block' and scope != 'submitblock' and scope != 'error'):
            suffix = time.strftime('%Y%m%d',time.localtime(time.time()))
            scope = scope + '.' + suffix

    if scope not in scope_to_f:
        scope_to_f[scope] = open('logs/%s.log' % scope, 'a+')
    print(str(datetime.datetime.now()), *args, file=scope_to_f[scope])
    scope_to_f[scope].flush()

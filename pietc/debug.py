from contextlib import contextmanager

DEBUG = True

# uncomment filters to print their debug info.
active_prefixes = [
    'simulating',
    # 'evaluating',
    # 'executing',
    # 'lambda call',
    # 'sequence call',
    # 'conditional call',
]

@contextmanager
def debugcontext (state=True):
    global active_prefixes
    prefixes = active_prefixes
    if not state:
        active_prefixes = []
    yield None
    active_prefixes = prefixes

def debuginfo (form, *args, prefix=''):
    if DEBUG and prefix in active_prefixes:
        print('{}: {}'.format(prefix, form.format(*args)))

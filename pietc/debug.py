DEBUG = True

# uncomment filters to print their debug info.
FILTERED_PREFIXES = [
    'broadcast',
    'evaluating',
    'executing',
    'lambda call',
    'sequence call',
    'conditional call',
]

def debuginfo (form, *args, prefix=''):
    if DEBUG and not prefix in FILTERED_PREFIXES:
        print('{}: {}'.format(prefix, form.format(*args)))

DEBUG = True

# uncomment filters to print their debug info.
active_prefixes = [
    # 'evaluating',
    # 'executing',
    'simulating',
    # 'lambda call',
    # 'sequence call',
    # 'conditional call',
]

def debuginfo (form, *args, prefix=''):
    if DEBUG and prefix in active_prefixes:
        print('{}: {}'.format(prefix, form.format(*args)))

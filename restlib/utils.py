def uncamel(s):
    """Uncamel-cases a string. Returns a list of the parts.

    >>> uncamel('') == []
    True
    >>> uncamel('Foo') == ['Foo']
    True
    >>> uncamel('FooBar') == ['Foo', 'Bar']
    True
    """
    toks, tmp = [], ''
    for i, x in enumerate(s):
        if x.isupper() and i:
            toks.append(tmp)
            tmp = ''
        tmp += x
    if tmp:
        toks.append(tmp)
    return toks

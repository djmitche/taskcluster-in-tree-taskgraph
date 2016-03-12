# TODO: base this on the moz.build sandbox (but don't import that, as
# it, and especially Context, are fairly specific to moz.build files)
class Sandbox(dict):
    def __init__(self, context):
        self._context = context
        self._builtins = {
            'None': None,
            'False': False,
            'True': True,
            'sorted': sorted,
            'int': int
        }
        dict.__setitem__(self, '__builtins__', self._builtins)

    def exec_file(self, path):
        source = open(path).read()
        code = compile(source, path, 'exec')
        exec code in self

    def __getitem__(self, key):
        if key.isupper():
            return self._context[key]
        return dict.__getitem__(self, key)

    def __setitem__(self, key, value):
        if key in self._builtins or key == '__builtins__':
            raise KeyError('Cannot reassign builtins')

        if key.isupper():
            if key in self._context and self._context[key] is not value:
                raise KeyError('global_ns', 'reassign', key)
            self._context[key] = value
        else:
            dict.__setitem__(self, key, value)

    def get(self, key, default=None):
        raise NotImplementedError('Not supported')

    def __len__(self):
        raise NotImplementedError('Not supported')

    def __iter__(self):
        raise NotImplementedError('Not supported')

    def __contains__(self, key):
        if key.isupper():
            return key in self._context
        return dict.__contains__(self, key)

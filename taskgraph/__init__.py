from __future__ import print_function
import os
import sandbox

def load_kind(path):
    context = {}
    sb = sandbox.Sandbox(context)
    sb.exec_file(os.path.join(path, 'kind.py'))

    # load the class defined by IMPLEMENTATION
    try:
        impl = context['IMPLEMENTATION']
    except KeyError:
        raise KeyError("{!r} does not define IMPLEMENTATION".format(path))
    if impl.count(':') != 1:
        raise TypeError('{!r} IMPLEMENTATION does not have the form "module:object"'
                        .format(path))

    impl_module, impl_object = impl.split(':')
    impl_class = __import__(impl_module)
    for a in impl_module.split('.')[1:]:
        impl_class = getattr(impl_class, a)
    for a in impl_object.split('.'):
        impl_class = getattr(impl_class, a)

    return impl_class(path, context)
        

def get_task_set(root):
    taskset = {}
    for subdir in os.listdir(root):
        path = os.path.join(root, subdir)
        if subdir.startswith('.') or not os.path.isdir(path):
            continue
        kind = load_kind(os.path.join(root, subdir))
        taskset.update(kind.load_tasks())
    return taskset

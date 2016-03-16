from __future__ import print_function
import os
import sandbox
import functools

from taskgraph.types import Task, TaskGraph

def memoized_property(f):
    @functools.wraps(f)
    def wrap(self):
        try:
            return f.return_value
        except AttributeError:
            rv = f(self)
            f.return_value = rv
            return rv
    return property(wrap)


class TaskGraphGenerator(object):
    """
    The central controller for taskgraph.  This handles all phases of graph
    generation.
    """

    def __init__(self, root):
        self.root = root


    @memoized_property
    def kinds(self):
        """
        All defined kinds.

        @type: dictionary mapping kind name to Kind instance
        """
        kinds = {}
        for path in os.listdir(self.root):
            path = os.path.join(self.root, path)
            if not os.path.isdir(path):
                continue
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

            kinds[os.path.basename(path)] = impl_class(path, context)
        return kinds


    @memoized_property
    def full_task_set(self):
        """
        The full task set: all tasks defined by any kind

        @type: TaskGraph (with no edges)
        """

        graph = TaskGraph()
        for kind in self.kinds.itervalues():
            for task in kind.load_tasks():
                graph.add_task(task)
        return graph

    @memoized_property
    def full_task_graph(self):
        """
        The full task graph: the full task set, but linked with dependency edges
        """
        taskgraph = self.full_task_set
        for t in taskgraph:
            t.dependencies = t.kind.get_task_dependencies(t, taskgraph)
        return taskgraph

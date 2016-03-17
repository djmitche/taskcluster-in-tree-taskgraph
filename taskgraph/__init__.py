from __future__ import print_function
import os
import sandbox
import functools

from taskgraph.types import Task, TaskGraph
from taskgraph.util import taskexpr

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

    def __init__(self, root, target_expression, optimization_finder):
        self.root = root
        self.target_expression = target_expression
        self.optimization_finder = optimization_finder


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

        @type: list of Tasks
        """

        taskset = []
        for kind in self.kinds.itervalues():
            for task in kind.load_tasks():
                taskset.append(task)
        return taskset

    @memoized_property
    def full_task_graph(self):
        """
        The full task graph: the full task set, but linked with dependency edges

        @type: TaskGraph
        """
        taskset = self.full_task_set
        taskgraph = TaskGraph()
        for t in taskset:
            taskgraph.add_task(t)
        for t in taskset:
            t.dependencies = t.kind.get_task_dependencies(t, taskgraph)
        return taskgraph

    @memoized_property
    def target_task_set(self):
        """
        The set of targetted tasks

        @type: list of Tasks
        """
        return [t for t in self.full_task_graph
                if taskexpr.evaluate(self.target_expression, task=t)]

    @memoized_property
    def target_task_graph(self):
        return self.full_task_graph.transitive_closure(self.target_task_set)

    @memoized_property
    def optimized_task_graph(self):
        taskgraph = self.target_task_graph
        def visit(task):
            task.optimization_key = task.kind.get_task_optimization_key(task, taskgraph)
        taskgraph.depth_first(visit)

        # look up all tasks in the index at once
        optimization_keys = filter(None, (t.optimization_key for t in taskgraph))
        optimizations = self.optimization_finder(optimization_keys)

        # assign the taskId for each task that has been successfully optimized away
        for task in taskgraph:
            task_id = optimizations.get(task.optimization_key)
            if task_id:
                task.task_id = task_id

        # now replace any dependencies on tasks that have been optimized away with
        # a direct dependency on the taskId TODO link this properly, rather than relying
        # on KeyError
        def replace(label, name):
            task_id = taskgraph[label].task_id
            if task_id:
                return task_id, name
            else:
                return label, name
        for task in taskgraph:
            task.dependencies = [replace(l, n) for l, n in task.dependencies]

        # re-compute the transitive closure of the subset of the graph.  Note
        # that this may include optimized tasks if they are in the
        # target_task_set.
        return taskgraph.transitive_closure(self.target_task_set)

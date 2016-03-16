import pprint

class Task(object):
    """
    Representation of a task in a TaskGraph.

    Each has:

    - kind: kind of task
    - label; the label for this task
    - attributes: a set of attributes for this task (for filtering)
    - task: the task definition
    - dependencies: the dependencies of this task, as a list of task labels
    - extra: extra kind-specific metadata
    """

    def __init__(self, kind, label, attributes=[], task={}, dependencies=[],
            **extra):
        self.kind = kind
        self.label = label
        self.attributes = attributes
        self.task = task
        self.dependencies = dependencies
        self.extra = extra

    def __repr__(self):
        return pprint.pformat({
            'kind': self.kind,
            'attributes': self.attributes,
            'task': self.task,
            'dependencies': self.dependencies,
        })


class TaskGraph(object):
    """
    Representation of a task graph.

    A task graph is a set of Tasks (nodes), each with a set of dependencies
    (edges).

    Tasks can be fetched by label.  A task's dependencies are in its
    `dependency` attribute, as a set of Task labels.
    """

    def __init__(self, tasks={}):
        self.tasks = {}
        self.tasks_by_kind = {}

    def add_task(self, task):
        if task.label in self.tasks:
            raise KeyError('Task with label {} already exists'.format(task.label))
        self.tasks[task.label] = task
        self.tasks_by_kind.setdefault(task.kind.name, {})[task.label] = task

    def __str__(self):
        return "\n".join("{}:\n{}".format(l, t) for (l, t) in self.tasks.iteritems())

    def __iter__(self):
        return self.tasks.itervalues()

import os
import abc

class Kind(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, path, context):
        self.name = os.path.basename(path)
        self.path = path
        self.context = context

    @abc.abstractmethod
    def load_tasks(self):
        """
        Get the set of tasks of this kind.

        The return value is a dictionary mapping task label to task, with tasks
        defined as Python dictionaries.
        """

    @abc.abstractmethod
    def get_task_dependencies(self, task, taskgraph):
        """
        Get the set of task labels this task depends on, by querying the task graph.

        Returns a list of (task_label, dependency_name) pairs describing the
        dependencies.
        """

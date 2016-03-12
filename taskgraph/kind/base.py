import abc

class Kind(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, path, context):
        self.path = path
        self.context = context

    @abc.abstractmethod
    def load_tasks(self):
        """
        Get the set of tasks of this kind.

        The return value is a dictionary mapping task label to task, with tasks
        defined as Python dictionaries.
        """

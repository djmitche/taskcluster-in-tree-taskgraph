import os
import yaml
import glob
from taskgraph.util import templates
from taskgraph.types import Task

class YamlLoader(object):
    """
    Load tasks specified in the TASKS variable

    Implements: load_tasks
    """

    # TODO: parameterize

    def load_tasks(self):
        if 'TASKS' not in self.context:
            raise KeyError('TASKS must be defined to load tasks')
        files = []
        for task_spec in self.context['TASKS']:
            if isinstance(task_spec, basestring):
                files.append(os.path.join(self.path, task_spec))
            ## TODO: use the **-aware globbing (mozpack.path) that moz.build does
            elif 'glob' in task_spec:
                files.extend(
                        f[len(self.path)+1:] for f in
                        glob.glob(os.path.join(self.path, task_spec['glob'])))
            else:
                raise TypeError("Invalid TASKS entry in {!r}: {!r}"
                                .format(self.path, task_spec))

        tpls = templates.Templates(self.path)
        return [Task(kind=self, label=f, **tpls.load(f)) for f in files]


class ExpressionDependencies(object):
    """
    Link tasks to their dependencies based on simple expressions either in
    self.dependencies or task.extra['dependencies']
    """

    def get_task_dependencies(self, task, taskgraph):
        dependencies = self.context.get('DEPENDENCIES', [])
        dependencies += task.extra.get('dependencies', [])

        def evaluate(expression, self, task):
            """
            Evaluate a boolean expression, which can be a string containing a
            python expression with free variables `self` and `task`, or a
            function taking arguments `self, task`
            """
            if isinstance(expression, basestring):
                return eval(expression, {'self': self, 'task': task})
            else:
                return expression(self, task)

        rv = []
        for dep in dependencies:
            # get the universe of possible target tasks
            target_tasks = taskgraph.tasks_by_kind.get(dep['kind'], {})
            where = dep.get('where') or (lambda self, task: True)
            selected_tasks = [tgt for tgt in target_tasks.itervalues()
                              if evaluate(where, task, tgt)]
            for tgt in selected_tasks:
                rv.append((tgt.label, dep['name']))
        return rv

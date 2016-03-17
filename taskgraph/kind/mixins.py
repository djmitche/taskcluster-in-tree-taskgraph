import hashlib
import os
import yaml
import glob
from taskgraph.util import templates
from taskgraph.types import Task
from taskgraph.util import taskexpr

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
        raw = {f: tpls.load(f) for f in files}
        return [Task(kind=self, label=f, task=t['task'], attributes=t.get('attributes', {}))
                for (f, t) in raw.iteritems()]


class ExpressionDependencies(object):
    """
    Link tasks to their dependencies based on simple expressions either in
    self.dependencies or task.extra['dependencies']

    Implements: `get_task_dependencies`
    """

    def get_task_dependencies(self, task, taskgraph):
        dependencies = self.context.get('DEPENDENCIES', [])
        dependencies += task.extra.get('dependencies', [])

        rv = []
        for dep in dependencies:
            # get the universe of possible target tasks
            target_tasks = taskgraph.tasks_by_kind.get(dep['kind'], {})
            where = dep.get('where') or (lambda self, task: True)
            selected_tasks = [tgt for tgt in target_tasks.itervalues()
                              if taskexpr.evaluate(where, self=task, task=tgt)]
            for tgt in selected_tasks:
                rv.append((tgt.label, dep['name']))
        return rv


class DefaultOptimizer(object):

    """
    Optimize based on the OPTIMIZATIONS context.  Each optimization type is
    defined by an `optimize_input_<type>` method, so subclasses may add custom
    types.

    Implements: `get_task_optimization_key`
    """

    def get_task_optimization_key(self, task, taskgraph):
        optimizations = [
                opt for opt in self.context.get('OPTIMIZATIONS', [])
                if taskexpr.evaluate(opt.get('where', lambda task: True), task=task)]
        if len(optimizations) > 1:
            raise RuntimeError('Task {} matches multiple optimizations ({}); tasks '
                               'much match no more than one optimization.'.format(
                                   task.label, ', '.join(o.name for o in optimizations)))
        if not optimizations:
            return None
        optimization = optimizations[0]

        # NOTE: it's important that all inputs to this hash are stable; generally that
        # means that the components of the hash are always in the same order, and use
        # the same syntax.
        m = hashlib.sha1()
        for input in optimization.get('inputs', []):
            method = getattr(self, 'optimize_input_' + input['type'].replace('-', '_'))
            update = method(input, task, taskgraph)
            m.update(update)
        rv = '{}.{}'.format(optimization['name'], m.hexdigest())
        return rv

    def optimize_input_vcs_files(self, input, task, taskgraph):
        # XXX this would do some fanciness to find the most recent revision in
        # which any of these files changed (and this would be mozilla-specific,
        # not in taskgraph)
        return 'TODO'

    def optimize_input_dependencies(self, input, task, taskgraph):
        return '\n'.join(
            taskgraph[l].optimization_key
            for l, _ in task.dependencies)

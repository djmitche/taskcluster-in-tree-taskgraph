import os
import yaml
import glob
from taskgraph.util import templates

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
        return {f: tpls.load(f) for f in files}

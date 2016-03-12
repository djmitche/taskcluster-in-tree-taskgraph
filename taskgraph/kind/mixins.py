import os
import yaml
import glob

class YamlLoader(object):
    """
    Load tasks specified in the TASKS variable

    Implements: load_tasks
    """

    def load_tasks(self):
        if 'TASKS' not in self.context:
            raise KeyError('TASKS must be defined to load tasks')
        files = []
        for task_spec in self.context['TASKS']:
            if isinstance(task_spec, basestring):
                files.append(os.path.join(self.path, task_spec))
            ## TODO: use the **-aware glob that moz.build does
            elif 'glob' in task_spec:
                files.extend(glob.glob(os.path.join(self.path, task_spec['glob'])))
            else:
                raise TypeError("Invalid TASKS entry in {!r}: {!r}"
                                .format(self.path, task_spec))

        return {f: yaml.load(open(f)) for f in files}

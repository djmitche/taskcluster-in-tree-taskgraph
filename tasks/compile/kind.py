# specify the implementation of this kind (a Python module:class reference; see tasks/lib)
IMPLEMENTATION = "taskgraph.kind.compile:CompileKind"

TASKS = [
    # TODO: allow variations here (re-parse the same file with multiple inputs)
    {"glob": "*-task.yml"}
]

# dependency dependencies (common to all kinds)
DEPENDENCIES = [
    # Linux-based builds require a docker image
    {
        "name": "linux-image",   # name for this link
        "kind": "docker-image",  # kind to which the link points
        # note this expression could also be a lambda.  "self" is the task
        # in this kind, and "task" is the task in the target kind
        "where": "self.platform in ('linux32', 'linux64', 'macosx64') "
                  "and task.image == 'desktop-test'",
    },

    # Mac builds require a pre-built clang toolchain
    {
        "name": "macosx-toolchain",
        "kind": "toolchain",
        "where": "self.platform == 'macosx64' and task.toolchain == 'macosx64-clang'",
    },
    {
        "name": "vcs",
        "kind": "vcs",
        # default "from" is all
        # default "to" is all - there is only one vcs task (which creates a bundle as an artifact)
    }
]

# variations (specific to this kind)
VARIATIONS = {
    # these will parameterize each task defintion
    "build-type": ["dbg", "opt"],
}

# criteria for replacing tasks of this kind with existing tasks
# each task must be matched by at most one optimization (via "where")
OPTIMIZATIONS = [{
    "where": "True",  # potentially replace any task
    "name": "compile",
    "inputs": [
        {'type': 'dependencies'},
        {
            'type': 'vcs-files',
            'files': [
                "compiled-files",
                "build-system",
                "mozharness",
                "compile-task-kind",
                "taskgraph",
            ],
        }
    ],
}]

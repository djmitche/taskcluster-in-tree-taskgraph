# specify the implementation of this kind (a Python module:class reference; see tasks/lib)
IMPLEMENTATION = "taskgraph.kind.compile:CompileKind"

TASKS = [
    {"glob": "*-task.yml"}
]

# dependency links (common to all kinds)
LINKS = [
    # Linux-based builds require a docker image
    {
        "name": "linux-image",   # name for this link
        "kind": "docker-image",  # kind to which the link points
        # query for tasks in this kind to link from
        "from": "task.platform in ('linux32', 'linux64', 'macosx64')",
        # query for tasks in the target kind to link to
        "to": "task.image == 'desktop-test'",
    },

    # Mac builds require a pre-built clang toolchain
    {
        "name": "macosx-toolchain",
        "kind": "toolchain",
        "from": "task.platform == 'macosx64'",
        "to": "task.toolchain == 'macosx64-clang'",
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
OPTIMIZATIONS = [{
    "for": "all",  # potentially replace any task
    "cover": {
        "links": "all",
        "vcs-last-modified": [
            "compiled-files",
            "build-system",
            "mozharness",
            "compile-task-kind",
            "taskgraph",
        ]
    }
}]
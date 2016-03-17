IMPLEMENTATION =  "taskgraph.kind.docker:DockerImageKind"

TASKS = [
    {"glob": "*-task.yml"}
]

# criteria for replacing tasks of this kind with existing tasks
OPTIMIZATIONS = [{
    "where": "True",
    "name": "docker-image",
    "inputs": [
        {'type': 'dependencies'},
        # for docker images, we want to use the directory hash so that
        # multiple try pushes with the same docker-image tweak don't all
        # trigger (very long) docker image rebuilds.  This input type is
        # specially implemented by this kind.
        {'type': 'docker-image-directory'},
        {
            'type': 'vcs-files',
            'files': [
                "docker-image-task-kind",
                "taskgraph",
            ]
        },
    ]
}]

IMPLEMENTATION =  "taskgraph.kind.docker:DockerImageKind"

TASKS = [
    {"glob": "*-task.yml"}
]

# criteria for replacing tasks of this kind with existing tasks
OPTIMIZATIONS = [{
    "for": "all",
    "cover": {
        "links": "all",
        # for docker images, we want to use the directory hash so that
        # multiple try pushes with the same docker-image tweak don't all
        # trigger (very long) docker image rebuilds
        "directory-hash": [
            # XXX not sure how interpolation will work here
            "testing/docker/{{ task.image }}",
        ],
        "vcs-last-modified": [
            "docker-image-task-kind",
            "taskgraph",
        ]
    }
}]

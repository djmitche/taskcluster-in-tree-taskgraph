from . import base, mixins

class DockerImageKind(mixins.YamlLoader, base.Kind):
    pass

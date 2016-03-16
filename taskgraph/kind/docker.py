from . import base, mixins

class DockerImageKind(mixins.YamlLoader, mixins.ExpressionDependencies, base.Kind):
    pass

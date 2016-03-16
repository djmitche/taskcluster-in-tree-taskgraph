from . import base, mixins

class CompileKind(mixins.YamlLoader, mixins.ExpressionDependencies, base.Kind):
    pass

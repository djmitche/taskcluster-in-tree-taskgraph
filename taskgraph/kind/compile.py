from . import base, mixins

class CompileKind(mixins.YamlLoader, mixins.ExpressionDependencies, mixins.DefaultOptimizer, base.Kind):
    pass

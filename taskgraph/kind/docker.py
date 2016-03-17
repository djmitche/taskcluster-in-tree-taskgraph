from . import base, mixins

class DockerImageKind(mixins.YamlLoader, mixins.ExpressionDependencies, mixins.DefaultOptimizer, base.Kind):
    
    def optimize_input_docker_image_directory(self, input, task, taskgraph):
        # XXX this would hash the contents of the directory containing the Dockerfile
        return task.attributes['image']

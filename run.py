import pprint
import taskgraph

index = {
    'compile.675bccf460bf3b62af5e38f2318e0e5eccfdb964': 'oldCompileJobTaskId',
}

def main():
    tgg = taskgraph.TaskGraphGenerator('tasks',
            'task.kind.name == "compile" and task.platform == "linux64"',
            lambda keys: index)

    print(tgg.optimized_task_graph)

if __name__ == "__main__":
    main()

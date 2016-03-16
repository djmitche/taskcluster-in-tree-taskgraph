import pprint
import taskgraph

def main():
    tgg = taskgraph.TaskGraphGenerator('tasks', 'task.kind.name == "compile" and task.platform == "linux64"')

    # step 1: For all kinds, generate all tasks. The result is the "full task set"
    print(tgg.target_task_graph)

if __name__ == "__main__":
    main()

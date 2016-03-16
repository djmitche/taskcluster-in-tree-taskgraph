import pprint
import taskgraph

def main():
    tgg = taskgraph.TaskGraphGenerator('tasks')

    # step 1: For all kinds, generate all tasks. The result is the "full task set"
    full_task_graph = tgg.full_task_graph
    print full_task_graph

if __name__ == "__main__":
    main()

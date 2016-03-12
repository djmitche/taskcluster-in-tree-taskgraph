import pprint
import taskgraph

def main():
    pprint.pprint(taskgraph.get_task_set('tasks'))

if __name__ == "__main__":
    main()

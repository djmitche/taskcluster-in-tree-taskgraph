# tl;dr

The task graph is built by linking different kinds of tasks together, pruning out tasks that are not required,
then optimizing by replacing subgraphs with links to already-completed tasks.

# Concepts

* *Task Kind* - Tasks are grouped by kind, where tasks of the same kind do not have interdependencies but have
  substantial similarities, and may depend on tasks of other kinds.  Kinds are the primary means of supporting
  diversity, in that a contributor can add a new kind to do just about anything without impacting other kinds.
* *Task Attributes* - Tasks have string attributes by which they can be queried and filtered.
* *Task Labels* - A unique identifier for the task within the graph that is stable across runs of the graph
  generation algorithm.  Labels begin with `<kind>/`.  Labels are replaced with TaskCluster TaskIds at the
  latest time possible, preventing spurious taskId changes in diffs made before that time.
* *Query Language* - A simple means of selecting subsets of tasks based on attributes.  Similar in principal
  to the [Bazel Query Language](http://bazel.io/docs/query.html).
* *Optimization* - replacement of a task in a graph with an equivalent, already-completed task, or a null
  task, avoiding repetition of work.

# Dependencies

Dependency links between tasks are always between different kinds(*).

Here is a hypothetical graph of the relationships between kinds for Gecko tests.
Note that this splits out the "compile" and "assemble" stages; this refers to artifact builds, which would only require the "assemble" stage.

![Kind Graph](https://cdn.rawgit.com/djmitche/taskcluster-in-tree-taskgraph/master/kinds.svg)

Each node in this graph contains many tasks, so each edge potentially represents _n*m_ task dependencies.
We use the query language to filter these dependencies down.
For example, from the assemble kind to the compile kind, only tasks with matching platform are connected with a dependency.

(*) A kind can depend on itself, though.  You can safely ignore that detail.
Tasks can also be generated within a kind using explicit dependencies.

# Decision Task

The decision task is the first task created when a new graph begins.
It is responsible for creating the rest of the task graph.

The decision task for pushes is defined in [`.taskcluster.yml`](/.taskcluster.yml).

We also have a number of periodic jobs:

 * nightly builds
 * periodic test runs such as [bootstrap tests](https://bugzilla.mozilla.org/show_bug.cgi?id=1245969)
 * rebuilds of toolchains and other prerequisites
 * rebuilds of docker images with up-to-date packages

All of these can be controlled from [`.cron.yml`](/.cron.yml).
A periodic task polls this file and creates tasks contained within as scheduled.

## Graph Generation

Graph generation, run via `mach taskgraph decision`, proceeds as follows:

1. For all kinds, generate all tasks.  The result is the "full task set"
1. Create links between tasks using kind-specific query expressions.  The result is the "full task graph".
1. Select the target tasks (based on try syntax or a tree-specific specification).  The result is the "target
   task set".
1. Based on the full task graph, calculate the transitive closure of the target task set.  That is, the target
   tasks and all ancestors of those tasks.  The result is the "target task graph".
1. Optimize the target task graph based on kind-specific optimization methods.  The result is the "optimized task graph".
1. Generate taskIds for all tasks in the optimized task graph.  Publish the full task graph with these taskIds included.
1. Create tasks for all tasks in the optimized task grap.

# Mach commands

A number of mach subcommands are avaialable to make this complex system more accesssible to those trying to understand or modify it.
They allow developers to run portions of the graph-generation process and output the results.

* `mach taskgraph tasks <query>` -- get a subset of the taskset based on the query, sorted by label.
  This is useful for making diffs to see the effects of a change to task definitions.
* `mach taskgraph full` -- generate the full task graph, including dependency links.
  This is also useful for diffs, and for visualization.
* `mach taskgraph target <expr>` -- get the target task graph, based on the given expression.
  The expression can be try syntax, `--project` to specify a project, or a query.
* `mach taskgraph optimized [<expr>]` -- get the optimized task graph, optionally based on the target graph for `<expr>`.
* `mach taskgraph visualize` -- generate a visualization of the given graph (maybe in `.dot` format?)
* `mach taskgraph decision` -- run the whole task-graph generation process (expects to be run in a decision task)

# Task Graph Definition

See the proposed [tasks/](/tasks) top-level Gecko directory.

Each subdirectory of this directory contains a `kind.yml` describing the kind.
Just about everything about a kind can be customized in Python.
This allows wild can crazy stuff in the "fringe" kinds that only a few people care about, with a more measured approach to the core kinds for building and testing the browser.
For example, we might want to generate a large tree of tasks to build and test each Rust crate that is included in the browser, using introspection to determine the list of crates.
That code will not clutter up the core build and test classes.

Tasks are (normally) defined in YAML files fairly similar to the existing mechanism.
The kind implementation is free to apply any kind of transformation to these task definitions.
For example, the compile implementation will drop the workspace cache for try jobs (clobbering).
It might also automatically add scopes for every cache and attach a coalescing key and route.
Again, this functionality is located "close" to the affected task definitions and is thus easy to find.

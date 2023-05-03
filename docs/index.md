# Introduction

dem is a command line tool to manage *containerized* Development Environments.

## Developing Embedded Software

Writing software for other architectures then our host usally requires a lot of different tools.
The tools used for a specific project can be grouped together and they form a Development 
Environment. To make it simpler to work with these tools, they can be bundled together into 
Integrated Development Environments.

## Concepts

### Loose coupling between tools :unlock:
One of the biggest disadvantage of IDEs, is that sometimes it is hard to use the underlying 
integrated tools separately. They depend on the IDE or earch other, so standalone usage is not 
possible, the whole installation is required. 

dem's goal is to reduce these dependencies. It assigns the required tools to Development 
Environments, but doesn't effect their usages.

### Separated environments for the tools :octicons-container-24:
The used tools can interfere with each other or the underlying host system causing hardly detectable 
and fixable issues throughout the development process. It can be really devastating to see two PCs
generating different binfaries from the same source and after days of debugging to find out that an
environment variable has a different value for some obscure reason. 

To solve this problem the tools need to operate in their own isolated environments. A lightweight 
and fast solution for isolation is containerization. The tools get built into their respective 
container images, and the way they communicate with the host system is totally under control.

### Scaleable tool change management :arrows_counterclockwise:
Several times throughout the development lifecycle changes in the used tools might needed. DEM makes
it possible to quickly swap tool images:
    - to use a different version of the same tool. Containerization ensures the safe coexistense of 
    the same tools with different version number
    - to use a completely different one
Adding a new tool is as simple as to change one. This makes the Development Environment scalable.

### Reliable Development Environment sharing :material-share:
To have a consistent development for every developer in the organization is mandatory to effectively
create software. With DEM you can easily share the exact same environment for every coworker.

### Quick setup :rocket:
Before joining a project, setting up the required tools can be a time cosuming taks. With DEM you 
can install a new Development Environment with a single command.


!!! example "Example Tutorial"

    Learn by doing! Try our tutorial with a simple embedded project!
# Introduction

**dem** (Development Environment Manager) is an open source command line tool to **manage 
containerized Development Environments.**

!!! info

    Currently only the Linux operating system and the Docker Container Engine is supported.

    Feel free to ask any question at
    [discussions](https://github.com/axem-solutions/dem/discussions).

!!! example "Example Tutorial"

    Learn by doing! Try our tutorial with a simple embedded project!

## Developing Embedded Software

Writing software for other architectures than our host usually requires a lot of different tools.
The tools used for a specific project can be grouped together and they form a Development 
Environment. To make it simpler to work with these tools, they are typically bundled together into 
Integrated Development Environments.

## Concept

### :unlock: Loose coupling between tools
One of the biggest disadvantages of IDEs, is that sometimes it is hard to use the underlying 
integrated tools separately. They might depend on the IDE or each other, so standalone usage is 
difficult, because the **whole IDE installation is required**.

dem's goal is to **reduce these dependencies** and provide the possibility of standalone usage for 
embedded developers.

### :octicons-container-24: Separated environments for the tools
In a generic setup, the used tools can interfere with each other or the underlying host system,
causing hardly detectable and fixable issues throughout the development process. It can be really 
devastating to see two PCs generating different binaries from the same source, and after days of 
debugging to find out that an environment variable had a different value for some obscure reason. 

To eliminate this problem, the tools need to operate in their **own isolated environments**. A 
lightweight and fast solution for isolation is **containerization**. The tools get built into their 
respective container images, and the way they communicate with the host system can be controlled.

### :arrows_counterclockwise: Scaleable tool management
Changes to the tools used may be necessary several times during the development lifecycle. dem makes
it possible to **quickly swap tool images**:

- to use a different version of the same tool 
- to use a completely different tool

Containerization ensures the **safe coexistence** of the same tools with different version numbers.  
Adding a new tool is as simple as to change one, making the Development Environment **scalable**.

### :material-share: Reliable Development Environment sharing
To **create software predictively and effectively**, it is mandatory to have a **consistent**
Development Environment for every developer in the organization.  
With dem, you can easily share the exact same environment with every coworker.

### :rocket: Quick setup
Before starting to work on a project, setting up the required tools can be a time consuming task. 
With dem you can **install a new Development Environment with a single command**.

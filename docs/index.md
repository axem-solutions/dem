# Introduction

**DEM** (Development Environment Manager) is an open source command line tool to **manage 
containerized Development Environments.**

!!! info

    Currently, only the Linux operating system and the Docker Container Engine is supported.

    Feel free to ask any questions at
    [discussions](https://github.com/axem-solutions/dem/discussions).

!!! example "Example Tutorial"

    Learn by doing! Try our [tutorial](https://www.axemsolutions.io/tutorial/index.html) 
    with a simple embedded project!

## Pain points DEM solves
- Slow and error-prone setup of Development Environments -> **Quick and reproducible installation** 
with a single command
- "It works on my machine" -> **Consistent Development Environments** for every developer
- Modifying the toolset is hard and time-consuming -> **Easy and scalable Dev Env management** where 
the tools are like building blocks
- Devs get out of flow and waste time and motivation configuring the tools -> Devs can **focus on 
their actual work**
- Vendor specific interfaces -> **Standardized Development Environments**

## Concept

### :unlock: Loose coupling between tools
One of the biggest disadvantage of traditional IDEs is that sometimes it is hard to use the 
underlying integrated tools separately. They might depend on the IDE itself or each other, so 
standalone usage can be difficult and the whole IDE installation might be required.

DEM's goal is to **reduce these dependencies** and provide the possibility of standalone usage.

### :octicons-container-24: Separated environments for the tools
In a generic setup, the used tools can interfere with each other or the underlying host system,
causing hardly detectable and fixable issues throughout the development process. It can be really 
devastating to see two PCs generating different binaries from the same source, and after days of 
debugging to find out that an environment variable had a different value for some obscure reason. 

To eliminate this problem, the tools need to operate in their **own isolated environments**. A 
lightweight and fast solution for isolation is **containerization**. The tools get built into their 
respective **container images**, and the way they communicate with the host system can be controlled.

### :arrows_counterclockwise: Scaleable tool management
Changes in the tools used for development may be necessary several times during the development 
lifecycle. DEM makes the change easy by providing a way to **quickly swap tool images**:

- to use a different version of the same tool 
- to use a completely different tool

Containerization ensures the **safe coexistence** of the different versions of the same tools.  
Adding a new tool is as simple as changing one, making the Development Environment **scalable**.

### :material-share: Reliable Development Environment sharing
To **create software predictively and effectively**, it is crucial to have a **consistent**
Development Environment **for every developer** in the organization.  
With DEM, you can **easily share** the same environment with every coworker.

### :rocket: Quick and reproducible setup
Before starting to work on a project, setting up the required tools can be a time-consuming task. 
By using DEM, the **installation of a new Development Environment** becomes very **quick** and
**simple**.

If some modifications must be added to an old project no one worked on for a while, installing the 
required toolset can be an exhausting task. With DEM the Development Environment can be assigned to
a project, so it can be **reinstalled whenever needed**.
# Introduction

dem is a command line tool to manage *containerized* development environments.

## Developing Embedded Software

Writing software for other architectures then our host usally requires a lot of different tools.
The tools used for a specific project can be grouped together and they form a Development 
Environment. To make it simpler to work with these tools, they can be bundled together into 
Integrated Development Environments.

## Concepts

### Loose coupling between tools
One of the biggest disadvantage of IDEs, is that sometimes it is hard to use the underlying 
integrated tools separately. They depend on the IDE or earch other, so standalone usage is not 
possible, the whole installation is required. 

dem's goal is to reduce these dependencies. It assigns the required tools to Development 
Environments, but doesn't effect their usages.

### Separated environments for each tool
The used tools can interfere with each other or the underlying host system causing hardly detectable 
and fixable issues throughout the development process. It can be really devastating to see two PCs
generating different binfaries from the same source and after days of debugging to find out that an
environment variable has a different value for some obscure reason. 

To solve this problem the tools need to operate in their own isolated environments. A lightweight 
and fast solution for isolation is containerization. The tools get built into their respective 
container images, and the way they communicate with the host system is totally under control.

## Project layout

    mkdocs.yml    # The configuration file.
    docs/
        index.md  # The documentation homepage.
        ...       # Other markdown pages, images and other files.

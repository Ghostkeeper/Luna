==================================
Goals, Requirements and Priorities
==================================
This document details why Luna exists and what its requirements and priorities are that lead to the architecture choices made for the application.

These requirements and priorities are not fixed. In fact, they are meant to change over time, depending on how the application develops.

-----
Goals
-----
The main objective for Luna is to perform a complex data conversion step for the user. This main objective is currently not fulfilled, but must be fulfilled before any release can be made. Which data conversion step is made depends on the specific set of plug-ins the user has loaded.

A secondary objective is to explore more exotic programming techniques.

------------
Requirements
------------
To be more specific, this section lays out the requirements of the application more rigorously. These requirements are hard, Boolean prerequisites for making any release.

#. The application performs the data conversion step.
#. The application runs reliably without crashing.

----------
Priorities
----------
Not all requirements are hard. In any application, some trade-offs must be made. This section lays out priorities that govern choices we make. The priorities laid out in this section are all considered positive attributes for the application, but not all of them are achievable at the same time.

The priorities are ordered from high to low.

#. The application contributes to the public domain.
#. The user's privacy is preserved. This implies data security as well.
#. The application is extensible. This means that a developer can easily add functionality to it.
#. The application is modular. This means that a user can select components and add or remove them from the application.
#. The programmers of the application learn programming architecture techniques from working on the application.
#. The application is easy to use.
#. The application is tolerant to errors, both from outside components (such as the internet or connected devices) and from plug-ins.
#. The application is easy to maintain. From this follows that code is reused.
#. The application is easy to compile and package. From this priority rises also the priority that the application has few dependencies, as they tend to make the application harder to compile.
#. The application performs well.
#. New programming architecture techniques are experienced with during development of the application.
#. The application scales well to larger input.
#. The application is developed quickly.
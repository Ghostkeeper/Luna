.. This documentation is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this documentation.
.. The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this documentation, the license provided with this documentation should be applied.

===========
Experiments
===========
One of the goals listed in :doc:`goals` is to explore more exotic programming techniques. The experiments towards this goal are listed in this document.

+-------------+-----------+----------------------------------------------------+
| Experiment  | Status    | Report                                             |
+=============+===========+====================================================+
| Everything  | Completed | Success. This really forces the programmer to      |
| is a        |           | think hard on what the API should be. It makes     |
| plug-in     |           | unit tests easier to write. It makes writing       |
|             |           | concurrent code easier. Unit tests via CMake is    |
|             |           | harder.                                            |
+-------------+-----------+----------------------------------------------------+
| Plug-in     | Completed | Mostly a success. This makes concurrency easier.   |
| type        |           | It reduces the amount of tests that need to be     |
| plug-ins    |           | written. It allows for hot-pluggable plug-ins due  |
|             |           | to the registering functionality. However, it      |
|             |           | introduces a lot of boilerplate code. Perhaps some |
|             |           | of that can still be factored out. Forces the      |
|             |           | programmer to make every plug-in have a plug-in    |
|             |           | type in order to specify an API for it, even if    |
|             |           | there will really never be more than one           |
|             |           | implementation of the type.                        |
+-------------+-----------+----------------------------------------------------+
| Model       | In        | Difficult to implement. Difficult to debug. Could  |
| change      | Progress  | make onChange listeners extremely easy and elegant |
| listeners   |           | to use. Forces the programmer to use an explicit   |
|             |           | state that gets updated rather than firing an      |
|             |           | event, so this makes code more clear. Elegance is  |
|             |           | nice. Dict, set and list are immutable in Python   |
|             |           | which requires them to be used in a less elegant   |
|             |           | manner.                                            |
+-------------+-----------+----------------------------------------------------+
| Unit tests  | In        | Probably not possible to interweave threads at     |
| for         | Progress  | bytecode-level. Will nonetheless catch a lot of    |
| concurrency |           | bugs. Similar experiments in other languages       |
|             |           | failed. Keeping it small for now to prevent this.  |
+-------------+-----------+----------------------------------------------------+
| Declarative | Planned   | Seems to make defining UI's very elegant. Involves |
| UI          |           | some complicated hacks. Integrates with other      |
|             |           | Python code very well.                             |
+-------------+-----------+----------------------------------------------------+
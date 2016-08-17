.. This documentation is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this documentation.
.. The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this documentation, the license provided with this documentation should be applied.

===========
Trust Model
===========
All code in Luna as well as any plug-ins must follow the trust model strictly. This trust model dictates when errors should be caught and by whom.

-----------
Plug-in API
-----------
All calls to any plug-in must be considered untrusted. It may raise any exception. This means that the call should be placed in a ``try``-``catch`` block if (and only if) such an exception is not fatal for the current method. If an exception would be fatal, the call should not be wrapped in a ``try``-``catch`` block, so that the exception gets passed on up.

Note that calls to the ``luna`` package may be considered trusted. If there is an exception there, the system can be considered unstable in general. One exception to this is the ``luna.plugins.api`` function, which is intended to call external plug-ins transparently and can therefore not be trusted.

Any input from external plug-ins should also be considered untrusted. Note that a plug-in may contain malicious code.

There are two exceptions to this part of the trust model:
* Calls from a plug-in to the same plug-in may be trusted, even if it goes via ``luna.plugins.api``.
* Calls to the ``logger`` API may be trusted to not give exceptions, for ease of use. Note that if this API should ever be changed in such a way that it returns some data, that data should still not be trusted.

----------
User Input
----------
User input should be treated with such caution in that the user may input anything that the user interface element allows. This means that text input may have any possible Unicode string, and that if some input is disallowed upon typing, this check must also be performed when pasting something in the text field.

--------------
Internet Input
--------------
It should be obvious that any input via the Internet should not be trusted and may contain any byte sequence.

------------------
Reading from Files
------------------
Input from files should not be trusted and may contain any byte sequence.

One exception to this part of the trust model is that files that are the result of the installation of the application may be assumed to remain unmodified since installation as long as those files are installed in a directory that requires administrator access to write to. The user may be assumed to install the application in a location that requires administrator access to write to, but if that same installation also writes to files outside the protected area (e.g. the user's settings folder), those files should not be trusted.

Since plug-ins may be installed to a location that is not in the protected area, their code and any input gained from it must be considered untrusted, as discussed in the section on `Plug-in API`_.
=============
Release Notes
=============

-----
0.4.0
-----

Released: 2025-07-01

*  **Features**

   *  Now using *lockss-pybasic* and *pydantic-argparse* internally.

*  **Changes**

   *  Bare arguments are no longer allowed and treated as node references; all WARC files must be specified via ``--warc/-w`` or ``--warcs/-W`` options.

========
WarcRead
========

.. |RELEASE| replace:: 0.4.0
.. |RELEASE_DATE| replace:: 2025-07-01

.. |WARC| replace:: ``--warc/-w``
.. |WARCS| replace:: ``--warcs/-W``
.. |HELP| replace:: ``--help/-h``

WarcRead is a library and command line tool for WARC file reporting and processing.

:Latest release: |RELEASE| (|RELEASE_DATE|)
:Release notes: `<CHANGELOG.rst>`_
:License: `<LICENSE>`_

-----------------
Table of Contents
-----------------

*  `Quick Start`_

*  `Installation`_

*  `Command Line Tool`_

   *  `Synopsis`_

   *  `WARC File Options`_

   *  `Commands`_

      *  `Top-Level Program`_

      *  `extract`_

      *  `report`_

*  `Library`_

-----------
Quick Start
-----------

::

    # Install with pipx
    pipx install lockss-warcread

    # Verify installation and discover all the commands
    warcread --help

    # Get all URLs and content types in a pile of WARC files
    warcread report --warc mywarcs*.warc.gz --url --content-type

    # Get all URLs and content types in a set of WARC files listed in mylist.txt
    warcread report --warcs mylist.txt --url --content-type

    # Extract the payload ("contents") of https://example.com/about.html
    # from within a pile of WARC files
    warcread extract --warc mywarcs*.warc.gz --target-url 'https://example.com/about.html'

------------
Installation
------------

WarcRead is available from the `Python Package Index <https://pypi.org/>`_ (PyPI) as ``lockss-debugpanel`` (https://pypi.org/project/lockss-warcread).

*  To install WarcRead in your own non-virtual environment, we recommend using ``pipx``::

       pipx install lockss-warcread

*  To install WarcRead globally for every user, you can use ``pipx`` as ``root`` with the ``--global`` flag (provided you are running a recent enough ``pipx``)::

       pipx install --global lockss-warcread

*  To install WarcRead in a Python virtual environment, simply use ``pip``::

       pip install lockss-warcread

The installation process adds a ``lockss.warcread`` Python `Library`_ and a ``warcread`` `Command Line Tool`_. You can check at the command line that the installation is functional by running ``warcread version`` or ``warcread --help``.

-----------------
Command Line Tool
-----------------

WarcRead is invoked at the command line as::

    warcread

or as a Python module::

    python -m lockss.warcread

Help messages and this document use ``warcread`` throughout, but the two invocation styles are interchangeable.

Synopsis
========

.. note::

   As of version 0.4.0, bare arguments are no longer allowed and treated as WARC files; all WARC files must be listed via the `WARC File Options`_ |WARC| and |WARCS|.

WarcRead uses `Commands`_, in the style of programs like ``git``, ``dnf``/``yum``, ``apt``/``apt-get``, and the like. You can see the list of available `Commands`_ by invoking ``warcread --help``::

    Usage: warcread [-h] {copyright,ext,extract,license,rep,report,version} ...

    Tool for WARC file reporting and processing

    Commands:
      {copyright,ext,extract,license,rep,report,version}
        copyright           print the copyright and exit
        ext                 synonym for: extract
        extract             extract parts of response records
        license             print the software license and exit
        rep                 synonym for: report
        report              output tab-separated report over response records
        version             print the version number and exit

    Help:
      -h, --help            show this help message and exit


WARC File Options
=================

.. note::

   As of version 0.4.0, bare arguments are no longer allowed and treated as WARC files; all WARC files must be listed via the `WARC File Options`_ |WARC| and |WARCS|.

`Commands`_ expect one or more WARC files to process. The set of WARC files to process is derived from:

*  The WARC files listed as |WARC| options.

*  The WARC files found in the files listed as |WARCS| options.

Examples::

    warcread report --warc mywarc01.warc.gz --warc mywarc02.warc.gz --warc mywarc03.warc.gz ... --url

    warcread report -w mywarc01.warc.gz -w mywarc02.warc.gz -w mywarc03.warc.gz ... --url

    warcread report --warc mywarc01.warc.gz mywarc02.warc.gz mywarc03.warc.gz ... --url

    warcread report -w mywarc01.warc.gz mywarc02.warc.gz mywarc03.warc.gz ... --url

    warcread report --warcs mylist1.txt --warcs mylist2.txt --warcs mylist3.txt ... --url

    warcread report -W mylist1.txt -W mylist2.txt -W mylist3.txt ... --url

    warcread report -warcs mylist1.txt mylist2.txt mylist3.txt ... --url

    warcread report -W mylist1.txt mylist2.txt mylist3.txt ... --url

Commands
========

The available commands are:

========== ============ =======
Command    Abbreviation Purpose
========== ============ =======
`extract`_ ext          extract parts of response records
`report`_  rep          output tab-separated report over response records
========== ============ =======

Top-Level Program
-----------------

The top-level executable alone does not perform any action or default to a given command::

    Usage: warcread [-h] {copyright,ext,extract,license,rep,report,version} ...
    warcread: error: the following arguments are required: {copyright,ext,extract,license,rep,report,version}

.. _extract:

``extract`` (``ext``)
---------------------

The ``extract`` (or alternatively ``ext``) command can be used to look for the WARC response record for a given target URL in a set of WARC files, and extract the WARC record's headers (``--warc-headers/--wh/-A``), the HTTP response's headers (``--http-headers/--hh/-H``), or the HTTP response's payload (``--http-payload/--hp/-P``)::

    Usage: warcread extract [-h] [-w WARC [WARC ...]] [-W WARCS [WARCS ...]] [-t TARGET_URL] [-H] [-P] [-A]

    Required Arguments:
      -t, --target-url TARGET_URL
                            target URL

    Optional Arguments:
      -w, --warc WARC [WARC ...]
                            (WARCs) add one or more WARC files to the set of WARC files to process (default: [])
      -W, --warcs WARCS [WARCS ...]
                            (WARCs) add the WARC files listed in one or more files to the set of WARC files to process (default: [])
      -H, --hh, --http-headers
                            (action) extract HTTP headers for target URL (default: False)
      -P, --hp, --http-payload
                            (action) extract HTTP payload for target URL (default: False)
      -A, --wh, --warc-headers
                            (action) extract WARC headers for target URL (default: False)

    Help:
      -h, --help            show this help message and exit

The command needs:

*  One or more WARC files, from the `WARC File Options`_ (|WARC| options, |WARCS| options).

*  A target URL, from the ``--target-url/-t`` option.

.. _report:

``report`` (``rep``)
---------------------

The ``report`` (or alternatively ``rep``) command can be used to produce a tabular (tab-separated) report over a set of WARC files, listing one or more columns of information about each::

    Usage: warcread report [-h] [-w WARC [WARC ...]] [-W WARCS [WARCS ...]] [-c] [-n] [-d] [-p] [-r] [-s] [-m] [-u] [-D] [-F]

    Optional Arguments:
      -w, --warc WARC [WARC ...]
                            (WARCs) add one or more WARC files to the set of WARC files to process (default: [])
      -W, --warcs WARCS [WARCS ...]
                            (WARCs) add the WARC files listed in one or more files to the set of WARC files to process (default: [])
      -c, --content-type    (column) output HTTP Content-Type (e.g. text/xml; charset=UTF-8) (default: False)
      -n, --http-code       (column) output HTTP response code (e.g. 404) (default: False)
      -d, --http-date       (column) output HTTP Date (default: False)
      -p, --http-protocol   (column) output HTTP protocol (e.g. HTTP/1.1) (default: False)
      -r, --http-reason     (column) output HTTP reason (e.g. Not Found) (default: False)
      -s, --http-status     (column) output HTTP status (e.g. HTTP/1.1 404 Not Found) (default: False)
      -m, --media-type      (column) output media type of HTTP Content-Type (e.g. text/xml) (default: False)
      -u, --url             (column) output URL of WARC record (default: False)
      -D, --warc-date       (column) output date of WARC record (default: False)
      -F, --warc-file       (column) output name of WARC file of origin (default: False)

    Help:
      -h, --help            show this help message and exit

The command needs:

*  One or more WARC files, from the `WARC File Options`_ (|WARC| options, |WARCS| options).

*  One or more column options, chosen among ``--content-type/-c``, ``--http-code/-n``, ``--http-date/-d``, ``--http-protocol/-p``, ``--http-reason/-r``, ``--http-status/-s``, ``--media-type/-m``, ``--url/-u``, ``--warc-date/-D``, and ``--warc-file/-F``. Note that currently ``--url/-u`` is not always on.

-------
Library
-------

The ``lockss.debugpanel.warcutil`` module contains a variety of utilities for WARC file processing. The module is documented inline with Python docstrings, which can be viewed with ``pydoc``.

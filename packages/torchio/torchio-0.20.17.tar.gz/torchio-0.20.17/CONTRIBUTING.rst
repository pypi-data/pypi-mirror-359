.. highlight:: shell

============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every little bit
helps, and credit will always be given.

You can contribute in many ways:

Types of contributions
----------------------

Report bugs
~~~~~~~~~~~

Report bugs
`on GitHub <https://github.com/TorchIO-project/torchio/issues/new?assignees=&labels=bug&template=bug_report.md&title=>`_.

If you are reporting a bug, please include:

* Your TorchIO version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

Fix bugs
~~~~~~~~

Look through the GitHub issues for bugs. Anything tagged with "bug" and "help
wanted" is open to whoever wants to implement it.

Implement features
~~~~~~~~~~~~~~~~~~

Look through the GitHub issues for features. Anything tagged with "enhancement"
and "help wanted" is open to whoever wants to implement it.

Write documentation
~~~~~~~~~~~~~~~~~~~

TorchIO could always use more documentation, whether as part of the
official TorchIO docs, in docstrings, or even on the web in blog posts,
articles, and such.

Submit feedback
~~~~~~~~~~~~~~~

The best way to send feedback is to file an issue at https://github.com/TorchIO-project/torchio/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

Get started!
------------

Ready to contribute? Here's how to set up ``torchio`` for local development.

1) Create an issue on the GitHub repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It's good practice to first discuss the proposed changes as the feature might
already be implemented.

2) Fork the ``torchio`` repository on GitHub
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Click `here <https://github.com/TorchIO-project/torchio/fork>`_ to create your fork.

3) Clone your fork locally
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    git clone git@github.com:your_github_username_here/torchio.git
    cd torchio

4) Install your local copy into a virtual environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`uv <https://docs.astral.sh/uv/>`_ is recommended for development.
You can use `just <https://just.systems/>`_ to set up the development environment.
This will 1) install ``uv`` if not found and 2) install ``torchio`` and all its
dependencies::

    just setup

5) Create a branch for local development using the issue number
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For example, if the issue number is 55::

    git checkout -b 55-name-of-your-bugfix-or-feature

Now you can make your changes locally.

6) Run unit tests
~~~~~~~~~~~~~~~~~

When you're done making changes, check that your changes pass the tests
using ``pytest``::

    uv run pytest -x

7) Commit your changes and push your branch to GitHub
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`Here's some great
advice to write good commit
messages <https://chris.beams.io/posts/git-commit>`_, and `here's some
more <https://medium.com/@joshuatauberer/write-joyous-git-commit-messages-2f98891114c4>`_)::

    git add .
    git commit -m "Fix nasty bug"
    git push origin 55-name-of-your-bugfix-or-feature

8) Check documentation
~~~~~~~~~~~~~~~~~~~~~~

If you have modified the documentation or some docstrings, build the docs and
verify that everything looks good::

    just build-docs

You can also build, serve and automatically rebuild the docs every
time you modify them and reload them in the browser::

    just serve-docs

9) Submit a pull request on GitHub
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tips
----

To run a subset of tests::

    uv run pytest tests/data/test_image.py

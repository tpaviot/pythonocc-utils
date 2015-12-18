===============================
Contributing to pythonocc-utils
===============================

Pre-requisites
==============

- git is installed

- git is properly setup

  Your personal git configurations are saved in the .gitconfig file. You can edit this   file directly or you can use the `git config --global` command:

  .. code-block:: shell
  
    $ git config --global user.email you@yourdomain.example.com
    $ git config --global user.name "Your Name Comes Here"
    $ git config --global merge.summary true


Forking
=======

Making your own copy (fork) of pythonocc-utils
----------------------------------------------

You need to do this only once. The instructions here are very similar to the instructions at http://help.github.com/forking/ - please see that page for more detail. We’re repeating some of it here just to give the specifics for the pythonocc-utils project, and to suggest some default names.

Set up and configure a github account.
If you don’t have a github account, go to the github page, and make one.

Create your own forked copy of pythonocc-utils:

- Log into your github account.

- Go to the pythonocc-utils github home at tpaviot/pythonocc-utils github.

- Click on the fork button

Set up your fork
----------------

.. code-block:: shell

  $ git clone https://github.com/<your-user-name>/pythonocc-utils
  $ cd pythonocc-utils

Linking your repository to the upstream repo
--------------------------------------------


.. code-block:: shell

  $   

**The git:// URL is read only**

Check
-----

.. code-block:: shell

  $ git remote -v show

Development workflow
====================

Pre-requisites
--------------

You already have your own forked and setup copy of the pythonocc-utils repository, by following:

- Making your own copy (fork) of pythonocc-utils

- Set up your fork

- Linking your repository to the upstream repo.

What is described below is a recommended workflow with Git.

Following the latest source
---------------------------

From time to time you may want to pull down the latest code. Do this with:

.. code-block:: shell

  $ cd pythonocc-utils
  $ git fetch
  $ git merge --ff-only

The tree in pythonocc-utils will now have the latest changes from the initial repository.

Basic workflow
--------------

- Start a new feature branch for each set of edits that you do.

- Hack away!

- When finished:

  - Contributors: push your feature branch to your own Github repo, and create a pull request.

Making a new feature branch
~~~~~~~~~~~~~~~~~~~~~~~~~~~

First, update your master branch with changes that have been made in the main pythonocc-utils repository. In this case, the --ff-only flag ensures that a new commit is not created when you merge the upstream and master branches. It is very important to avoid merging adding new commits to master.

.. code-block:: shell

  # go to the master branch
  $ git checkout master
  # download changes from github
  $ git fetch upstream
  # update the master branch
  $ git merge upstream/master --ff-only
  # Push new commits to your Github repo
  $ git push

or

.. code-block:: shell

  $ git pull --ff-only upstream master
  $ git push

Finally create a new branch for your work and check it out:

.. code-block:: shell

  $ git checkout -b my-new-feature master

The editing workflow
~~~~~~~~~~~~~~~~~~~~

.. code-block:: shell

  # hack hack
  $ git status # Optional
  $ git diff # Optional
  $ git add modified_file
  $ git commit
  # push the branch to your own Github repo
  $ git push origin my-new-feature


Commit messages
~~~~~~~~~~~~~~~

Commit messages should be clear and follow a few basic rules. Example:

.. code-block:: shell

  ENH: add functionality X to pythonocc-utils.<submodule>.
  
  The first line of the commit message starts with a capitalized acronym
  (options listed below) indicating what type of commit this is.  Then a blank
  line, then more text if needed.  Lines shouldn't be longer than 72
  characters.  If the commit is related to a ticket, indicate that with
  "See #3456", "See ticket 3456", "Closes #3456" or similar.


.. code-block:: shell

  API: an (incompatible) API change
  BLD: change related to building pythonocc-utils
  BUG: bug fix
  DEP: deprecate something, or remove a deprecated object
  DEV: development tool or utility
  DOC: documentation
  ENH: enhancement
  MAINT: maintenance commit (refactoring, typos, etc.)
  REV: revert an earlier commit
  STY: style fix (whitespace, PEP8)
  TST: addition or modification of tests
  REL: related to releasing pythonocc-utils

Asking for your changes to be merged with the main repo
-------------------------------------------------------

When you feel your work is finished, you can create a pull request (PR). Github has a nice help page that outlines the process for filing pull requests: https://help.github.com/articles/using-pull-requests/#initiating-the-pull-request

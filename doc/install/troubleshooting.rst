.. _install_troubleshooting:

============================
Installation Troubleshooting
============================

Common installation issues and solutions will be posted here as they are
discovered.

.. _install_trouble_ppc:

Running setup.py fails at PIL installation, 'gcc for ppc not installed'
-----------------------------------------------------------------------

This issue affects Mac OS X machines running Xcode 4.

After running the command:

.. sourcecode:: bash

   python setup.py develop

An error similar to this may be shown:

.. sourcecode:: text

   Running PIL-1.1.6/setup.py -q bdist_egg --dist-dir /var/folders/7W/7Wsp1hLuHKO4MHt1O5quqk+++TI/-Tmp-/easy_install-iYcKsT/PIL-1.1.6/egg-dist-tmp-Qn6yLs
   --- using frameworks at /System/Library/Frameworks
   _imaging.c:2907: warning: initialization from incompatible pointer type
   _imaging.c:2967: warning: initialization from incompatible pointer type
   /usr/libexec/gcc/powerpc-apple-darwin10/4.2.1/as: assembler (/usr/bin/../libexec/gcc/darwin/ppc/as or /usr/bin/../local/libexec/gcc/darwin/ppc/as) for architecture ppc not installed
   Installed assemblers are:
   /usr/bin/../libexec/gcc/darwin/x86_64/as for architecture x86_64
   /usr/bin/../libexec/gcc/darwin/i386/as for architecture i386
   _imaging.c:2907: warning: initialization from incompatible pointer type
   _imaging.c:2967: warning: initialization from incompatible pointer type
   _imaging.c:3149: fatal error: error writing to -: Broken pipe
   compilation terminated.

Note the 4th line: **'/usr/libexec/gcc/powerpc-apple ... gcc/darwin/ppc/as) for architecture ppc not installed'**

This may occur in OS X after upgrading to Xcode 4, which appears to remove PPC compilation
support in Python. Simply run:

.. sourcecode:: bash

   # Set gcc archflags to exclude ppc
   export ARCHFLAGS='-arch i386 -arch x86_64'

Now try your command again.

Running setup.py fails on Fedora
--------------------------------

Fedora users have reported that the 'tk-devel' package must be installed before
installing MediaCore CE, or setup.py will fail.

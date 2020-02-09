This version of efl fails to run tests for 32 bit archs.

See [eina - value - test - cats warnings on 32bit to get some silence](https://git.enlightenment.org/core/efl.git/commit/src/tests/eina/eina_test_value.c?h=efl-1.23&id=a8d1c7d8ad5b54425147a6f678c917b966ada8f0)

To build for 32 bit disable tests:

```
export DEB_BUILD_OPTIONS="nocheck"
dpkg-buildpackage -rfakeroot -b -uc```

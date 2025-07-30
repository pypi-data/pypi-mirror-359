# ICHEC Django Core #

This is a set of Django application building blocks and utilities for use at ICHEC. They can be used to build and test other Django apps.

Useful elements include:

* A common collection of Django Settings for use in consuming projects, intended to provide secure defaults:

``` python
from ichec_django_core import settings

MY_DJANGO_SETTING = settings.MY_DJANGO_SETTING
```

* Core functionality for authentication, including models of portal members and organizations 

* Functionality for handling user provided media and subsequent access in a secure and performant way

* Tested, re-usable components

# Licensing #

This software is copyright of the Irish Centre for High End Computing (ICHEC). It may be used under the terms of the GNU AGPL version 3 or later, with license details in the included `LICENSE` file. Exemptions are available for Marinerg project partners and possibly others on request.

Integrations
============

.. _django:

Django
------

Add :class:`unpoly.contrib.django.UnpolyMiddleware` to `MIDDLEWARES` and it will
attach :class:`unpoly.up.Unpoly` as `up` to every request. As simple as that ;=)

.. _starlette:

Starlette
---------

Add a new :class:`starlette.middleware.Middleware` to your Starlette
application as follows:

```python
from starlette.middleware import Middleware
from unpoly.contrib.starlette import UnpolyMiddleware
app = Starlette(..., middleware=[Middleware(UnpolyMiddleware)])
```

Simalarly to the Django middleware, :class:`unpoly.up.Unpoly` will be available
as an `up` attribute on every :class:`starlette.requests.Request`.

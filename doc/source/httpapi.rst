HTTP API
=========

Archivant and Users
---------------------

.. autoflask:: webant.webant:create_app(dict(USERS_DATABASE='sqlite:////tmp/asd'))
   :blueprints: api
   :include-empty-docstring:

Agherant
-----------

.. autoflask:: webant.webant:create_app(dict(AGHERANT_DESCRIPTIONS=range(3)))
   :blueprints: agherant
   :include-empty-docstring:

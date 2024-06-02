Wikidata Handy Interface in Python
==================================

Just some basic wrappers built around mainly wikidataintegrator and pywikibot
to gather some Wikidata info about stuff.

This is not meant to be a big thing, just some convenience tool I used for some
specific purpose. The interface is very lacking but maybe you will find a couple
things that might be useful for your use case. It is very bare bones and just
aims to avoid writing lots of dictionary keys.

Installation
============

.. code-block:: bash

    git clone git@github.com:YoannDupont/whip.git
    cd whip
    pip install .

Basic usage
===========

.. code-block:: python
   :linenos:

    import whip.lasso, whip.properties

    # you might want multiple candidates when exploring, this works for the example
    qid = whip.lasso.from_name("Le Petit Prince", langs=["fr"], maximum_candidates=1)[0]
    entry = whip.lasso.from_qid(qid)
    author_qid = whip.properties.naive_get(entry, "P50", extra_key="id") # some properties have an "extra" level.
    author_entry = whip.lasso.from_qid(author_qid)

    print(whip.properties.label(entry, "fr")) # prints "Le Petit Prince"
    print(whip.properties.instance_of(entry)) # prints "{'Q7725634'}" for "literary work"
    print(whip.properties.label(author_entry, "fr")) # prints "Antoine de Saint-Exupéry"

ie-linked-data
==============

This is a suite of scripts and data files used in dealing with converting the legacy statistical datasets to linked data. 

It contains:

* Scripts
  * [a parser for PC-Axis format](ie-linked-data/tree/master/pcaxis/PCAxisParser.py)
  * [converters for CSO's CSV datasets to RDF](ie-linked-data/tree/master/csv/Converters/)
  * [RDFModel](ie-linked-data/tree/master/RDFModel/) - a simple wrapper for the RDF API

* Data files
  * Classes
  * Codelists
  * Concepts
  * Data structure definitions
  * Properties
  * Datasets


Requirements:

* Python 2.x
* [librdf](http://librdf.org/docs/python.html) Python library - wrapper for Redland Toolkit


Bugs:

* Some of the prefixes in turtle files are not defined:
  * Concepts/concepts.ttl is missing "@prefix concept: <http://stats.govdata.ie/concept/> ."
  * Properties/properties.ttl is missing "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> ."

* Script is generating invalid URIs for some of the turtle files (age1.ttl, age2.ttl, birthplace.ttl, marital-status.ttl, nationality.ttl, religion.ttl):
  * e.g., Codelists/age1.ttl contains "code-age1:0" for object but should be "<http://stats.govdata.ie/codelist/age1/0>" instead

* Need to review URI patterns
  * e.g., /City and /city/galway: This can raise two (or more) issues. If want to move up one level on /city/galway, we get /city, expecting a collection of cities, however that URI doesn't exist due to case sensitivity. In contrast, /City is used for class definition.

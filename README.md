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

* Need to review URI patterns
  * e.g., /City and /city/galway: This can raise two (or more) issues. If want to move up one level on /city/galway, we get /city, possibly expecting a collection of cities, however that URI doesn't exist due to case sensitivity. In contrast, /City is used for class definition.

* Some of the object resources are outputted as literals as opposed to IRIs. This occurs in gender-age-aggregates.ttl (e.g., prop:geoArea "http://geo.govdata.ie/traditional-county/tipperary") and persons-by-religion/persons-by-religion.ttl (prop:religion "http://stats.govdata.ie/codelist/religion/catholic").

* Replace URIs like http://stats.data-gov.ie/codelist/census-2006/city/galway/ea/041-039 with http://stats.data-gov.ie/codelist/census-2006/city/geo/galway/ea/041-039 in observations.

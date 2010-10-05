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

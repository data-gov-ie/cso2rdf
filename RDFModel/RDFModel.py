#!/usr/bin/env python
#-*- coding:utf-8 -*-

import ataxit, os, random, RDF, re, unicodedata


class RDFModel (object):
  """
    Helper class for interacting with RDF.Storage from librdf
  """
  
  def __init__(self, namespaces = {}):
    # Initialize variables
    name = "db-{0!s}".format(
      random.randint(1, 999999)
    )
    self.db = RDF.Storage(
      storage_name = "hashes",
      name = name,
      options_string = "hash-type='bdb'"
    )
    self.model = RDF.Model(self.db)
    self.serializer = RDF.Serializer(name="turtle")
    self.ns = {}
    
    # Define basic namespaces
    basicNamespaces = {
      "rdf" : "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
      "xsd" : "http://www.w3.org/2001/XMLSchema#",
    }
    # Extend basic namespaces with those provided in parameters
    basicNamespaces.update(namespaces)
    self.addNamespaces(basicNamespaces)
    ataxit.register(self.clearTempFiles)
    
  def clearTempFiles(self):
    for file in os.listdir(os.curdir):
      if bool(re.match("db-\d+\.db$", file)):
        os.remove(os.path.join(os.curdir, file))
    
  def addNamespaces(self, namespaces):
    for namespace in namespaces:
      if not self.ns.has_key(namespace):
        if type(namespaces[namespace]) == RDF.Uri:
          namespaces[namespace] = str(namespaces[namespace])
        self.ns[namespace] = RDF.NS(namespaces[namespace])
        self.serializer.set_namespace(namespace, namespaces[namespace])
  
  def bootstrap(self, filename):
    file = open(filename, "r")
    parser = RDF.Parser(name="turtle")
    status = parser.parse_string_into_model(self.model, file.read(), "http://example.com/bootstrap")
    file.close()
    if not status:
      raise RDF.RedlandError("Error parsing bootstrapping file.")
    else:
      namespaces = parser.namespaces_seen()
      self.addNamespaces(namespaces)
    return self      
        
  def append(self, statements):
    for statement in statements: 
      try:
        self.model.append(RDF.Statement(statement[0], statement[1], statement[2]))
      except RDF.RedlandError:
        print "RDF.RedlandError\ns: {0}\np: {1}\no: {2}".format(
          subject,
          statement[0],
          statement[1]
        )
    return self
  
  def appendToSubject(self, subject, statements):
    for statement in statements:
      try:
        self.model.append(RDF.Statement(subject, statement[0], statement[1]))
      except RDF.RedlandError:
        print "RDF.RedlandError\ns: {0}\np: {1}\no: {2}".format(
          subject,
          statement[0],
          statement[1]
        )
    return self
        
  def write(self, filename):
    file = open(filename, "w")
    file.write(
      self.serializer.serialize_model_to_string(
        self.model
      )
    )
    file.close()
    
  def stringForUri(self, text):
    # Normalize accents
    text = unicode(text, "utf-8")
    text = "".join((c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn"))
    # Clean unwanted characters
    return unicode.encode(re.sub("\s", "-", text.lower()), "utf-8")
    
  def clean(self, what, where):
    return re.compile("\s*{0}\s*".format(what), flags = re.IGNORECASE).sub("", where).strip()
  
  def sparql(self, query):
    query = RDF.SPARQLQuery(query)
    results = query.execute(self.model)
    return results

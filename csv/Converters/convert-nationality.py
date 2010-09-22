#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
from Converter import Converter

# Definition of the paths
DSD = os.path.join("..", "..", "DSDs", "persons-by-nationality.ttl")
ED_FILE = os.path.join("..", "Datasources", "ed", "nationality.csv")
EA_FILE = os.path.join("..", "Datasources", "ea", "nationality.csv")


class ConvertNationality (Converter):
  
  def __init__(self, title):
    namespaces = {
      # own namespaces
      "code-nationality" : "http://stats.govdata.ie/codelist/nationality/",
    }
    Converter.__init__(self, DSD, title, namespaces, ED_FILE, EA_FILE)
    
    self.setAppendedDimensions([
      self.ns["prop"]["nationality"],
    ])
    
    self.nationalityIndexToConcept = [
      {
        "notation" : "irish",
        "uri" : self.ns["code-nationality"]["irish"],
      },
      {
        "notation" : "uk",
        "uri" : self.ns["code-nationality"]["uk"],
      },
      {
        "notation" : "polish",
        "uri" : self.ns["code-nationality"]["polish"],
      },
      {
        "notation" : "lithuanian",
        "uri" : self.ns["code-nationality"]["lithuanian"],
      },
      {
        "notation" : "other-eu-25",
        "uri" : self.ns["code-nationality"]["other-eu-25"],
      },
      {
        "notation" : "rest",
        "uri" : self.ns["code-nationality"]["rest"],
      },
      {
        "notation" : "not-stated",
        "uri" : self.ns["code-nationality"]["not-stated"],
      },
      {
        "notation" : "total",
        "uri" : self.ns["code-nationality"]["total"],
      },
    ]
    
  def callback(self, dimensions, line):
    for key, obsValue in enumerate(line):
      self.appendObservation(
        dimensions + [self.nationalityIndexToConcept[key]],
        obsValue
      )
    
    
if __name__ == "__main__":
  cn = ConvertNationality(
    title = "Persons usually resident and present in the State on Census Night, classified by nationality, 2006"
  )
  cn.main()

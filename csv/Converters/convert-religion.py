#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
from Converter import Converter

# Definition of the paths
DSD = os.path.join("..", "..", "DSDs", "persons-by-religion.ttl")
ED_FILE = os.path.join("..", "Datasources", "ed", "religion.csv")
EA_FILE = os.path.join("..", "Datasources", "ea", "religion.csv")


class ConvertReligion (Converter):
  
  def __init__(self, title):
    namespaces = {
      # own namespaces
      "code-religion" : "http://stats.data-gov.ie/codelist/religion/",
    }
    Converter.__init__(self, DSD, title, namespaces, ED_FILE, EA_FILE)
    self.setAppendedDimensions([
      self.ns["prop"]["religion"],
    ])
    
    self.religionIndexToConcept = [
      {
        "notation" : "catholic",
        "uri" : self.ns["code-religion"]["catholic"],
      },
      {
        "notation" : "other",
        "uri" : self.ns["code-religion"]["other"],
      },
      {
        "notation" : "non",
        "uri" : self.ns["code-religion"]["non"],
      },
      {
        "notation" : "not-stated",
        "uri" : self.ns["code-religion"]["not-stated"],
      },
      {
        "notation" : "total",
        "uri" : self.ns["code-religion"]["total"],
      },
    ]
  
  def callback(self, dimensions, line):
    for key, obsValue in enumerate(line):
      self.appendObservation(
        dimensions + [self.religionIndexToConcept[key]],
        obsValue
      )
  

if __name__ == "__main__":
  cr = ConvertReligion(
    title = "Number of persons by religion, 2006"
  )
  cr.main()

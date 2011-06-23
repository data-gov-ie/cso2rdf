#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
from Converter import Converter

# Definition of the paths
DSD = os.path.join("..", "..", "DSDs", "persons-by-birthplace.ttl")
ED_FILE = os.path.join("..", "Datasources", "ed", "birthplace.csv")
EA_FILE = os.path.join("..", "Datasources", "ea", "birthplace.csv")


class ConvertBirthplace (Converter):
  
  def __init__(self, title):
    namespaces = {
      # own namespaces
      "code-birthplace" : "http://stats.data-gov.ie/codelist/birthplace/",
    }
    Converter.__init__(self, DSD, title, namespaces, ED_FILE, EA_FILE)
    
    self.setAppendedDimensions([
      self.ns["prop"]["birthplace"],
    ])
    
    self.birthplaceIndexToConcept = [
      {
        "notation" : "ireland",
        "uri" : self.ns["code-birthplace"]["ireland"],
      },
      {
        "notation" : "uk",
        "uri" : self.ns["code-birthplace"]["uk"],
      },
      {
        "notation" : "poland",
        "uri" : self.ns["code-birthplace"]["poland"],
      },
      {
        "notation" : "lithuania",
        "uri" : self.ns["code-birthplace"]["lithuania"],
      },
      {
        "notation" : "other-eu-25",
        "uri" : self.ns["code-birthplace"]["other-eu-25"],
      },
      {
        "notation" : "rest",
        "uri" : self.ns["code-birthplace"]["rest"],
      },
      {
        "notation" : "total",
        "uri" : self.ns["code-birthplace"]["total"],
      },
    ]
    
  def callback(self, dimensions, line):
    for key, obsValue in enumerate(line):
      self.appendObservation(
        dimensions + [self.birthplaceIndexToConcept[key]],
        obsValue
      )

if __name__ == "__main__":
  cb = ConvertBirthplace(
    title = "Persons usually resident and present in the State on Census Night, classified by place of birth, 2006"
  )
  cb.main()

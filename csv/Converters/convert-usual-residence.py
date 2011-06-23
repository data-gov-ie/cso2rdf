#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
from Converter import Converter

# Definition of the paths
DSD = os.path.join("..", "..", "DSDs", "persons-by-usual-residence.ttl")
ED_FILE = os.path.join("..", "Datasources", "ed", "usual_residence.csv")
EA_FILE = os.path.join("..", "Datasources", "ea", "usual_residence.csv")


class ConvertUsualResidence (Converter):
  
  def __init__(self, title):
    namespaces = {
      # own namespaces
      "code-residence" : "http://stats.data-gov.ie/codelist/usual-residence/",
    }
    Converter.__init__(self, DSD, title, namespaces, ED_FILE, EA_FILE)
    
    self.setAppendedDimensions([
      self.ns["prop"]["usualResidence"],
    ])
    
    self.usualResidenceIndexToConcept = [
      {
        "notation" : "same-address",
        "uri" : self.ns["code-residence"]["same-address"],
      },
      {
        "notation" : "elsewhere-in-county",
        "uri" : self.ns["code-residence"]["elsewhere-in-county"],
      },
      {
        "notation" : "elsewhere-in-ireland",
        "uri" : self.ns["code-residence"]["elsewhere-in-ireland"],
      },
      {
        "notation" : "outside-ireland",
        "uri" : self.ns["code-residence"]["outside-ireland"],
      },
      {
        "notation" : "total",
        "uri" : self.ns["code-residence"]["total"],
      },
    ]
    
  def callback(self, dimensions, line):
    for key, obsValue in enumerate(line):
      self.appendObservation(
        dimensions + [self.usualResidenceIndexToConcept[key]],
        obsValue
      )
    
    
if __name__ == "__main__":
  cur = ConvertUsualResidence(
    title = "Usually resident population aged one year and over by usual residence one year before Census Day, 2006"
  )
  cur.main()

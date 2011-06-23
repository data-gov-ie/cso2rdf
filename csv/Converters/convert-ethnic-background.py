#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
from Converter import Converter

# Definition of the paths
DSD = os.path.join("..", "..", "DSDs", "persons-by-ethnic-background.ttl")
ED_FILE = os.path.join("..", "Datasources", "ed", "ethnic_background.csv")
EA_FILE = os.path.join("..", "Datasources", "ea", "ethnic_background.csv")


class ConvertEthnicBackground (Converter):
  
  def __init__(self, title):
    namespaces = {
      # own namespaces
      "code-ethnic-group" : "http://stats.data-gov.ie/codelist/ethnic-group/",
    }
    Converter.__init__(self, DSD, title, namespaces, ED_FILE, EA_FILE)
    
    self.setAppendedDimensions([
      self.ns["prop"]["ethnicGroup"],
    ])
    
    self.ethnicGroupIndexToConcept = [
      {
        "notation" : "white-irish",
        "uri" : self.ns["code-ethnic-group"]["white-irish"],
      },
      {
        "notation" : "white-irish-traveller",
        "uri" : self.ns["code-ethnic-group"]["white-irish-traveller"],
      },
      {
        "notation" : "other-white",
        "uri" : self.ns["code-ethnic-group"]["other-white"],
      },
      {
        "notation" : "black",
        "uri" : self.ns["code-ethnic-group"]["black"],
      },
      {
        "notation" : "asian",
        "uri" : self.ns["code-ethnic-group"]["asian"],
      },
      {
        "notation" : "other",
        "uri" : self.ns["code-ethnic-group"]["other"],
      },
      {
        "notation" : "not-stated",
        "uri" : self.ns["code-ethnic-group"]["not-stated"],
      },
      {
        "notation" : "total",
        "uri" : self.ns["code-ethnic-group"]["total"],
      },
    ]
    
  def callback(self, dimensions, line):
    for key, obsValue in enumerate(line):
      self.appendObservation(
        dimensions + [self.ethnicGroupIndexToConcept[key]],
        obsValue
      )
    
    
if __name__ == "__main__":
  ceb = ConvertEthnicBackground(
    title = "Usually resident population by ethnic or cultural background, 2006"
  )
  ceb.main()

#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
from Converter import Converter

# Definition of the paths
DSD = os.path.join("..", "..", "DSDs", "persons-by-gender-and-age.ttl")
ED_FILE = os.path.join("..", "Datasources", "ed", "gender-age.csv")
EA_FILE = os.path.join("..", "Datasources", "ea", "gender-age.csv")


class ConvertGenderAge (Converter):
  
  def __init__(self, title):
    namespaces = {
      "sdmx-code" : "http://purl.org/linked-data/sdmx/2009/code#",
      # Our namespaces
      "code-age1" : "http://stats.govdata.ie/codelist/age1/",
    }
    Converter.__init__(self, DSD, title, namespaces, ED_FILE, EA_FILE)
    self.setAppendedDimensions([
      self.ns["sdmx-dimension"]["sex"],
      self.ns["prop"]["age1"],
    ])
    self.sexIndexToConcept = [
      {
        "notation" : "T",
        "uri" : self.ns["sdmx-code"]["sex-T"],
      },
      {
        "notation" : "M",
        "uri" : self.ns["sdmx-code"]["sex-M"],
      },
      {
        "notation" : "F",
        "uri" : self.ns["sdmx-code"]["sex-F"],
      },
    ]
   
  def getAge(self, age):
    age = str(age)
    if age == "19+":
      concept = {
        "notation" : "19-and-more",
        "uri" : self.ns["code-age1"]["19-and-more"],
      }
    elif age == "Total":
      concept = {
        "notation" : "total",
        "uri" : self.ns["code-age1"]["total"],
      }
    else:
      concept = {
        "notation" : age,
        "uri" : self.ns["code-age1"][age],
      }
      
    return concept
  
  def callback(self, dimensions, line):
    for key, obsValue in enumerate(line[1:]):
      self.appendObservation(
        dimensions + [self.sexIndexToConcept[key]] + [self.getAge(str(line[0]))],
        obsValue
      )


if __name__ == "__main__":
  cr = ConvertGenderAge(
    title = "Persons aged 18 and under by sex and single year of age and persons aged 19 and over by sex, 2006",
  )
  cr.main()

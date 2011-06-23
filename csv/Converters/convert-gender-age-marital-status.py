#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
from Converter import Converter

# Definition of the paths
DSD = os.path.join("..", "..", "DSDs", "persons-by-gender-age-and-marital-status.ttl")
ED_FILE = os.path.join("..", "Datasources", "ed", "gender-age-marital_status.csv")
EA_FILE = os.path.join("..", "Datasources", "ea", "gender-age-marital_status.csv")


class ConvertGenderAgeMaritalStatus (Converter):
  
  def __init__ (self, title):
    namespaces = {
      "sdmx-code" : "http://purl.org/linked-data/sdmx/2009/code#",
      # own namespaces
      "code-marital" : "http://stats.data-gov.ie/codelist/marital-status/",
      "code-age2" : "http://stats.data-gov.ie/codelist/age2/",
    }
    Converter.__init__(self, DSD, title, namespaces, ED_FILE, EA_FILE)
    
    self.setAppendedDimensions([
      self.ns["sdmx-dimension"]["sex"],
      self.ns["prop"]["maritalStatus"],
      self.ns["prop"]["age2"],
    ])
    
    self.getAge = {
      "0 - 4 years" : {
        "notation" : "0-4",
        "uri" : self.ns["code-age2"]["0-4"],
      },
      "5 - 9 years" : {
        "notation" : "5-9",
        "uri" : self.ns["code-age2"]["5-9"],
      },
      "10 - 14 years" : {
        "notation" : "10-14",
        "uri" : self.ns["code-age2"]["10-14"],
      },
      "15 - 19 years" : {
        "notation" : "15-19",
        "uri" : self.ns["code-age2"]["15-19"],
      },
      "20 - 24 years" : {
        "notation" : "20-24",
        "uri" : self.ns["code-age2"]["20-24"],
      },
      "25 - 29 years" : {
        "notation" : "25-29",
        "uri" : self.ns["code-age2"]["25-29"],
      },
      "30 - 34 years" : {
        "notation" : "30-34",
        "uri" : self.ns["code-age2"]["30-34"],
      },
      "35 - 39 years" : {
        "notation" : "35-39",
        "uri" : self.ns["code-age2"]["35-39"],
      },
      "40 - 44 years" : {
        "notation" : "40-44",
        "uri" : self.ns["code-age2"]["40-44"],
      },
      "45 - 49 years" : {
        "notation" : "45-49",
        "uri" : self.ns["code-age2"]["45-49"],
      },
      "50 - 54 years" : {
        "notation" : "50-54",
        "uri" : self.ns["code-age2"]["50-54"],
      },
      "55 - 59 years" : {
        "notation" : "55-59",
        "uri" : self.ns["code-age2"]["55-59"],
      },
      "60 - 64 years" : {
        "notation" : "60-64",
        "uri" : self.ns["code-age2"]["60-64"],
      },
      "65 - 69 years" : {
        "notation" : "65-69",
        "uri" : self.ns["code-age2"]["65-69"],
      },
      "70 - 74 years" : {
        "notation" : "70-74",
        "uri" : self.ns["code-age2"]["70-74"],
      },
      "75 - 79 years" : {
        "notation" : "75-79",
        "uri" : self.ns["code-age2"]["75-79"],
      },
      "80 - 84 years" : {
        "notation" : "80-84",
        "uri" : self.ns["code-age2"]["80-84"],
      },
      "85 years and over" : {
        "notation" : "85-and-more",
        "uri" : self.ns["code-age2"]["85-and-more"],
      },
      "Total" : {
        "notation" : "total",
        "uri" : self.ns["code-age2"]["total"],
      },
    }
    
    self.maritalStatusIndexToConcept = [
      {
        "notation" : "total",
        "uri" : self.ns["code-marital"]["total"],
      },
      {
        "notation" : "single",
        "uri" : self.ns["code-marital"]["single"],
      },
      {
        "notation" : "married",
        "uri" : self.ns["code-marital"]["married"],
      },
      {
        "notation" : "separated",
        "uri" : self.ns["code-marital"]["separated"],
      },
      {
        "notation" : "divorced",
        "uri" : self.ns["code-marital"]["divorced"],
      },
      {
        "notation" : "widowed",
        "uri" : self.ns["code-marital"]["widowed"],
      },
    ]
    
  def getGender(self, index):
    if index in range(0, 6):
      return {
        "notation" : "M",
        "uri" : self.ns["sdmx-code"]["sex-M"],
      }
    elif index in range(6, 12):
      return {
        "notation" : "F",
        "uri" : self.ns["sdmx-code"]["sex-F"],
      }
    
  def getMaritalStatus(self, index):
    return self.maritalStatusIndexToConcept[index % 6]
    
  def callback(self, dimensions, line):
    age = self.getAge[line[0].strip()]
    for key, obsValue in enumerate(line[1:]):
      self.appendObservation(
        dimensions + [self.getGender(key), self.getMaritalStatus(key), age],
        obsValue
      )
    

if __name__ == "__main__":
  cgams = ConvertGenderAgeMaritalStatus(
    title = "Persons by sex, age and marital status, 2006"
  )
  cgams.main()

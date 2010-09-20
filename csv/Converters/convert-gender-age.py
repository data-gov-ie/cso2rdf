#!/usr/bin/env python
#-*- coding:utf-8 -*-

import csv, itertools, os, RDF, re, sys
from Converter import Converter

# Definition of the paths
DSD = os.path.join("..", "..", "DSDs", "persons-by-gender-and-age.ttl")
ED_FILE = os.path.join("..", "Datasources", "ed", "gender-age.csv")
EA_FILE = os.path.join("..", "Datasources", "ea", "gender-age.csv")


class ConvertGenderAge (Converter):
  """
    Class for converting CSO datasets about religion
  """
  
  def __init__(self, DSD, title):
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
    
  def callbackEA(self, dimensions, line):
    for key, obsValue in enumerate(line[1:]):
      self.appendObservation(
        dimensions + [self.sexIndexToConcept[key]] + [self.getAge(str(line[0]))],
        str(obsValue)
      )
    
  def callbackED(self, dimensions, line):
    for key, obsValue in enumerate(line[1:]):
      self.appendObservation(
        dimensions + [self.sexIndexToConcept[key]] + [self.getAge(str(line[0]))],
        str(obsValue)
      )
    
  def computeAggregates(self):
    output = self.getTraditionalCountiesMapping()
    
    for traditionalCounty in output:
      if output[traditionalCounty].has_key("exactMatch"):
        administrativeCounty = output[traditionalCounty]["exactMatch"]
        query = """PREFIX prop: <http://stats.govdata.ie/property/>
          PREFIX sdmx: <http://purl.org/linked-data/sdmx#>

          SELECT ?observation WHERE {{
           ?observation a sdmx:Observation ;
             prop:geoArea ?geo .
           FILTER (?geo = <{0}>)
          }}
        """.format(administrativeCounty)
        for observation in self.sparql(query):
          dimensions = [
            {
              "notation" : "2006",
            },
            {
              "notation" : output[traditionalCounty]["notation"],
              "uri" : traditionalCounty,
            },
          ]
          observation = str(observation["observation"].uri)
          query = """PREFIX prop: <http://stats.govdata.ie/property/>
            PREFIX sdmx-dimension: <http://purl.org/linked-data/sdmx/2009/dimension#>
            
            SELECT ?sex ?age ?population WHERE {{
              <{0}> sdmx-dimension:sex ?sex ;
                prop:age1 ?age ;
                prop:population ?population .
          }}""".format(observation)
          for statement in self.sparql(query):
            sex = str(statement["sex"].uri)
            age = str(statement["age"].uri)
            population = str(statement["population"].literal_value["string"])
            dimensions += [
              {
                "notation" : self.getLastPartOfUri(sex),
                "uri" : sex,
              },
              {
                "notation" : self.getLastPartOfUri(age),
                "uri" : age,
              },
            ]
          self.appendObservation(dimensions, population)
          
      elif output[traditionalCounty].has_key("narrower"):
        dimensions = [
          {
            "notation" : "2006",
          },
          {
            "notation" : output[traditionalCounty]["notation"],
            "uri" : traditionalCounty,
          },
        ]
        narrowers = output[traditionalCounty]["narrower"]
        
        sexes = self.sexIndexToConcept
        ages = [self.getAge(age) for age in range(0, 19) + ["19+", "Total"]]
        products = [element for element in itertools.product(sexes, ages)]
        for product in products:
          sex = product[0]
          age = product[1]
          query = """PREFIX prop: <http://stats.govdata.ie/property/>
            PREFIX sdmx: <http://purl.org/linked-data/sdmx#>
            PREFIX sdmx-dimension: <http://purl.org/linked-data/sdmx/2009/dimension#>

            SELECT ?population WHERE {{
              ?observation a sdmx:Observation ;
                prop:geoArea ?geo ;
                sdmx-dimension:sex ?sex ;
                prop:age1 ?age ;
                prop:population ?population .
              FILTER (?sex = <{0}>)
              FILTER (?age = <{1}>)
              FILTER ({2})
            }}""".format(
            str(sex["uri"].uri),
            str(age["uri"].uri),
            " || ".join(
              ["?geo = <{0}>".format(narrower) for narrower in narrowers]
            )
          )
          populationTotal = 0
          for populationPart in self.sparql(query):
            populationTotal += int(
              populationPart["population"].literal_value["string"]
            )
          
          populationTotal = str(populationTotal)
          self.appendObservation(
            dimensions + [sex, age],
            populationTotal
          )
          
     
if __name__ == "__main__":
  cr = ConvertGenderAge(
    DSD = DSD,
    title = "Persons aged 18 and under by sex and single year of age and persons aged 19 and over by sex, 2006",
  )
  cr.main()
  cr.write()

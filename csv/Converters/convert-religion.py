#!/usr/bin/env python
#-*- coding:utf-8 -*-

# TODO:
# compute values for geographical entities that are not in out datasets (traditional counties, maybe even state) - in which step will we do that?
# (a) afterwards with SPARQL queries

import csv, os, RDF, re
from RDFModel import RDFModel


class ConvertReligion (RDFModel):
  """
    Class for converting CSO datasets about religion
  """
  
  def __init__(self, datasetID):
    self.datasetID = datasetID
    namespaces = {
      "qb" : "http://purl.org/linked-data/cube#",
      "sdmx" : "http://purl.org/linked-data/sdmx#",
      "sdmx-dimension" : "http://purl.org/linked-data/sdmx/2009/dimension#",
      "sdmx-metadata" : "http://purl.org/linked-data/sdmx/2009/metadata#",
      "skos" : "http://www.w3.org/2004/02/skos/core#",
      "year" : "http://reference.data.gov.uk/id/year/",
      # own namespaces
      "code" : "http://stats.govdata.ie/codelist/",
      "data" : "http://stats.govdata.ie/data/",
      "dsd" : "http://stats.govdata.ie/dsd/",
      "geo" : "http://geo.govdata.ie/",
      "prop" : "http://stats.govdata.ie/property/",
      "religion-code" : "http://stats.govdata.ie/codelist/religion/",
    }
    RDFModel.__init__(self, namespaces)
    
    self._fileEDs = open(os.path.join("..", "datasources", "ed", "religion.csv"), "r")
    self.fileEDs = csv.reader(self._fileEDs, delimiter=";")
    self._fileEAs = open(os.path.join("..", "datasources", "ea", "religion.csv"), "r")
    self.fileEAs = csv.reader(self._fileEAs, delimiter=";")
    
    self.regexp = {
      "EAs" : re.compile(
        "^(?P<name>[\D\s]+)\s(?P<c1_part1>\d{2})(?:\/)?(?P<c1_part2>\d{3})?(?:,\s?\d{2}\/)?(?P<c2>\d{3})?$"
      ),
      "EDs" : re.compile(
        "^(?P<code1>\d{3})?(?:\/)?(?P<code2>\d{3})?\s?(?P<name1>[^\/]+)(?:\/)?(?P<name2>[^\/]+)?$"
      )
    }
    self.provinces = ["Connacht", "Leinster", "Munster", "Ulster"]
    self.typeToUri = {
      "AdministrativeCounty" : "county",
      "TraditionalCounty" : "traditional-county",
      "City" : "city",
    }
    self.datasetID = datasetID
    self.buffers = {
      "areaURI" : "",
      "broader" : {
        "notation" : "",
        "type" : "",
        "uri" : "",
      },      
    }
    
  def getGeo(self, conceptType, **kwargs):
    ## Output template
    geo = {
      "notation" : "",
      "type" : "",
      "uri" : "",
    }
    
    ## Enumeration area
    if conceptType == "EnumerationArea":
      geo["notation"] = self.stringForUri(
        "{0} ea{1}".format(
          self.buffers["broader"]["notation"],
          kwargs["code"]
        )
      )
      if self.buffers["broader"]["type"] == "City":
        geo["uri"] = self.ns["geo"][
          self.stringForUri(
            "city/{0}/ea/{1}".format(
              self.clean("-city", self.buffers["broader"]["notation"]),
              kwargs["code"]
            )
          )
        ]
      elif self.buffers["broader"]["type"] == "suburbs":
        geo["uri"] = self.ns["code"][
          "suburbs/{0}/ea/{1}".format(
            self.clean("-suburbs", self.buffers["broader"]["notation"]),
            kwargs["code"]
          )
        ]
      elif self.buffers["broader"]["type"] == "AdministrativeCounty":
        geo["uri"] = self.ns["geo"][
          "county/{0}/ea/{1}".format(
            self.clean("-county", self.buffers["broader"]["notation"]),
            kwargs["code"]
          )
        ]

    ## Electoral division
    elif conceptType == "ElectoralDivision":
      geo = {
        "notation" : self.stringForUri(
          "{0} ed{1}".format(self.buffers["broader"]["notation"], kwargs["code"])
        ),
        "uri" : self.ns["geo"][
          self.stringForUri(
            "{0}/{1}/ed/{2}".format(
              self.typeToUri[self.buffers["broader"]["type"]],
              self.clean("-city", self.buffers["broader"]["notation"]),
              kwargs["code"]
            )
          )
        ],
      }
      
    ## Administrative county
    elif conceptType == "AdministrativeCounty":
      countyName = self.clean("county", kwargs["name"])
      geo = {
        "notation" : self.stringForUri(countyName),
        "type" : "AdministrativeCounty",
        "uri" : self.ns["geo"]["county/{0}".format(self.stringForUri(countyName))],
      }
      self.buffers["broader"] = geo
      
    ## City
    elif conceptType == "City":
      cityName = self.clean("city", kwargs["name"])
      geo = {
        "notation" : self.stringForUri(kwargs["name"]),
        "type" : "City",
        "uri" : self.ns["geo"]["city/{0}".format(self.stringForUri(cityName))],
      }
      self.buffers["broader"] = geo
      
    ## Province
    elif conceptType == "Province":
      geo = {
        "notation" : self.stringForUri(kwargs["name"]),
        "type" : "Province",
        "uri" : self.ns["geo"]["province/{0}".format(self.stringForUri(kwargs["name"]))],
      }
      self.buffers["broader"] = geo
      
    ## Paired enumeration area
    elif conceptType == "paired ea":
      geo = {
        "notation" : "{0}-ea{1}-{2}".format(
          self.stringForUri(kwargs["name1"]),
          kwargs["code1"],
          kwargs["code2"]
        ),
        "type" : "paired ea",
      }
      if self.buffers["broader"]["type"] == "City":
        geo["uri"] = self.ns["code"]["cso-specific/city/{0}/ea/{1}-{2}".format(
          self.clean("-city", self.buffers["broader"]["notation"]),
          kwargs["code1"],
          kwargs["code2"]
        )]
      elif self.buffers["broader"]["type"] == "suburbs":
        geo["uri"] = self.ns["code"]["cso-specific/suburbs/{0}/ea/{1}-{2}".format(
          self.clean("-suburbs", self.buffers["broader"]["notation"]),
          kwargs["code1"],
          kwargs["code2"]
        )]
      elif self.buffers["broader"]["type"] == "AdministrativeCounty":
        geo["uri"] = self.ns["code"]["cso-specific/county/{0}/ea/{1}-{2}".format(
          self.clean("-county", self.buffers["broader"]["notation"]),
          kwargs["code1"],
          kwargs["code2"]
        )]
    
    ## Paired electoral division
    elif conceptType == "paired ed":
      geo = {
        "notation" : "{0}-ed{1}-{2}".format(
          self.buffers["broader"]["notation"],
          kwargs["code1"],
          kwargs["code2"]
        ),
        "type" : "paired ed",
        "uri" : self.ns["code"]["cso-specific/{0}/{1}/ed/{2}-{3}".format(
          self.typeToUri[self.buffers["broader"]["type"]],
          self.buffers["broader"]["notation"],
          kwargs["code1"],
          kwargs["code2"]
        )],
      }
    
    elif conceptType == "suburbs":
      geo["notation"] = self.stringForUri(kwargs["name"])
      geo["type"] = "suburbs"
      geo["uri"] = self.ns["code"]["cso-specific/suburbs/{0}".format(
        self.clean("-suburbs", geo["notation"]))
      ]
      self.buffers["broader"] = geo
    
    elif conceptType == "State":
      geo = {
        "notation" : "roi",
        "type" : "State",
        "uri" : self.ns["geo"]["roi"],
      }
      self.buffers["broader"] = geo
        
    if not geo.has_key("notation") or not geo.has_key("uri"):
      raise Exception("Geographic concept lacks notation or URI.") # Add helpful information!
      
    return geo
  
  def appendObservation(self, dimensions, obsValue):
    # Template for dimensions parameter:
    # dimensions = [
    #   {
    #     "notation" : "",
    #     "uri" : "",
    #   },
    # ]
    
    observationUri = self.ns["data"]["/".join(
      [self.datasetID] + [dimension["notation"] for dimension in dimensions]
    )]
    print "Adding observation: <{0}>".format(observationUri)
    self.appendToSubject(
      observationUri,
      [
        [
          self.ns["rdf"]["type"],
          self.ns["sdmx"]["Observation"],
        ],
        [
          self.ns["sdmx-dimension"]["refPeriod"],
          self.ns["year"][dimensions[0]["notation"]],
        ],
        [
          self.ns["prop"]["geoArea"],
          dimensions[1]["uri"], # Original: self.buffers["areaURI"],
        ],
        [
          self.ns["prop"]["religion"],
          self.ns["religion-code"][dimensions[2]["notation"]],
        ],
        [
          self.ns["prop"]["population"],
          RDF.Node(
            literal = obsValue,
            datatype = self.ns["xsd"]["int"].uri
          ),
        ],
      ]
    )
    
  def addFromEDs(self):
    for line in self.fileEDs:
      if self.fileEDs.line_num > 3: # Skip first three lines
        dimensions = [{"notation" : "2006"}]
        
        geoArea = line[0].strip()
        match = self.regexp["EDs"].match(geoArea)
        code1 = match.group("code1")
        code2 = match.group("code2")
        name1 = match.group("name1")
        name2 = match.group("name2")
        
        if name1 and not code1: # then it's a top level area
          if name1 == "State": # then it's the Republic of Ireland
            geo = self.getGeo(conceptType = "State")
          elif name1 in self.provinces: # then it's a province
            geo = self.getGeo(conceptType = "Province", name = name1)
          elif "City" in name1: # then it's a city
            geo = self.getGeo(conceptType = "City", name = name1)
          elif not name1 == "State": # then it's an administrative county
            geo = self.getGeo(conceptType = "AdministrativeCounty", name = name1)
        elif code1 and not code2: # then it's normal ED
          geo = self.getGeo(conceptType = "ElectoralDivision", name = name1, code = code1)
        elif code2: # then it's paired ED
          geo = self.getGeo(conceptType = "paired ed", name = name1, code1 = code1, code2 = code2)
        elif not name1:
          raise Exception("Parsing error for geographic area {0}.".format(geoArea))

        dimensions.append(geo)
        
        for key, obsValue in enumerate(line[1:]):
          key += 1 # Switching from zero offset
          self.appendObservation(dimensions + [{"notation" : str(key),}], obsValue)
            
  def addFromEAs(self):
    for line in self.fileEAs:
      if self.fileEAs.line_num > 3: # Skip first three lines
        dimensions = [{"notation" : "2006"}]
        
        geoArea = line[0].strip()
        match = self.regexp["EAs"].match(geoArea)
        if match:
          name = match.group("name")
          c1_part1 = match.group("c1_part1")
          c1_part2 = match.group("c1_part2")
          c2 = match.group("c2")
          
          if name and not c1_part2: # then it's a broader area
            if "Suburbs" in name: # then it is "suburbs" - an unspecified type
              geo = self.getGeo(conceptType = "suburbs", name = name)
            elif "City" in name: # then it's a "city"
              geo = self.getGeo(conceptType = "City", name = name)
            elif name in ["South Dublin", "Fingal", "Dún Laoghaire-Rathdown"]: # then it's an "adminitrative county"
              geo = self.getGeo(conceptType = "AdministrativeCounty", name = name)
            else:
              raise Exception("Wrong name: {0}".format(name))
          elif c1_part2 and not c2: # then it's a normal EA
            geo = self.getGeo(conceptType = "EnumerationArea", code = c1_part2)
          elif c2: # then it's a paired EA
            geo = self.getGeo(conceptType = "paired ea", name1 = name, code1 = c1_part2, code2 = c2)
          
          dimensions.append(geo)
          
          for key, obsValue in enumerate(line[1:]):
            key += 1
            self.appendObservation(dimensions + [{"notation" : str(key)}], obsValue)
  
  def initiateDataset(self, dsd, title):
    self.appendToSubject(
      self.ns["data"][self.datasetID],
      [
        [
          self.ns["rdf"]["type"],
          self.ns["qb"]["DataSet"],
        ],
        [
          self.ns["qb"]["structure"],
          self.ns["dsd"][dsd],
        ],
        [
          self.ns["sdmx-metadata"]["title"],
          RDF.Node(
            literal = title,
            language = "en"
          )
        ],
      ]
    )
              
  def main(self):
    self.initiateDataset(dsd = "persons-by-religion", title = "Number of persons by religion, 2006")
    self.addFromEDs()
    self.addFromEAs()
    self._fileEAs.close()
    self._fileEDs.close()
    self.calculateAggregates()
        
  def write(self):
    RDFModel.write(self, os.path.join("..", "converted-data", "{0}.ttl".format(self.datasetID)))

  def calculateAggregates(self):
    pass
    
     
if __name__ == "__main__":
  cr = ConvertReligion(datasetID = "persons-by-religion")
  cr.main()
  cr.write()

#!/usr/bin/env python
#-*- coding:utf-8 -*-

import csv, os, re, RDF, sys, unicodedata
sys.path.append(os.path.join("..", "..", "RDFModel"))
from RDFModel import RDFModel

# Definition of the paths
PATH_TO_ED_FILE = os.path.join("..", "Datasources", "ed", "religion.csv")
PATH_TO_EA_FILE = os.path.join("..", "Datasources", "ea", "religion.csv")
PATH_TO_OUTPUT = os.path.join("..", "Datasets", "geo")


class GeoAreasWriter (RDFModel):
  """
    Generate RDF Turtle list of geographical areas from CSV files.
  """
  
  def __init__(self, fileEDs, fileEAs):
    namespaces = {
      "skos" : "http://www.w3.org/2004/02/skos/core#",
      ## Custom namespaces
      "geo" : "http://geo.govdata.ie/",
      "code" : "http://stats.govdata.ie/codelist/",
      "code-geo" : "http://stats.govdata.ie/codelist/geo/",
    }
    RDFModel.__init__(self, namespaces)
    ## Initiating RDF models used
    self.models = {
      "topLevel" : RDFModel(namespaces),
      "eas" : RDFModel(namespaces),
      "eds" : RDFModel(namespaces),
      "csoStuff" : RDFModel(namespaces),
    }
    ## Bootstrapping data
    self.models["topLevel"].bootstrap("top-level-bootstrap.ttl")
    
    self._fileEDs = open(fileEDs, "r")
    self.fileEDs = csv.reader(self._fileEDs, delimiter=";")
    self._fileEAs = open(fileEAs, "r")
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
    self.cityToProvince = {
      "Dublin City 02" : "Leinster",
      "South Dublin 03" : "Leinster",
      "Fingal 04" : "Leinster",
      "Dún Laoghaire-Rathdown 05" : "Leinster",
      "Cork City 17" : "Munster",
      "Cork Suburbs 18" : "Munster",
      "Limerick City 20" : "Munster",
      "Limerick Suburbs 21" : "Munster",
      "Limerick Suburbs in Clare 16" : "Munster",
      "Waterford City 24" : "Munster",
      "Waterford Suburbs 07" : "Munster",
      "Waterford Suburbs in Kilkenny 07" : "Leinster",
      "Galway City 26" : "Connacht",
    }
    self.typeToUri = {
      "AdministrativeCounty" : "county",
      "TraditionalCounty" : "traditional-county",
      "City" : "city",
    }
    self.getTraditionalCounty = {
      "North Tipperary" : "Tipperary",
      "South Tipperary" : "Tipperary",
      "Dún Laoghaire-Rathdown" : "Dublin",
      "Fingal" : "Dublin",
      "South Dublin" : "Dublin",
    }
    self.buffers = {
      "broader" : {
        "notation" : "",
        "prefLabel" : "",
        "type" : "",
        "uri" : "",
      },
    }
     
  def getConcept(self, conceptType, **kwargs):
    ## Template for returned dict
    concept = {
      "model" : "", # RDF model to which to append to
      "type" : "", # rdfs:Class which the concept is an instance of
      "prefLabel" : "", # Preferred label for the concept
      "notation" : "", # Notation that can identify the concept in URIs
      "codeLists" : [], # An array of codelists on which the concept should be featured on
    }
    if conceptType == "EnumerationArea":
      concept = {
        "model" : self.models["eas"],
        "type" : "EnumerationArea",
        "prefLabel" : "{0} {1}".format(self.buffers["broader"]["prefLabel"], kwargs["code"]),
        "notation" : self.stringForUri("{0} ea{1}".format(self.buffers["broader"]["notation"], kwargs["code"])),
        "codeLists" : [
          self.ns["code-geo"]["census-2006"],
          self.ns["code-geo"]["roi"],
        ],
      }
      if self.buffers["broader"]["type"] == "City":
        concept["uri"] = self.ns["geo"][
          self.stringForUri(
            "city/{0}/ea/{1}".format(
              self.clean("-city", self.buffers["broader"]["notation"]),
              kwargs["code"]
            )
          )
        ]
      elif self.buffers["broader"]["type"] == "suburbs":
        concept["uri"] = self.ns["code"][
          "suburbs/{0}/ea/{1}".format(
            self.clean("-suburbs", self.buffers["broader"]["notation"]),
            kwargs["code"]
          )
        ]
      elif self.buffers["broader"]["type"] == "AdministrativeCounty":
        concept["uri"] = self.ns["geo"][
          "county/{0}/ea/{1}".format(
            self.clean("-county", self.buffers["broader"]["notation"]),
            kwargs["code"]
          )
        ]
    elif conceptType == "ElectoralDivision":
      concept = {
        "model" : self.models["eds"],
        "uri" : self.ns["geo"][
          self.stringForUri(
            "{0}/{1}/ed/{2}".format(
              self.typeToUri[self.buffers["broader"]["type"]],
              self.clean("-city", self.buffers["broader"]["notation"]),
              kwargs["code"]
            )
          )
        ],
        "type" : "ElectoralDivision",
        "prefLabel" : kwargs["name"],
        "notation" : self.stringForUri(
          "{0} ed{1}".format(self.buffers["broader"]["notation"], kwargs["code"])
        ),
        "codeLists" : [
          self.ns["code-geo"]["census-2006"],
          self.ns["code-geo"]["roi"],
        ],
      }
    elif conceptType == "AdministrativeCounty":
      countyName = self.clean("county", kwargs["name"])
      concept = {
        "model" : self.models["topLevel"],
        "uri" : self.ns["geo"]["county/{0}".format(self.stringForUri(countyName))],
        "type" : "AdministrativeCounty",
        "prefLabel" : "County {0} (administrative)".format(countyName),
        "notation" : self.stringForUri(countyName),
        "codeLists" : [
          self.ns["code-geo"]["census-2006"],
          self.ns["code-geo"]["top-level"],
          self.ns["code-geo"]["roi"],
        ],
      }
      if self.getTraditionalCounty.has_key(countyName):
        self.buffers["broader"]["uri"] = self.ns["geo"][
          "traditional-county/{0}".format(
            self.stringForUri(self.getTraditionalCounty[countyName])
          )
        ]
      else:
        self.buffers["broader"]["uri"] = self.ns["geo"][
          "traditional-county/{0}".format(self.stringForUri(countyName))
        ]
    elif conceptType == "City":
      cityName = self.clean("city", kwargs["name"])
      concept = {
        "model" : self.models["topLevel"],
        "uri" : self.ns["geo"]["city/{0}".format(self.stringForUri(cityName))],
        "type" : "City",
        "prefLabel" : kwargs["name"],
        "notation" : self.stringForUri(kwargs["name"]),
        "codeLists" : [
          self.ns["code-geo"]["census-2006"],
          self.ns["code-geo"]["top-level"],
          self.ns["code-geo"]["roi"],
        ],
      }
      self.buffers["broader"]["uri"] = self.ns["geo"]["traditional-county/{0}".format(cityName.lower())]
    elif conceptType == "paired ed":
      concept = {
        "model" : self.models["csoStuff"],
        "uri" : self.ns["code"]["cso-specific/{0}/{1}/ed/{2}-{3}".format(
          self.typeToUri[self.buffers["broader"]["type"]],
          self.buffers["broader"]["notation"],
          kwargs["code1"],
          kwargs["code2"]
        )],
        "prefLabel" : "{0} {1}, {2} {3}".format(kwargs["name1"], kwargs["code1"], kwargs["name2"], kwargs["code2"]),
        "notation" : "{0}-ed{1}-{2}".format(self.buffers["broader"]["notation"], kwargs["code1"], kwargs["code2"]),
        "type" : "",
        "codeLists" : [
          self.ns["code-geo"]["census-2006"],
        ],
      }
    elif conceptType == "paired ea":
      concept = {
        "model" : self.models["csoStuff"],
        "prefLabel" : "{0} {1}, {2}".format(kwargs["name1"], kwargs["code1"], kwargs["code2"]),
        "notation" : "{0}-ea{1}-{2}".format(self.stringForUri(kwargs["name1"]), kwargs["code1"], kwargs["code2"]),
        "type" : "",
        "codeLists" : [
          self.ns["code-geo"]["census-2006"],
        ],
      }
      if self.buffers["broader"]["type"] == "City":
        concept["uri"] = self.ns["code"]["cso-specific/city/{0}/ea/{1}-{2}".format(
          self.clean("-city", self.buffers["broader"]["notation"]),
          kwargs["code1"],
          kwargs["code2"]
        )]
      elif self.buffers["broader"]["type"] == "suburbs":
        concept["uri"] = self.ns["code"]["cso-specific/suburbs/{0}/ea/{1}-{2}".format(
          self.clean("-suburbs", self.buffers["broader"]["notation"]),
          kwargs["code1"],
          kwargs["code2"]
        )]
      elif self.buffers["broader"]["type"] == "AdministrativeCounty":
        concept["uri"] = self.ns["code"]["cso-specific/county/{0}/ea/{1}-{2}".format(
          self.clean("-county", self.buffers["broader"]["notation"]),
          kwargs["code1"],
          kwargs["code2"]
        )]
    elif conceptType == "suburbs":
      notation = self.stringForUri(kwargs["name"])
      concept = {
        "model" : self.models["csoStuff"],
        "uri" : self.ns["code"]["cso-specific/suburbs/{0}".format(self.clean("-suburbs", notation))],
        "prefLabel" : kwargs["name"],
        "notation" : notation,
        "type" : "suburbs",
        "codeLists" : [
          self.ns["code-geo"]["census-2006"],
        ],
      }
    else:
      raise ValueError("Wrong conceptType argument: {0}".format(conceptType))
    
    print "Adding concept: \nURI: {0}\nprefLabel: {1}\nnotation: {2}".format(
      concept["uri"],
      concept["prefLabel"],
      concept["notation"]
    )
    
    concept["model"].appendToSubject(
      concept["uri"],
      [
        [
          self.ns["rdf"]["type"],
          self.ns["skos"]["Concept"],
        ],
        [
          self.ns["skos"]["prefLabel"],
          RDF.Node(literal = concept["prefLabel"], language = "en"),
        ],
        [
          self.ns["skos"]["notation"],
          RDF.Node(literal = concept["notation"]),
        ],
        [
          self.ns["skos"]["broader"],
          self.buffers["broader"]["uri"],
        ],
      ]
    )
    concept["model"].appendToSubject(
      self.buffers["broader"]["uri"],
      [
        [
          self.ns["skos"]["narrower"],
          concept["uri"],
        ],
      ]
    )
    if kwargs.has_key("pairedURI"):
      concept["model"].appendToSubject(
        concept["uri"],
        [
          [
            self.ns["skos"]["broader"],
            kwargs["pairedURI"],
          ],
        ]
      )
      concept["model"].appendToSubject(
        kwargs["pairedURI"],
        [
          [
            self.ns["skos"]["narrower"],
            concept["uri"],
          ],
        ]
      )
    if not conceptType in ["paired ed", "paired ea", "suburbs"]:
      concept["model"].appendToSubject(
        concept["uri"],
        [
          [
            self.ns["rdf"]["type"],
            self.ns["geo"][concept["type"]],
          ],
        ]
      )
    
    for codeList in concept["codeLists"]:
      concept["model"].appendToSubject(
        concept["uri"],
        [
          [
            self.ns["skos"]["inScheme"],
            codeList,
          ],
        ]
      )  
    return concept
      
  def addEDs(self):
    """
      Add electoral divisions
    """
        
    for line in self.fileEDs:
      if self.fileEDs.line_num > 3: # Skip first three lines
        geoArea = line[0].strip()
        match = self.regexp["EDs"].match(geoArea)
        code1 = match.group("code1")
        code2 = match.group("code2")
        name1 = match.group("name1")
        name2 = match.group("name2")
        
        if name1 and not code1: # then it's a top level area
          if name1 in self.provinces: # then it's a province
            self.buffers["broader"]["prefLabel"] = name1
            self.buffers["broader"]["notation"] = self.stringForUri(name1)
            self.buffers["broader"]["uri"] = self.ns["geo"][self.stringForUri(name1)]
          elif not name1 == "State": # then it's "a county"
            # set it to broader buffer for the proceeding narrower 
            if "City" in name1:
              conceptType = "City"
            else:
              conceptType = "AdministrativeCounty"
            self.buffers["broader"] = self.getConcept(conceptType = conceptType, name = name1)
            
        elif code1 and not code2: # then it's normal ED
          self.getConcept(
            conceptType = "ElectoralDivision",
            name = name1,
            code = code1
          )
          
        elif code2: # then it's paired ED
          paired = self.getConcept(
            conceptType = "paired ed",
            name1 = name1,
            code1 = code1,
            name2 = name2,
            code2 = code2
          )
          self.getConcept(
            conceptType = "ElectoralDivision",
            name = name1,
            code = code1,
            pairedURI = paired["uri"]
          )
          self.getConcept(
            conceptType = "ElectoralDivision",
            name = name2,
            code = code2,
            pairedURI = paired["uri"]
          )
          
        elif not name1:
          raise Exception("Parsing error for geographic area {0}.".format(geoArea))
    
  def addEAs(self):
    """
      Add enumeration areas
    """
    
    for line in self.fileEAs:
      if self.fileEAs.line_num > 3: # Skip first three lines
        geoArea = line[0].strip()
        match = self.regexp["EAs"].match(geoArea)
        if match:
          name = match.group("name")
          c1_part1 = match.group("c1_part1")
          c1_part2 = match.group("c1_part2")
          c2 = match.group("c2")
          if name and not c1_part2: # then it's a broader area
            # set broader according to dictionary
            self.buffers["broader"]["prefLabel"] = self.cityToProvince[geoArea]
            self.buffers["broader"]["notation"] = self.stringForUri(self.buffers["broader"]["prefLabel"])
            self.buffers["broader"]["uri"] = self.ns["geo"]["province/{0}".format(self.buffers["broader"]["notation"])]
            if "Suburbs" in name: # then it is "suburb" - an unspecified type
              conceptType = "suburbs"
            elif name in ["Dublin City", "Cork City", "Galway City", "Limerick City", "Waterford City"]: # then it's a "city"
              conceptType = "City"
            else:
              if name in ["South Dublin", "Fingal", "Dún Laoghaire-Rathdown"]:
                conceptType = "AdministrativeCounty"
              else:
                raise Exception("Wrong name: {0}".format(name))
            self.buffers["broader"] = self.getConcept(conceptType = conceptType, name = name)
          elif c1_part2 and not c2: # then it's a normal EA
            self.getConcept(conceptType = "EnumerationArea", code = c1_part2)
          elif c2: # then it's a paired EA
            paired = self.getConcept(conceptType = "paired ea", name1 = name, code1 = c1_part2, code2 = c2)
            self.getConcept(conceptType = "EnumerationArea", code = c1_part2, pairedURI = paired["uri"])
            self.getConcept(conceptType = "EnumerationArea", code = c2, pairedURI = paired["uri"])
          
  def main(self):
    self.addEDs()
    self.addEAs()
    
    self._fileEAs.close()
    self._fileEDs.close()
  
  def write(self, name):
    for model in self.models.keys():
      self.models[model].write("{0}-{1}.ttl".format(name, model))


if __name__ == "__main__":
  writer = GeoAreasWriter(
    fileEDs = PATH_TO_ED_FILE,
    fileEAs = PATH_TO_EA_FILE
  )
  writer.main()
  writer.write(
    outputFile = PATH_TO_OUTPUT
  )

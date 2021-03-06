#!/usr/bin/env python
#-*- coding:utf-8 -*-

## TODO
# How come the paired ea receive TraditionalCounty as broader?
# Write unittests for concept type detection

import csv, os, re, RDF, sys, unicodedata
sys.path.append(os.path.join("..", "..", "RDFModel"))
from RDFModel import RDFModel

# Definition of the paths
ED_FILE = os.path.join("..", "Datasources", "ed", "religion.csv")
EA_FILE = os.path.join("..", "Datasources", "ea", "religion.csv")
OUTPUT_FILE = os.path.join("..", "..", "Codelists", "geo")
TOP_LEVEL_BOOTSTRAP_FILE = os.path.join("bootstrap", "top-level.ttl")


class GeoAreasWriter (RDFModel):
  """
    Generate RDF Turtle list of geographical areas from CSV files.
  """
  
  def __init__(self, fileEDs, fileEAs):
    namespaces = {
      "skos" : "http://www.w3.org/2004/02/skos/core#",
      ## Custom namespaces
      "geo" : "http://geo.data-gov.ie/",
      "code-geo" : "http://stats.data-gov.ie/codelist/geo/",
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
    self.models["topLevel"].bootstrap(TOP_LEVEL_BOOTSTRAP_FILE)
    
    self._fileEDs = open(fileEDs, "r")
    self.fileEDs = csv.reader(self._fileEDs, delimiter=";")
    self._fileEAs = open(fileEAs, "r")
    self.fileEAs = csv.reader(self._fileEAs, delimiter=";")

    self.regexp = {
      "EAs" : re.compile(
        "^(?P<name>[\D\s]+)(?=\s|$)\s?(?P<c1_part1>\d{2})?\/?(?P<c1_part2>\d{3})?(?:,\s?\d{2}\/)?(?P<c2>\d{3})?$"
      ),
      "EDs" : re.compile(
        "^(?P<code1>\d{3})?(?:\/)?(?P<code2>\d{3})?\s?(?P<name1>[^\/]+)(?:\/)?(?P<name2>[^\/]+)?$"
      )
    }
    self.provinces = [
      "Connacht",
      "Leinster",
      "Munster",
      "Ulster"
    ]
    self.cityNames = [
      "Dublin City",
      "Cork City",
      "Galway City",
      "Limerick City",
      "Waterford City"
    ]
    self.toBroader = {
      "Dublin City" : {
        "prefLabel" : "Dublin",
        "type" : "TraditionalCounty",
      },
      "Dublin City and Suburbs" : {
        "prefLabel" : "Dublin",
        "type" : "TraditionalCounty",
      },
      "South Dublin" : {
        "prefLabel" : "Dublin",
        "type" : "TraditionalCounty",
        "city plus suburbs" : {
          "prefLabel" : "Dublin City and Suburbs",
          "type" : "city plus suburbs",
        },
      },
      "Fingal" : {
        "prefLabel" : "Dublin",
        "type" : "TraditionalCounty",
        "city plus suburbs" : {
          "prefLabel" : "Dublin City and Suburbs",
          "type" : "city plus suburbs",
        },
      },
      "Dún Laoghaire-Rathdown" : {
        "prefLabel" : "Dublin",
        "type" : "TraditionalCounty",
        "city plus suburbs" : {
          "prefLabel" : "Dublin City and Suburbs",
          "type" : "city plus suburbs",
        },
      },
      "Cork City and Suburbs" : {
        "prefLabel" : "Cork",
        "type" : "TraditionalCounty",
      },
      "Cork City" : {
        "prefLabel" : "Cork",
        "type" : "TraditionalCounty",
      },
      "Cork Suburbs" : {
        "prefLabel" : "Cork",
        "type" : "TraditionalCounty",
        "city plus suburbs" : {
          "prefLabel" : "Cork City and Suburbs",
          "type" : "city plus suburbs",
        },
      },
      "Limerick City and Suburbs" : { # it contains areas both in Limerick and Clare which are both in Munster
        "prefLabel" : "Munster",
        "type" : "Province",
      },
      "Limerick City" : {
        "prefLabel" : "Limerick",
        "type" : "TraditionalCounty",
      },
      "Limerick Suburbs" : {
        "suburbs" : {
          "prefLabel" : "Munster",
          "type" : "Province",
        },
        "city plus suburbs" : {
          "prefLabel" : "Limerick City and Suburbs",
          "type" : "city plus suburbs",
        },
        "EnumerationArea" : {
          "prefLabel" : "Limerick",
          "type" : "TraditionalCounty",
        },
      },
      "Limerick Suburbs in Clare" : {
        "prefLabel" : "Clare",
        "type" : "TraditionalCounty",
        "city plus suburbs" : {
          "prefLabel" : "Limerick City and Suburbs",
          "type" : "city plus suburbs",
        },
      },
      "Waterford City and Suburbs" : { # it contains areas both in Munster (Waterford) and Leinster (Kilkenny)
        "prefLabel" : "Republic of Ireland",
        "type" : "State",
      },
      "Waterford City" : {
        "prefLabel" : "Waterford",
        "type" : "TraditionalCounty",
      },
      "Waterford Suburbs" : {
        "suburbs" : {
          "prefLabel" : "Kilkenny",
          "type" : "TraditionalCounty",
        },
        "EnumerationArea" : {
          "prefLabel" : "Waterford",
          "type" : "TraditionalCounty",
        },
        "city plus suburbs" : {
          "prefLabel" : "Waterford City and Suburbs",
          "type" : "city plus suburbs",
        },
      },
      "Waterford Suburbs in Kilkenny" : {
        "prefLabel" : "Kilkenny",
        "type" : "TraditionalCounty",
        "city plus suburbs" : {
          "prefLabel" : "Waterford City and Suburbs",
          "type" : "city plus suburbs",
        },
      },
      "Galway City" : {
        "prefLabel" : "Galway",
        "type" : "TraditionalCounty",
      },
      "Galway City and Suburbs" : {
        "prefLabel" : "Galway",
        "type" : "TraditionalCounty",
      },
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
      "broader" : [],
    }
  
  def getEDConceptType(self, code1, code2, name1, name2):
    if name1 and not code1: # then it's a top level area
      if name1 in self.provinces: # then it's a province
        conceptType = "Province"
      elif name1 == "State":
        conceptType = "State"
      else:
        if "City" in name1:
          conceptType = "City"
        else:
          conceptType = "AdministrativeCounty"
    elif code1 and not code2: # then it's normal ED
      conceptType = "ElectoralDivision"
    elif code2: # then it's paired ED
      conceptType = "paired ed"
    elif not name1:
      raise Exception(
        "Parsing error for geographic area {0} {1} {2} {3}.".format(
          code1,
          code2,
          name1,
          name2
        )
      ) 
    return conceptType
  
  def getEAConceptType(self, name, c1_part1, c1_part2, c2):
    if not c1_part2: # then it's a broader area
      if name and not c1_part1 and "Suburbs" in name: # then it's a city + suburbs
        conceptType = "city plus suburbs"
      elif name and not c1_part2 and "Suburbs" in name: # then it's a suburbs
        conceptType = "suburbs"
      elif name in self.cityNames: # then it's a "city"
        conceptType = "City"
      elif name in ["South Dublin", "Fingal", "Dún Laoghaire-Rathdown"]: # then it's an administrative county
        conceptType = "AdministrativeCounty"
    elif c1_part2 and not c2: # then it's a normal EA
      conceptType = "EnumerationArea"
    elif c2: # then it's a paired EA
      conceptType = "paired ea"
    else:
      raise Exception(
        "Geographic area cannot be matched: {0}".format(
          name,
          c1_part1,
          c1_part2,
          c2
        )
      )
    return conceptType
    
  def getEDBroader(self, conceptType, code1, code2, name1, name2):
    if conceptType == "Province":
      broader = {
        "prefLabel" : "Republic of Ireland",
        "type" : "State",
      }
    elif conceptType == "City":
      broader = self.getConcept(
        conceptType,
        name = name1,
        doNotAppend = True
      )
    elif conceptType == "AdministrativeCounty":
      broader = self.toBroader["{0} {1}".format(name1, code1)]
    elif conceptType == "ElectoralDivision":
      pass
    elif conceptType == "paired ed":
      pass
      
  def getEABroader(self, conceptType, name, c1_part1, c1_part2, c2):
    pass
    
  def getConcept(self, conceptType, doNotAppend = False, **kwargs):
    # kwargs.keys() = ["name", "name1", "name2, "code1", "code2", "doNotAppend"]
    ## Template for returned dict
    concept = {
      "codeLists" : [], # An array of codelists on which the concept should be featured on
      "model" : "", # RDF model to which to append to
      "notation" : "", # Notation that can identify the concept in URIs
      "prefLabel" : "", # Preferred label for the concept
      "type" : "", # rdfs:Class which the concept is an instance of or just a label for the type
    }
    if conceptType == "EnumerationArea":
      concept = {
        "codeLists" : [
          self.ns["code-geo"]["census-2006"],
          self.ns["code-geo"]["roi"],
        ],
        "model" : self.models["eas"],
        "notation" : self.stringForUri(
          "{0} ea{1}".format(
            self.clean(
              "-.+$",
              self.buffers["broader"][-1]["notation"]
            ), 
            kwargs["code"]
          )
        ),
        "prefLabel" : "{0} {1}".format(kwargs["name"], kwargs["code"]),
        "type" : conceptType,
      }
      broader = self.buffers["broader"][-1]
      if broader["type"] == "City":
        concept["uri"] = self.ns["geo"][
          self.stringForUri(
            "city/{0}/ea/{1}".format(
              self.clean("-city", broader["notation"]),
              kwargs["code"]
            )
          )
        ]
      elif broader["type"] == "suburbs":
        if broader["type"] in ["paired ea", "suburbs", "city plus suburbs"]:
          broader = self.toBroader[broader["prefLabel"]]
          if broader.has_key("EnumerationArea"):
            broader = broader["EnumerationArea"]
          broader = self.getConcept(
            conceptType = broader["type"],
            name = broader["prefLabel"],
            doNotAppend = True
          )
        concept["uri"] = self.ns["geo"][
          "{0}/{1}/ea/{2}".format(
            self.typeToUri[broader["type"]],
            self.clean("-.+$", broader["notation"]),
            kwargs["code"]
          )
        ]
      elif broader["type"] == "AdministrativeCounty":
        concept["uri"] = self.ns["geo"][
          "county/{0}/ea/{1}".format(
            self.clean("-county", broader["notation"]),
            kwargs["code"]
          )
        ]
      elif broader["type"] == "TraditionalCounty":
        concept["uri"] = self.ns["geo"][
          "traditional-county/{0}/ea/{1}".format(
            self.clean("-.+$", broader["notation"]),
            kwargs["code"]
          )
        ]
      else:
        raise Exception(
          "Unhandled broader concept type: {0}".format(
            broader["type"]
          )
        )
    elif conceptType == "ElectoralDivision":
      concept = {
        "codeLists" : [
          self.ns["code-geo"]["census-2006"],
          self.ns["code-geo"]["roi"],
        ],
        "model" : self.models["eds"],
        "notation" : self.stringForUri(
          "{0} ed{1}".format(self.buffers["broader"][-1]["notation"], kwargs["code"])
        ),
        "prefLabel" : kwargs["name"],
        "type" : conceptType,
        "uri" : self.ns["geo"][
          self.stringForUri(
            "{0}/{1}/ed/{2}".format(
              self.typeToUri[self.buffers["broader"][-1]["type"]],
              self.clean("-city", self.buffers["broader"][-1]["notation"]),
              kwargs["code"]
            )
          )
        ],
      }
    elif conceptType == "AdministrativeCounty":
      countyName = self.clean("county", kwargs["name"])
      concept = {
        "model" : self.models["topLevel"],
        "uri" : self.ns["geo"]["county/{0}".format(self.stringForUri(countyName))],
        "type" : conceptType,
        "prefLabel" : "County {0} (administrative)".format(countyName),
        "notation" : self.stringForUri(countyName),
        "codeLists" : [
          self.ns["code-geo"]["census-2006"],
          self.ns["code-geo"]["top-level"],
          self.ns["code-geo"]["roi"],
        ],
      }
      if self.getTraditionalCounty.has_key(countyName):
        self.buffers["broader"][-1]["uri"] = self.ns["geo"][
          "traditional-county/{0}".format(
            self.stringForUri(self.getTraditionalCounty[countyName])
          )
        ]
    elif conceptType == "City":
      cityName = self.clean("city", kwargs["name"])
      concept = {
        "codeLists" : [
          self.ns["code-geo"]["census-2006"],
          self.ns["code-geo"]["top-level"],
          self.ns["code-geo"]["roi"],
        ],
        "model" : self.models["topLevel"],
        "notation" : self.stringForUri(kwargs["name"]),
        "prefLabel" : kwargs["name"],
        "type" : conceptType,
        "uri" : self.ns["geo"]["city/{0}".format(self.stringForUri(cityName))],
      }
      self.buffers["broader"][-1]["uri"] = self.ns["geo"]["traditional-county/{0}".format(cityName.lower())]
    elif conceptType == "paired ed":
      concept = {
        "codeLists" : [
          self.ns["code-geo"]["census-2006"],
        ],
        "model" : self.models["csoStuff"],
        "notation" : "{0}-ed{1}-{2}".format(self.buffers["broader"][-1]["notation"], kwargs["code1"], kwargs["code2"]),
        "prefLabel" : "{0} {1}, {2} {3}".format(kwargs["name1"], kwargs["code1"], kwargs["name2"], kwargs["code2"]),
        "type" : conceptType,
        "uri" : self.ns["code-geo"]["census-2006/{0}/{1}/ed/{2}-{3}".format(
          self.typeToUri[self.buffers["broader"][-1]["type"]],
          self.buffers["broader"][-1]["notation"],
          kwargs["code1"],
          kwargs["code2"]
        )],
      }
    elif conceptType == "paired ea":
      concept = {
        "codeLists" : [
          self.ns["code-geo"]["census-2006"],
        ],
        "model" : self.models["csoStuff"],
        "notation" : "{0}-ea{1}-{2}".format(self.stringForUri(kwargs["name1"]), kwargs["code1"], kwargs["code2"]),
        "prefLabel" : "{0} {1}, {2}".format(kwargs["name1"], kwargs["code1"], kwargs["code2"]),
        "type" : conceptType,
      }
      broader = self.buffers["broader"][-1]
      if broader["type"] == "City":
        concept["uri"] = self.ns["code-geo"]["census-2006/city/{0}/ea/{1}-{2}".format(
          self.clean("-city", broader["notation"]),
          kwargs["code1"],
          kwargs["code2"]
        )]
      elif broader["type"] == "suburbs":
        concept["uri"] = self.ns["code-geo"]["census-2006/suburbs/{0}/ea/{1}-{2}".format(
          self.clean("-suburbs", broader["notation"]),
          kwargs["code1"],
          kwargs["code2"]
        )]
      elif broader["type"] == "AdministrativeCounty":
        concept["uri"] = self.ns["code-geo"]["census-2006/county/{0}/ea/{1}-{2}".format(
          self.clean("-county", broader["notation"]),
          kwargs["code1"],
          kwargs["code2"]
        )]
      elif broader["type"] == "TraditionalCounty":
        raise SystemExit
        #concept["uri"] = self.ns["code-geo"]["census-2006/"]
      else:
        raise Exception("Not implemented broader type: {0}".format(broader["type"]))
    elif conceptType == "suburbs":
      notation = self.stringForUri(kwargs["name"])
      concept = {
        "codeLists" : [
          self.ns["code-geo"]["census-2006"],
        ],
        "model" : self.models["csoStuff"],
        "notation" : notation,
        "prefLabel" : kwargs["name"],
        "type" : conceptType,
        "uri" : self.ns["code-geo"]["census-2006/suburbs/{0}".format(self.clean("-suburbs", notation))],
      }
    elif conceptType == "city plus suburbs":
      notation = self.stringForUri(kwargs["name"])
      concept = {
        "codeLists" : [
          self.ns["code-geo"]["census-2006"],
        ],
        "model" : self.models["csoStuff"],
        "notation" : notation,
        "prefLabel" : kwargs["name"],
        "type" : conceptType,
        "uri" : self.ns["code-geo"]["census-2006/cities-suburbs/{0}".format(
          self.stringForUri(self.clean("\s*City and Suburbs", kwargs["name"]))
        )],
      }
    elif conceptType == "TraditionalCounty":
      concept = {
        "codeLists" : [
          self.ns["code-geo"]["census-2006"],
          self.ns["code-geo"]["roi"],
          self.ns["code-geo"]["top-level"],
        ],
        "model" : self.models["topLevel"],
        "notation" : "{0}-traditional".format(self.stringForUri(kwargs["name"])),
        "prefLabel" : "County {0} (traditional)".format(kwargs["name"]),
        "type" : conceptType,
        "uri" : self.ns["geo"][
          "traditional-county/{0}".format(
            self.stringForUri(kwargs["name"])
          )
        ],
      }
    elif conceptType == "Province":
      notation = self.stringForUri(kwargs["name"])
      concept = {
        "codeLists" : [
          self.ns["code-geo"]["census-2006"],
          self.ns["code-geo"]["roi"],
          self.ns["code-geo"]["top-level"],
        ],
        "model" : self.models["topLevel"],
        "notation" : notation,
        "prefLabel" : kwargs["name"],
        "type" : conceptType,
        "uri" : self.ns["geo"]["province/{0}".format(notation)],
      }
    elif conceptType == "State":
      concept = {
        "codeLists" : [
          self.ns["code-geo"]["census-2006"],
          self.ns["code-geo"]["roi"],
          self.ns["code-geo"]["top-level"],
        ],
        "model" : self.models["topLevel"],
        "notation" : "roi",
        "prefLabel" : "Republic of Ireland",
        "type" : conceptType,
        "uri" : self.ns["geo"]["roi"],
      }
    else:
      raise ValueError("Wrong conceptType argument: {0}".format(conceptType))
    
    if not doNotAppend:
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
        ]
      )
      for broader in self.buffers["broader"]:
        self.getModelToAppend(concept, broader).appendToSubject(
          concept["uri"],
          [
            [
              self.ns["skos"]["broader"],
              broader["uri"],
            ],
          ]
        ).appendToSubject(
          broader["uri"],
          [
            [
              self.ns["skos"]["narrower"],
              concept["uri"],
            ],
          ]
        )
      if not conceptType in ["paired ed", "paired ea", "suburbs", "city plus suburbs"]:
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
  
  def getModelToAppend(self, concept, broader):
    csoStuff = ["paired ea", "paired ed", "suburbs", "city plus suburbs"]
    if (concept["type"] in csoStuff) or (broader["type"] in csoStuff):
      model = self.models["csoStuff"]
    else:
      model = concept["model"]
    return model
      
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
        
        conceptType = self.getEDConceptType(code1, code2, name1, name2)
        if conceptType == "Province":
          self.buffers["broader"] = []
          self.buffers["broader"].append(self.getConcept(
            conceptType,
            name = name1,
            doNotAppend = True
          ))
        elif conceptType in ["AdministrativeCounty", "City"]:
          self.buffers["broader"].append(self.getConcept(
            conceptType,
            name = name1
          ))
          self.buffers["broader"] = [self.buffers["broader"].pop()]
        elif conceptType == "ElectoralDivision":
          self.getConcept(
            conceptType,
            name = name1,
            code = code1
          )
        elif conceptType == "paired ed":
          self.buffers["broader"].insert(0, self.getConcept(
            conceptType = "paired ed",
            name1 = name1,
            code1 = code1,
            name2 = name2,
            code2 = code2
          ))
          self.getConcept(
            conceptType = "ElectoralDivision",
            name = name1,
            code = code1,
          )
          self.getConcept(
            conceptType = "ElectoralDivision",
            name = name2,
            code = code2,
          )
          self.buffers["broader"] = [self.buffers["broader"].pop()]
        elif conceptType == "State":
          pass # We already have Republic of Ireland in the bootstrap RDF
        else:
          raise Exception("Unknown concept type: {0}".format(conceptType))
    
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
          conceptType = self.getEAConceptType(name, c1_part1, c1_part2, c2)
          if conceptType == "city plus suburbs":
            self.buffers["broader"] = []
            broader = self.toBroader[name]
            self.buffers["broader"].append(
              self.getConcept(
                conceptType = broader["type"],
                name = broader["prefLabel"],
                doNotAppend = True
              )
            )
            self.buffers["broader"].insert(0, self.getConcept(
              conceptType = conceptType,
              name = name
            ))
          elif conceptType == "City":
            self.buffers["broader"].append(
              self.getConcept(
                conceptType = conceptType,
                name =  name
              )
            )
            self.buffers["broader"] = [self.buffers["broader"].pop()]
          elif conceptType == "AdministrativeCounty":
            self.buffers["broader"] = []
            broader = self.toBroader[name]
            if broader.has_key("city plus suburbs"):
              self.buffers["broader"].append(
                self.getConcept(
                  conceptType = broader["city plus suburbs"]["type"],
                  name = broader["city plus suburbs"]["prefLabel"],
                  doNotAppend = True
                )
              )
            self.buffers["broader"].append(
              self.getConcept(
                conceptType = broader["type"],
                name = broader["prefLabel"],
                doNotAppend = True
              )
            )
            self.buffers["broader"].append(
              self.getConcept(
                conceptType = conceptType,
                name = name
              )
            )
            self.buffers["broader"] = [self.buffers["broader"].pop()]
          elif conceptType == "suburbs":
            self.buffers["broader"] = []
            broader = self.toBroader[name]
            if broader.has_key("city plus suburbs"):
              self.buffers["broader"].append(
                self.getConcept(
                  conceptType = broader["city plus suburbs"]["type"],
                  name = broader["city plus suburbs"]["prefLabel"],
                  doNotAppend = True
                )
              )
            if broader.has_key("suburbs"):
              self.buffers["broader"].append(
                self.getConcept(
                  conceptType = broader["suburbs"]["type"],
                  name = broader["suburbs"]["prefLabel"],
                  doNotAppend = True
                )
              )
            else:
              self.buffers["broader"].append(
                self.getConcept(
                  conceptType = broader["type"],
                  name = broader["prefLabel"],
                  doNotAppend = True
                )
              )
            self.buffers["broader"].insert(-1,
              self.getConcept(
                conceptType = conceptType,
                name = name
              )
            )
            if len(self.buffers["broader"]) > 2:
              self.buffers["broader"] = self.buffers["broader"][-2:]
          elif conceptType == "EnumerationArea":
            broader = self.toBroader[name]
            if broader.has_key("EnumerationArea"):
              broader = broader["EnumerationArea"]
              self.buffers["broader"].append(self.getConcept(
                conceptType = broader["type"],
                name = broader["prefLabel"],
                doNotAppend = True
              ))
            self.getConcept(
              conceptType = "EnumerationArea",
              name = name,
              code = c1_part2
            )
          elif conceptType == "paired ea":
            self.buffers["broader"].insert(0, self.getConcept(
              conceptType = "paired ea",
              name1 = name,
              code1 = c1_part2,
              code2 = c2
            ))
            self.getConcept(
              conceptType = "EnumerationArea",
              name = name,
              code = c1_part2
            )
            self.getConcept(
              conceptType = "EnumerationArea",
              name = name,
              code = c2
            )
            self.buffers["broader"] = [self.buffers["broader"].pop()]
          else:
            raise Exception("Unknown concept type: {0}".format(conceptType))
        else:
          raise Exception("Geographic area does not match: {0}".format(geoArea))
          
  def main(self):
    self.addEAs()
    self.addEDs()
    
    self._fileEAs.close()
    self._fileEDs.close()
  
  def write(self, name):
    for model in self.models.keys():
      self.models[model].write(
        "{0}-{1}.ttl".format(
          name,
          model
        )
      )


if __name__ == "__main__":
  writer = GeoAreasWriter(
    fileEDs = ED_FILE,
    fileEAs = EA_FILE
  )
  writer.main()
  writer.write(
    OUTPUT_FILE
  )

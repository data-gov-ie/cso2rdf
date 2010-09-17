#!/usr/bin/env python
#-*- coding:utf-8 -*-

# TODO:
# For computing aggregates, the MemoryStorage is not enough due to the volume of data.
# Stack trace:
#librdf error - digest SHA1 already registered
#librdf error - hash bdb already registered
#librdf error - hash memory already registered
#librdf error - model storage already registered
#librdf error - storage hashes already registered
#librdf error - storage trees already registered
#librdf error - storage memory already registered
#librdf error - storage file already registered
#librdf error - storage uri already registered
#librdf error - query language triples already registered
#librdf error - query language laqrs already registered
#librdf error - query language rdql already registered
#librdf error - query language sparql already registered
#Traceback (most recent call last):
#  File "./convert-religion.py", line 582, in <module>
#    cr.main()
#  File "./convert-religion.py", line 574, in main
#    self.computeAggregates()
#  File "./convert-religion.py", line 554, in computeAggregates
#    for populationPart in self.sparql(query):
#  File "/usr/lib/python2.6/dist-packages/RDF.py", line 2020, in next
#    Redland.librdf_query_results_next(self._results)
#RDF.RedlandError: 'digest MD5 already registered'

import csv, os, RDF, re, sys
sys.path.append(os.path.join("..", "..", "RDFModel"))
from RDFModel import RDFModel

# Definition of the paths
DSD = os.path.join("..", "..", "DSDs", "persons-by-religion.ttl")
ED_FILE = os.path.join("..", "Datasources", "ed", "religion.csv")
EA_FILE = os.path.join("..", "Datasources", "ea", "religion.csv")
TOP_LEVEL_GEO = os.path.join("..", "..", "Codelists", "geo-topLevel.ttl")


class ConvertReligion (RDFModel):
  """
    Class for converting CSO datasets about religion
  """
  
  def __init__(self, DSD, title):
    self.datasetID = re.search("(.+)(?=\.\D+)", os.path.basename(DSD)).group()
    self.title = title
    namespaces = {
      "qb" : "http://purl.org/linked-data/cube#",
      "sdmx" : "http://purl.org/linked-data/sdmx#",
      "sdmx-dimension" : "http://purl.org/linked-data/sdmx/2009/dimension#",
      "sdmx-metadata" : "http://purl.org/linked-data/sdmx/2009/metadata#",
      "skos" : "http://www.w3.org/2004/02/skos/core#",
      "year" : "http://reference.data.gov.uk/id/year/",
      # own namespaces
      "code" : "http://stats.govdata.ie/codelist/",
      "code-geo" : "http://stats.govdata.ie/codelist/geo/",
      "data" : "http://stats.govdata.ie/data/",
      "dsd" : "http://stats.govdata.ie/dsd/",
      "geo" : "http://geo.govdata.ie/",
      "prop" : "http://stats.govdata.ie/property/",
      "code-religion" : "http://stats.govdata.ie/codelist/religion/",
    }
    RDFModel.__init__(self, namespaces)
    self.DSD = RDFModel(namespaces).bootstrap(DSD)
    
    self._fileEDs = open(ED_FILE, "r")
    self.fileEDs = csv.reader(self._fileEDs, delimiter=";")
    self._fileEAs = open(EA_FILE, "r")
    self.fileEAs = csv.reader(self._fileEAs, delimiter=";")
    
    self.regexp = {
      "EAs" : re.compile(
        "^(?P<name>[\D\s]+)(?=\s|$)\s?(?P<c1_part1>\d{2})?\/?(?P<c1_part2>\d{3})?(?:,\s?\d{2}\/)?(?P<c2>\d{3})?$"
      ),
      "EDs" : re.compile(
        "^(?P<code1>\d{3})?(?:\/)?(?P<code2>\d{3})?\s?(?P<name1>[^\/]+)(?:\/)?(?P<name2>[^\/]+)?$"
      )
    }
    self.provinces = ["Connacht", "Leinster", "Munster", "Ulster"]
    self.cityNames = [
      "Dublin City",
      "Cork City",
      "Galway City",
      "Limerick City",
      "Waterford City"
    ]
    self.typeToUri = {
      "AdministrativeCounty" : "county",
      "TraditionalCounty" : "traditional-county",
      "City" : "city",
    }
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
        geo["uri"] = self.ns["code-geo"][
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
      else:
        raise Exception("Wrong broader type: {0}".format(self.buffers["broader"]["type"]))

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
        "type" : conceptType,
        "uri" : self.ns["geo"]["county/{0}".format(self.stringForUri(countyName))],
      }
      self.buffers["broader"] = geo
      
    ## City
    elif conceptType == "City":
      cityName = self.clean("city", kwargs["name"])
      geo = {
        "notation" : self.stringForUri(kwargs["name"]),
        "type" : conceptType,
        "uri" : self.ns["geo"]["city/{0}".format(self.stringForUri(cityName))],
      }
      self.buffers["broader"] = geo
      
    ## Province
    elif conceptType == "Province":
      geo = {
        "notation" : self.stringForUri(kwargs["name"]),
        "type" : conceptType,
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
        "type" : conceptType,
      }
      if self.buffers["broader"]["type"] == "City":
        geo["uri"] = self.ns["code"]["census-2006/city/{0}/ea/{1}-{2}".format(
          self.clean("-city", self.buffers["broader"]["notation"]),
          kwargs["code1"],
          kwargs["code2"]
        )]
      elif self.buffers["broader"]["type"] == "suburbs":
        geo["uri"] = self.ns["code"]["census-2006/suburbs/{0}/ea/{1}-{2}".format(
          self.clean("-suburbs", self.buffers["broader"]["notation"]),
          kwargs["code1"],
          kwargs["code2"]
        )]
      elif self.buffers["broader"]["type"] == "AdministrativeCounty":
        geo["uri"] = self.ns["code"]["census-2006/county/{0}/ea/{1}-{2}".format(
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
        "type" : conceptType,
        "uri" : self.ns["code"]["census-2006/{0}/{1}/ed/{2}-{3}".format(
          self.typeToUri[self.buffers["broader"]["type"]],
          self.buffers["broader"]["notation"],
          kwargs["code1"],
          kwargs["code2"]
        )],
      }
    
    elif conceptType == "suburbs":
      geo["notation"] = self.stringForUri(kwargs["name"])
      geo["type"] = conceptType
      geo["uri"] = self.ns["code"]["census-2006/suburbs/{0}".format(
        self.clean("-suburbs", geo["notation"]))
      ]
      self.buffers["broader"] = geo
    
    elif conceptType == "State":
      geo = {
        "notation" : "roi",
        "type" : conceptType,
        "uri" : self.ns["geo"]["roi"],
      }
      self.buffers["broader"] = geo
      
    elif conceptType == "city plus suburbs":
      geo["notation"] = self.stringForUri(kwargs["name"])
      geo["type"] = conceptType
      geo["uri"] = self.ns["code"]["census-2006/cities-suburbs/{0}".format(geo["notation"])]
      
    return geo
  
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
    print "Adding observation: <{0}>".format(observationUri.uri)
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
          dimensions[1]["uri"],
        ],
        [
          self.ns["prop"]["religion"],
          dimensions[2]["uri"],
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
        
        conceptType = self.getEDConceptType(code1, code2, name1, name2)
        if conceptType == "State":
          geo = self.getGeo(conceptType)
        elif conceptType == "Province":
          geo = self.getGeo(conceptType, name = name1)
        elif conceptType == "City":
          geo = self.getGeo(conceptType, name = name1)
        elif conceptType == "AdministrativeCounty":
          geo = self.getGeo(conceptType, name = name1)
        elif conceptType == "ElectoralDivision":
          geo = self.getGeo(conceptType, name = name1, code = code1)
        elif conceptType == "paired ed":
          geo = self.getGeo(conceptType, name = name1, code1 = code1, code2 = code2)

        dimensions.append(geo)
        
        for key, obsValue in enumerate(line[1:]):
          self.appendObservation(dimensions + [self.religionIndexToConcept[key]], obsValue)
            
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
          
          conceptType = self.getEAConceptType(name, c1_part1, c1_part2, c2)
          if conceptType == "city plus suburbs":
            geo = self.getGeo(conceptType, name = name)
          elif conceptType == "suburbs":
            geo = self.getGeo(conceptType, name = name)
          elif conceptType == "City":
            geo = self.getGeo(conceptType, name = name)
          elif conceptType == "AdministrativeCounty":
            geo = self.getGeo(conceptType, name = name)
          elif conceptType == "EnumerationArea":
            geo = self.getGeo(conceptType, code = c1_part2)
          elif conceptType == "paired ea":
            geo = self.getGeo(conceptType, name1 = name, code1 = c1_part2, code2 = c2)
          
          dimensions.append(geo)
          
          for key, obsValue in enumerate(line[1:]):
            self.appendObservation(dimensions + [self.religionIndexToConcept[key]], obsValue)
        else:
          print geoArea
          raise SystemExit
  
  def initiateDataset(self):
    self.appendToSubject(
      self.ns["data"][self.datasetID],
      [
        [
          self.ns["rdf"]["type"],
          self.ns["qb"]["DataSet"],
        ],
        [
          self.ns["qb"]["structure"],
          self.ns["dsd"][self.datasetID],
        ],
        [
          self.ns["sdmx-metadata"]["title"],
          RDF.Node(
            literal = self.title,
            language = "en"
          )
        ],
      ]
    )
  
  def computeAggregates(self):
    print "[INFO] Computing aggregates"
    m = RDFModel()
    m.bootstrap(TOP_LEVEL_GEO)
    
    print "[INFO] Getting hierarchy data"
    query = """PREFIX geo: <http://geo.govdata.ie/>
      PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

      SELECT ?trad ?notation ?match WHERE {
        ?trad a geo:TraditionalCounty .
        ?match a geo:AdministrativeCounty .
        ?trad skos:exactMatch ?match .
        ?trad skos:notation ?notation .
      }
    """

    output = {}
    for result in m.sparql(query):
      result["trad"] = str(result["trad"].uri)
      output[result["trad"]] = {
        "exactMatch" : str(result["match"].uri),
        "notation" : str(result["notation"]),
      }
      print "[INFO] Got exact match between {0} and {1}".format(
        result["trad"],
        output[result["trad"]]["exactMatch"]
      )

    query = """PREFIX geo: <http://geo.govdata.ie/>
      PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

      SELECT ?trad ?notation ?narrower WHERE {
        ?trad a geo:TraditionalCounty .
        ?trad skos:narrower ?narrower .
        ?trad skos:notation ?notation .
      }
    """
    narrowers = {}
    for result in m.sparql(query):
      result["trad"] = str(result["trad"].uri)
      if not narrowers.has_key(result["trad"]):
        narrowers[result["trad"]] = {
          "notation" : str(result["notation"]),
        }
      result["narrower"] = str(result["narrower"].uri)
      if not narrowers[result["trad"]].has_key("narrower"):
        narrowers[result["trad"]]["narrower"] = [result["narrower"]]
      else:
        narrowers[result["trad"]]["narrower"].append(result["narrower"])
      print "[INFO] Got narrower match between {0} and {1}".format(
        result["trad"],
        result["narrower"],
      )
          
    output.update(narrowers)
    
    print "[INFO] Getting values to aggregate"
    for traditionalCounty in output:
      print "[INFO] Computing aggregates for traditional county {0}".format(
        traditionalCounty
      )
      if output[traditionalCounty].has_key("exactMatch"):
        administrativeCounty = output[traditionalCounty]["exactMatch"]
        print "[INFO] Getting data for the exact match <{0}>".format(
          administrativeCounty
        )
        query = """PREFIX prop: <http://stats.govdata.ie/property/>
          PREFIX sdmx: <http://purl.org/linked-data/sdmx#>

          SELECT ?observation WHERE {{
           ?observation a sdmx:Observation .
           ?observation prop:geoArea <{0}> .
          }}
        """.format(administrativeCounty)
        print "[INFO] Issuing SPARQL query: {0}".format(
          query
        )
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
          print "[INFO] Getting data for the observation <{0}>".format(
            observation
          )
          query = """PREFIX prop: <http://stats.govdata.ie/property/>
            SELECT ?religion ?population WHERE {{
            <{0}> prop:religion ?religion .
            <{0}> prop:population ?population .
          }}""".format(observation)
          for statement in self.sparql(query):
            religion = str(statement["religion"].uri)
            population = str(statement["population"].literal_value["string"])
            print "[INFO] Got religion {0} and population {1}".format(
              religion,
              population
            )
            dimensions.append({
              "notation" : re.search("(?<=\/)([^\/]+)$", religion).group(),
              "uri" : religion,
            })
          self.appendObservation(dimensions, population)
          
      elif output[traditionalCounty].has_key("narrower") and False: # just to make sure computing works for exact matches
        print "[INFO] Getting data for narrower"
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
        print "[INFO] The narrowers are {0}".format(", ".join(["<{0}>".format(narrower) for narrower in narrowers]))
        for religion in self.religionIndexToConcept:
          religion = religion["uri"].uri
          print "[INFO] Starting with religion {0}".format(religion)
          religionStr = str(religion)
          query = """PREFIX prop: <http://stats.govdata.ie/property/>
            PREFIX sdmx: <http://purl.org/linked-data/sdmx#>

            SELECT ?population WHERE {{
              ?observation a sdmx:Observation .
              ?observation prop:geoArea ?geo .
              ?observation prop:religion <{0}> .
              ?observation prop:population ?population .
              FILTER ({1})
            }}""".format(
              religionStr,
              " || ".join(
                ["?geo = <{0}>".format(narrower) for narrower in narrowers]
              )
            )
          print "[INFO] SPARQL query: {0}".format(query)
          populationTotal = 0
          for populationPart in self.sparql(query):
            print "[INFO] Got population count {0}".format(
              populationPart["population"]
            )
            populationTotal += int(
              populationPart["population"].literal_value["string"]
            )
          self.appendObservation(
            dimensions + [
              {
                "notation" : re.search("(?<=\/)([^\/]+)$", religionStr).group(),
                "uri" : religion,
              },
            ], 
            populationTotal
          )
      
  def main(self):
    self.initiateDataset()
    self.addFromEAs()
    self.addFromEDs()
    self._fileEAs.close()
    self._fileEDs.close()
    self.computeAggregates()
        
  def write(self):
    RDFModel.write(self, os.path.join("..", "Datasets", "{0}.ttl".format(self.datasetID)))


if __name__ == "__main__":
  cr = ConvertReligion(DSD = DSD, title = "Number of persons by religion, 2006")
  cr.main()
  cr.write()

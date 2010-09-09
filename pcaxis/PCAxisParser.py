#!/usr/bin/env python
#-*- coding:utf-8 -*-

import datetime, decimal, json, os, re, string, sys, unittest
from pyparsing import alphanums, alphas, Combine, delimitedList, FollowedBy, Group, LineEnd, Literal, nums, OneOrMore, Optional, ParseException, QuotedString, Regex, Suppress, White, Word


class PCAxisParserTestCase (unittest.TestCase):
  """
    Unit tests for PCAxisParser grammar
  """
  
  def setUp(self):
    self.testInst = PCAxisParser()
    self.testInst.buffers["validLanguageCodes"].append("sv")
    
  def assertParses(self, grammarElement, parseString):
    try:
      self.testInst.grammar[grammarElement].parseString(parseString)
      pass
    except ParseException as err:
      self.fail("Error parsing: {0} \nError: {1}".format(grammarElement, err))
    
  def test_EOL(self):
    self.assertParses("EOL", "\n")
      
  def test_number(self):
    self.assertParses("number", "5")
    
  def test_quotedString(self):
    self.assertParses("quotedString", "'string'")
    
  def test_quote(self):
    self.assertParses("quote", "'")
    
  def test_dots(self):
    self.assertParses("dots", "......")
  
  def test_quotedDots(self):
    self.assertParses("quotedDots", "'...'")
  
  def test_dataNumber(self):
    self.assertParses("dataNumber", "5.5")
    
  def test_baseKeyword(self):
    self.assertParses("baseKeyword", "CREATION-DATE")
    
  def test_tableSpecificKeyword(self):
    self.assertParses("tableSpecificKeyword", """CREATION-DATE=""")
    
  def test_variableSpecificKeyword1(self):
    self.assertParses("variableSpecificKeyword",
      """VALUES("Principal Economic Status")=""")
    
  def test_variableSpecificKeyword2(self):
    self.assertParses("variableSpecificKeyword",
      """UNITS("Average Maximum Temperature (Degrees C)")=""")
    
  def test_valueSpecificKeyword(self):
    self.assertParses("valueSpecificKeyword",
      """VALUES("Principal Economic Status","High")=""")
    
  def test_languageSpecificKeyword(self):
    self.assertParses("languageSpecificKeyword", """CONTENTS[sv]=""")
    
  def test_keywordValue1(self):
    self.assertParses("keywordValue", """"320";""")
    
  def test_keywordValue2(self):
    self.assertParses("keywordValue", """"320","300";""")
    
  def test_keywordValue3(self):
    self.assertParses("keywordValue",
      """"Multi" \n"line";""")
  
  def test_keywordValues(self):
    self.assertParses("keywordValues",
      """"320","Multi"\n"line","365","415",\n"465","500","535","575";""")
    
  def test_timeFormat(self):
    self.assertParses("timeFormat", "Q1")
  
  def test_timeValues(self):
    self.assertParses("timeValues", '"1994", "1995", "1996"')
  
  def test_timeSpan(self):
    self.assertParses("timeSpan", '"1994"-"1996"')
  
  def test_TLIST1(self):
    self.assertParses("TLIST", """TLIST(A1), "1994", "1995", "1996";""")
    
  def test_TLIST2(self):
    self.assertParses("TLIST", """TLIST(A1, "1994"-"1996");""")
    
  def test_keywordLine(self):
    self.assertParses("keywordLine", 
      """VALUES("Principal Economic Status","High")="320","Multi"\n"line","365","415",\n"465","500","535","575";""")
  
  def test_observation1(self):
    self.assertParses("observation", "'..'")
  
  def test_observation2(self):
    self.assertParses("observation", "5.5")
    
  def test_observation3(self):
    self.assertParses("observation", "-5.5")
    
  def test_observationSeparator(self):
    self.assertParses("observationSeparator", "\t")
    
  def test_observationLine1(self):
    self.assertParses("observationLine",
      """".." ".." ".." 14473 14052 14369 """)
    
  def test_observationLine2(self):
    self.assertParses("observationLine",
      """8.20 3.50 5.90 12.80 -4.80 8.80 4.10 6.50 """)
    
  def test_observationLines(self):
    self.assertParses("observationLines",
      """".." ".." ".." 100 33 90 \n12 3 6 0 7 64 \n276127 286424 266572 293354 328334 342475 """)
    
  def test_data(self):
    self.assertParses("data",
      """DATA=\n2399676 2515942 2585145 2766663 3089775 3375399 \n931948 988280 1012871 1137858 1314664 1453227 \n1288100 1341340 1384571 1356613 1454413 1565016 \n".." ".." ".." 87792 133838 166797;""")
      
  def test_parseDate(self):
    dateString = "20100531 13:00"
    dateDict = {
      "year" : "2010",
      "month" : "05",
      "day" : "31",
      "hours" : "13",
      "minutes" : "00",
    }
    self.assertEqual(self.testInst.parseDate(dateString),
      dateDict, msg="Parsing date failed.")
  
  def test_parseContact(self):
    contactString = "Census Enquiries, CSO\nTel: 1 8951460\nFax: 1 8951399\nE-mail: census@cso.ie"
    contactDict = {
      "name" : "Census Enquiries, CSO",
      "phone" : "1 8951460",
      "fax" : "1 8951399",
      "email" : "census@cso.ie",
    }
    self.assertEqual(self.testInst.parseContact(contactString),
      contactDict, msg="Parsing contact failed.")
      
  def test_convertToNumber1(self):
    numberString = ["-5"]
    expectedResult = -5
    self.assertEqual(self.testInst.convertToNumber(numberString), expectedResult, msg="Failed converting to number.")
        
  def test_convertToNumber2(self):
    numberString = ["-5.5"]
    expectedResult = "-5.5"
    self.assertEqual(self.testInst.convertToNumber(numberString), expectedResult, msg="Failed converting to number.")
    
  def test_convertTimeListValueYearFormat(self):
    result = self.testInst.convertTimeList(["A1", ["1995"]])
    print result
    expectedResult = [{
      "year" : "1995",
      "frequency" : "year",
      "number" : "",
    }]
    self.assertEqual(result, expectedResult, msg="Failed converting time period - year format.")
    
  def test_convertTimeListValueHalfyearFormat(self):
    result = self.testInst.convertTimeList(["H1", ["19952"]])
    expectedResult = [{
      "frequency" : "half",
      "year" : "1995",
      "number" : "2",
    }]
    self.assertEqual(result, expectedResult, msg="Failed converting time period - half-year format.")
    
  def test_convertTimeListValueQuarterFormat(self):
    result = self.testInst.convertTimeList(["Q1", ["19954"]])
    expectedResult = [{
      "frequency" : "quarter",
      "year" : "1995",
      "number" : "4",
    }]
    self.assertEqual(result, expectedResult, msg="Failed converting time period - quarter format.")
    
  def test_convertTimeListMonthFormat(self):
    result = self.testInst.convertTimeList(["M1", ["199512"]])
    expectedResult = [{
      "frequency" : "month",
      "year" : "1995",
      "number" : "12",
    }]
    self.assertEqual(result, expectedResult, msg="Failed converting time period - month format.")
    
  def test_convertTimeListWeekFormat(self):
    result = self.testInst.convertTimeList(["W1", ["201008"]])
    expectedResult = [{
      "frequency" : "week",
      "year" : "2010",
      "number" : "08",
    }]
    self.assertEqual(result, expectedResult, msg="Failed converting time period - week format. Got result: {0}".format(result))
    
  def tearDown(self):
    self.testInst = None


class PCAxisParser (object):
  """
    Parser for PC-Axis files
  """
  
  def __init__(self):
    self.filename = ""
    self.basedir = ""
    
    #############
    # Constants #
    #############
    self.possibleKeywords = [
      "AGGREGALLOWED", "AUTOPEN", "AXIS-VERSION", "BASEPERIOD", 
      "CELLNOTE", "CELLNOTEX", "CFPRICES", "CHARSET", 
      "CODEPAGE", "CODES", "CONFIDENTIAL", "CONTACT", 
      "CONTENTS", "CONTVARIABLE", "COPYRIGHT", "CREATION-DATE", 
      "DATA", "DATABASE", "DATANOTECELL", "DATANOTESUM", 
      "DATASYMBOL1", "DATASYMBOL2", "DATASYMBOL3", 
      "DATASYMBOL4", "DATASYMBOL5", "DATASYMBOL6", "DATASYMBOLNIL",
      "DATASYMBOLSUM", "DAYADJ", "DECIMAL", "DEFAULT-GRAPH",
      "DESCRIPTION", "DESCRIPTIONDEFAULT", "DIRECTORY-PATH",
      "DOMAIN", "DOUBLECOLUMN", "ELIMINATION", "HEADING",
      "HIERARCHIES", "HIERARCHYLEVELS", "HIERARCHYLEVELSOPEN",
      "HIERARCHYNAMES", "INFO", "INFOFILE", "KEYS", 
      "LANGUAGE", "LANGUAGES", "LAST-UPDATED", "LINK", 
      "MAP", "MATRIX", "NEXT-UPDATE", "NOTE", "NOTEX", 
      "PARTITIONED", "PRECISION", "PRESTEXT", "PX-SERVER", 
      "REFPERIOD", "ROUNDING", "SEASADJ", "SHOWDECIMALS", 
      "SOURCE", "STOCKFA", "STUB", "SUBJECT-AREA", "SUBJECT-CODE",
      "SURVEY", "SYNONYMS", "TABLEID", "TIMEVAL", "TITLE", 
      "UNITS", "UPDATE-FREQUENCY", "VALUENOTE", "VALUENOTEX",
      "VALUES", "VARIABLE-TYPE"
    ]
    self.mandatoryKeywords = [
      "CONTENTS", "DATA", "DECIMAL", "HEADING", 
      "MATRIX", "STUB", "SUBJECT-AREA", "SUBJECT-CODE", 
      "TITLE", "UNITS", "VALUES"
    ]
    self.languageAllowedKeywords = [
      "BASEPERIOD", "CELLNOTE", "CELLNOTEX", "CFPRICES",
      "CODES", "CONTACT", "CONTENTS", "CONTVARIABLE",
      "DATABASE", "DATANOTECELL", "DATANOTESUM", "DATASYMBOL1",
      "DATASYMBOL2", "DATASYMBOL3", "DATASYMBOL4", "DATASYMBOL5",
      "DATASYMBOL6", "DATASYMBOLNIL", "DATASYMBOLSUM", "DAYADJ",
      "DESCRIPTION", "DOMAIN", "DOUBLECOLUMN", "ELIMINATION",
      "HEADING", "HIERARCHIES", "HIERARCHYLEVELS", "HIERARCHYLEVELSOPEN",
      "HIERARCHYNAMES", "INFO", "INFOFILE", "KEYS",
      "LAST-UPDATED", "LINK", "MAP", "NOTE",
      "NOTEX", "PARTITIONED", "PRECISION", "PRESTEXT",
      "REFPERIOD", "SEASADJ", "SOURCE", "STOCKFA",
      "STUB", "SUBJECT-AREA", "SURVEY", "TIMEVAL",
      "TITLE", "UNITS", "VALUENOTE", "VALUENOTEX",
      "VALUES", "VARIABLE-TYPE"
    ]

    ###########
    # Buffers #
    ###########
    self.buffers = {
      "foundKeywords" : [],
      "currentKeyword" : "",
      "validLanguageCodes" : [],
      "languageCode" : "",
      "timeFormat" : "",
      "rounding" : "",
      "results" : {},
    }
    
    ###########
    # Grammar #
    ###########
    # Utilities
    self.grammar = {}
    self.grammar["EOL"] = LineEnd().suppress()
    self.grammar["quote"] = Suppress(Regex("\"|\'"))
    self.grammar["number"] = Word(nums).setParseAction(self.convertToNumber)
    self.grammar["quotedString"] = (QuotedString('"') | QuotedString("'"))\
      .setParseAction(lambda tokens: tokens[0].replace("#", "\n"))
    self.grammar["quotedNumber"] = self.grammar["quote"] + self.grammar["number"] + self.grammar["quote"]
    self.grammar["lparen"], self.grammar["rparen"], self.grammar["lbracket"], self.grammar["rbracket"] = map(Suppress, "()[]")
    self.grammar["dots"] = Regex("\.{1,6}")
    self.grammar["quotedDots"] = self.grammar["quote"] + self.grammar["dots"] + self.grammar["quote"]
    self.grammar["dataNumber"] = Combine(Optional("-") + Word(nums) +\
      Optional(Literal(".") + Word(nums))).setParseAction(self.convertToNumber)

    # Keywords
    self.grammar["baseKeyword"] = Word(alphanums.upper() + "-")\
      .setParseAction(self.handleKeyword)("keyword")
    self.grammar["tableSpecificKeyword"] = self.grammar["baseKeyword"] + FollowedBy("=")
    self.grammar["variableSpecificKeyword"] = self.grammar["baseKeyword"] +\
      self.grammar["lparen"] +\
      self.grammar["quotedString"]("variable") +\
      self.grammar["rparen"]  + FollowedBy("=")
    self.grammar["valueSpecificKeyword"] = self.grammar["baseKeyword"] +\
      self.grammar["lparen"] + Group(self.grammar["quotedString"]("variable") + Suppress(",") +\
      self.grammar["quotedString"]("value")) + self.grammar["rparen"]  + FollowedBy("=")
    self.grammar["languageSpecificKeyword"] = (self.grammar["baseKeyword"] +\
      self.grammar["lbracket"] + Word(alphas).setParseAction(self.isValidLanguageCode)("language") +\
      self.grammar["rbracket"] + FollowedBy("=")).setParseAction(self.isLanguageAllowedKeyword)
    self.grammar["keyword"] = self.grammar["tableSpecificKeyword"] |\
      self.grammar["variableSpecificKeyword"] |\
      self.grammar["valueSpecificKeyword"] |\
      self.grammar["languageSpecificKeyword"]

    # Keyword values
    self.grammar["keywordValue"] = OneOrMore(self.grammar["quotedString"])\
      .setParseAction(lambda tokens: " ".join(tokens))
    self.grammar["keywordValues"] = Group(delimitedList((self.grammar["number"] |\
      self.grammar["keywordValue"])\
      .setParseAction(self.handleKeywordValue)("keywordValue")))("keywordValues") +\
      FollowedBy(";")

    # Time list values
    self.grammar["timeFormat"] = Regex("[AHQMW]1").setParseAction(self.setTimeFormat)("timeFormat")
    self.grammar["timeValues"] = Group(delimitedList(self.grammar["quotedNumber"])("timeValue"))
    self.grammar["timeSpan"] = Group(delimitedList(self.grammar["quotedNumber"]("timeValue"), delim="-"))
    self.grammar["TLIST"] = Literal("TLIST") + self.grammar["lparen"] +\
      (self.grammar["timeFormat"] + ((self.grammar["rparen"] + Suppress(",") +\
      self.grammar["timeValues"])|(Suppress(",") + self.grammar["timeSpan"] +\
      self.grammar["rparen"]))).setParseAction(self.convertTimeList) + FollowedBy(";")

    self.grammar["keywordLine"] = Group(self.grammar["keyword"] + Suppress("=") +\
      (self.grammar["keywordValues"] | self.grammar["TLIST"]) +\
      Suppress(";"))

    # Data values
    self.grammar["observation"] = (self.grammar["quotedDots"] | self.grammar["dataNumber"])
    self.grammar["observationSeparator"] = White(" \t").suppress()
    self.grammar["observationLine"] = Group(delimitedList(self.grammar["observation"],\
      delim=self.grammar["observationSeparator"]).leaveWhitespace())
    self.grammar["observationLines"] = OneOrMore(self.grammar["observationLine"] +\
      Optional(Suppress(";")))("keywordValues")
    self.grammar["data"] = Group(Literal("DATA")("keyword") + Suppress("=") +\
      Optional(OneOrMore(self.grammar["EOL"])) + self.grammar["observationLines"])
    
    # Whole file
    self.grammar["pcaxisFile"] = OneOrMore(self.grammar["keywordLine"]) +\
      OneOrMore(self.grammar["EOL"]) + self.grammar["data"]

  #################
  # Parse actions #
  #################
  def isValidKeyword(self, tokens):
    keyword = tokens[0]
    if keyword in self.possibleKeywords:
      return keyword
    else:
      raise ParseException("Invalid keyword")

  def handleKeyword(self, tokens):
    keyword = tokens[0]
    self.buffers["currentKeyword"] = keyword
    self.buffers["foundKeywords"].append(keyword)
      
  def parseDate(self, dateString):
    dateGrammar = Regex("\d{4}")("year") + Regex("\d{2}")("month") +\
      Regex("\d{2}")("day") + Regex("\d{2}")("hours") +\
      Suppress(":") + Regex("\d{2}")("minutes")
    results = dateGrammar.parseString(dateString)
    return {
      "year" : results["year"],
      "month" : results["month"],
      "day" : results["day"],
      "hours" : results["hours"],
      "minutes" : results["minutes"],
    }
  
  def parseContact(self, contactString):
    try:
      results = {}
      lines = contactString.split("\n")
      results["name"] = lines[0]
      results["phone"] = lines[1].split(":")[-1].strip()
      results["fax"] = lines[2].split(":")[-1].strip()
      results["email"] = lines[3].split(":")[-1].strip()
      return results
    except:
      return contactString
  
  def convertTimeList(self, tokens):
    output = []
    timeFormatValue = {
      "A1" : "year",
      "H1" : "half",
      "Q1" : "quarter",
      "M1" : "month",
      "W1" : "week",
    }
    try:
      timeFormat = timeFormatValue[tokens[0]]
    except KeyError:
      raise ParseException("{0} is not a valid time code.".format(tokens[0]))
      
    for timeValue in tokens[1]:
      timeValue = str(timeValue)
      period = {
        "frequency" : timeFormat,
        "year" : "",
        "number" : "",
      }
      if timeFormat == "year":
        period["year"] = timeValue
      elif timeFormat == "half":
        halfyearDate = re.match("(\d{4})([1-2])", timeValue)
        period["year"] = halfyearDate.group(1)
        period["number"] = halfyearDate.group(2)
      elif timeFormat == "quarter":
        quarterDate = re.match("(\d{4})([1-4])", timeValue)
        period["year"] = quarterDate.group(1)
        period["number"] = quarterDate.group(2)
      elif timeFormat == "month":
        monthDate = re.match("(\d{4})(\d{2})", timeValue)
        period["year"] = monthDate.group(1)
        period["number"] = monthDate.group(2)
      elif timeFormat == "week":
        weekDate = re.match("(\d{4})(\d{2})", timeValue)
        period["year"] = weekDate.group(1)
        period["number"] = weekDate.group(2)
      output.append(period)
      
    return output
        
  def handleKeywordValue(self, tokens):
    keywordValue = tokens[0]
    ck = self.buffers["currentKeyword"]
    if ck == "ROUNDING":
      self.buffers["rounding"] = int(keywordValue)
    elif ck == "DECIMAL":
      self.setDecimalPrecision(int(keywordValue))
    elif ck in ["LAST-UPDATED", "CREATION-DATE"]:
      return self.parseDate(keywordValue)
    elif ck == "CONTACT":
      return self.parseContact(keywordValue)
      
  def isValidLanguageCode(self, tokens):
    self.buffers["languageCode"] = tokens[0]
    if self.buffers["languageCode"] in self.buffers["validLanguageCodes"]:
      return self.buffers["languageCode"]
    else:
      raise ParseException("%s is not valid language code." % (self.buffers["languageCode"]))
    
  def isLanguageAllowedKeyword(self, tokens):
    keyword = tokens[0]
    if keyword in self.languageAllowedKeywords:
      return keyword
    else:
      raise ParseException("%s is not language allowed keyword." % (keyword))

  def hasMandatoryKeywords(self):
    for mandatoryKeyword in self.mandatoryKeywords:
      if not mandatoryKeyword in self.buffers["foundKeywords"]:
        raise ParseException("File is missing required keyword: %s" % (mandatoryKeyword))
        
  def convertToNumber(self, tokens):
    number = tokens[0]
    if "." in number:
      number = +decimal.Decimal(number).normalize() # unary + operator forces rounding
      return number.__str__() # __str__() is necessary for the serialization
    else:
      return int(number)

  def setTimeFormat(self, tokens):
    self.buffers["timeFormat"] = tokens[0]
    
  def setDecimalPrecision(self, precision):
    if self.buffers["rounding"] == 0:
      rounding = decimal.ROUND_HALF_EVEN
    if self.buffers["rounding"] == 1:
      rounding = decimal.ROUND_HALF_UP
    else:
      raise ValueError("Rounding must be either 0 or 1.")
    context = decimal.Context(prec=precision, rounding=rounding)
    decimal.setcontext(context)

  ###########
  # Methods #
  ###########
  def parse(self, fileStream):
    try:
      ptree = self.grammar["pcaxisFile"].parseFile(fileStream)
    except ParseException as err:
      print("Parse error: {0}".format(err))
      raise SystemExit
    return ptree
      
  def parseFiles(self, path):
    if os.path.isdir(path):
      self.basedir = path
      for file in os.listdir(path):
        file = os.path.join(self.basedir, file)
        self.parseFiles(file)
    elif os.path.isfile(path):
      match = re.match("^(.*)\.(.*)$", path)
      self.filename = match.group(1)
      suffix = match.group(2)
      if suffix == "px":
        fileStream = open(path, "r")
        self.convertToJSON(self.parse(fileStream))
    else:
      raise IOError("File path wasn't specified correctly.")
    
  def convertToJSON(self, parseTree):
    if parseTree:
      file = open(self.filename + ".json", "w")
      file.write(json.dumps(parseTree.asList(), indent=2, sort_keys=True))
      file.close()
      
if __name__ == "__main__":
  if len(sys.argv) > 1:
    param = sys.argv[1]
    if param == "--debug":
      suite = unittest.TestLoader().loadTestsFromTestCase(PCAxisParserTestCase)
      unittest.TextTestRunner(verbosity=2).run(suite)
    else:
      parser = PCAxisParser()
      parser.parseFiles(param)
  else:
    raise Exception("You must specify file or directory to convert.")

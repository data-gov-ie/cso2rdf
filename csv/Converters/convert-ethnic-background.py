#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
from Converter import Converter

# Definition of the paths
DSD = os.path.join("..", "..", "DSDs", "persons-by-ethnic-background.ttl")
ED_FILE = os.path.join("..", "Datasources", "ed", "ethnic_background.csv")
EA_FILE = os.path.join("..", "Datasources", "ea", "ethnic_background.csv")


class ConvertEthnicBackground (Converter):
  
  def __init__(self,):
    
    
if __name__ == "__main__":
  ceb = ConvertEthnicBackground(
  )
  ceb.main()

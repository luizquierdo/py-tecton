#!/usr/bin/python
# -*- coding: utf-8 -*-

from Integrador import Integrador

import os, shutil, logging
from logging.config import fileConfig
import json

integrador = Integrador()

with open('factura.json') as data_file:
    data = json.load(data_file)

integrador.crear_factura_venta_desde_so(data)

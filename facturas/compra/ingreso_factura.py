#!/usr/bin/python
# -*- coding: utf-8 -*-

from facturas.DTE import DTE
from facturas.compra.TectonImapClient import TectonImapClient
from facturas.compra.IntegradorFacturaCompra import IntegradorFacturaCompra

import os, shutil, logging
from logging.config import fileConfig

fileConfig('logging_config.ini')
logger = logging.getLogger()
logger.debug("ejecutando programa")

## primero leer el correo y descargar los XML

os.chdir("./DESCARGA_DTES")
TectonImapClient().descargar_xml_dtes()

integrador = IntegradorFacturaCompra()

for file in os.listdir("."):

    if file.endswith(".xml") or file.endswith(".XML"):
        head, tail = os.path.split(os.path.abspath(file))
        shutil.move(file, os.path.join(head, "XML"))

    elif os.path.isfile(file):
        os.remove(file)

os.chdir("./XML")

for file in os.listdir("."):

    if os.path.isdir(file):
        continue

    try:
        dte = DTE(file)

        if dte.tipo_dte == 33 and not dte.es_respuesta():
            os.rename("./" + file, "./DTE_33/" + file)
        elif dte.tipo_dte == 34:
            os.rename("./" + file, "./DTE_34/" + file)
        elif dte.tipo_dte == 52:
            os.rename("./" + file, "./DTE_52/" + file)
        elif dte.tipo_dte == 61:
            os.rename("./" + file, "./DTE_61/" + file)
        elif not os.path.isdir(file):
            os.rename("./" + file, "./NO_DTE/" + file)

    except:
        if os.path.exists(file) and not os.path.isdir(file):
            os.rename("./" + file, "./NO_DTE/" + file)

os.chdir("./DTE_33")

for file in os.listdir("."):

    if os.path.isdir(file):
        continue

    try:
        dte = DTE(file)

        facturas = integrador.get_facturas(dte.numero_factura, dte.rut_proveedor)

        if len(facturas) > 0:
            os.rename("./" + file, "./INGRESADO/" + file)
        else:
            os.rename("./" + file, "./POR_INGRESAR/" + file)

    except Exception as e:
        logger.error(
            "ERROR AL CLASIFICAR SI LAS FACTURAS ESTAN INGRESADAS, ARCHIVO: " + file + ", EXCEPCION: " + e.message)

os.chdir("./POR_INGRESAR")

for file in os.listdir("."):

    if os.path.isdir(file): continue

    try:
        dte = DTE(file)

        if dte.numero_referencias_GD() > 0:
            os.rename("./" + file, "./REF_GD/" + file)
        elif dte.numero_referencias_OC() > 0:
            os.rename("./" + file, "./REF_OC/" + file)
        else:
            os.rename("./" + file, "./SIN_REF/" + file)
    except Exception as e:
        logger.error("ERROR AL CLASIFICAR REFERENCIAS, ARCHIVO: " + file + ", EXCEPCION: " + e.message)

os.chdir("./SIN_REF")
for file in os.listdir("."):

    if os.path.isdir(file):
        continue

    try:
        dte = DTE(file)
        logger.debug(
            "Ingresando factura " + dte.numero_factura + " " + integrador.get_nombre_proveedor(dte.rut_proveedor))
        # integrador.crear_factura(dte)
        # os.rename("./" + file, "./INGRESADAS/" + file)

    except Exception as e:
        logger.error("ERROR AL CREAR FACTURA, ARCHIVO: " + file + ", EXCEPCION: " + e.message)

# for file in os.listdir("."):
#
#    if not file.endswith(".xml"): continue
#
#    print("PROCESANDO EL ARCHIVO: " + file)

# leemos el XML. Si hay excepciones, continuamos con el siguiente archivo XML
#    try:
#        dte = DTE(file)
#    except:
#        continue

#    nom_guia = integrador.buscar_guia_por_monto(dte)
#    print("Guia: " + nom_guia)
#    si se encuentra una guia en el ERP, ingresamos la factura a partir de la guia.
#    si hay errores en la creacion de la factura a partir de la guia, procedemos con el siguiente XML
#    if nom_guia != "NO_HAY_GUIA":
#        try:
#            integrador.insertar_factura_desde_guia(nom_guia, dte)
#            continue
#        except:
#            continue

#    nombre_oc = integrador.buscar_oc_por_monto(dte)
#    print("OC: " + nombre_oc)
#    if nombre_oc != "NO_HAY_OC":
#        try:
## creamos la guia
## hay que validar si el documento es guía o factura.
#            nom_guia = integrador.insertar_guia_desde_oc(nombre_oc, dte)
#            if dte.tipo_dte == 33 or dte.tipo_dte == 34:
## creamos la factura
#                nombre_factura = integrador.crear_factura(dte)
#                print("Factura Ingresada!: " + nombre_factura)
#                continue
#        except:
#            continue

#    try:
# crear_factura(dte)
#        print("creando guía")
#        nom_guia = integrador.crear_guia(dte)
#        if dte.tipo_dte != 33 or 34:
#            print("creando factura")
#            integrador.crear_factura(dte)
#        os.rename("./" + file, "./XML_OK/" + file)
#        print("nueva factura y guía creadas desde cero")
#    except:
#        print("Error al crear factura desde cero")
#        if os.path.exists("./" + file) :
#            os.rename("./" + file, "./XML_NOK/" + file)

######################################################################################################

# if integrador.existe_factura(folio, proveedor)
#    salir
#
# if dte.contar_referencias_GD() = 0:
#
#    if dte.contar_referencias_OC = 0:
#
#        if integrador.buscar_gd_por_monto() is not None :
#            integrador.insertar_factura_desde_guia()
#
#        else if integrador.buscar_oc_por_monto() is not None:
#            integrador.insertar_guia_desde_oc()
#
#   elif dte.contar_referencias_OC = 1
#       oc = integrador.buscar_oc(numero_referencia)
#       if oc is not None and (dte.tipo_dte == 33 or dte.tipo_dte = 52):
#            integrador.generar_guia_desde_oc()
# else integrador.ejecutar_flujo_por_monto()
#
#   else:
# if numero referencias OC es mayor que 1
# for referencia in referencias:
# oc = integrador.buscar_oc(numero_referencia)
# integrador.agregar_items_oc_a_guia()

# elif dte.contar_referencias_GD() = 1
# factura = integrador.hacer_factura_desde_guia()
# if factura is None:
# integrador.ejecutar_flujo_por_monto()

# elif dte.contar_referencias_GD() > 1
# for referencia in referencias:
# gd = integrador.buscar_gd(numero_referencia)
# integrador.agregar_items_gd_a_factura()

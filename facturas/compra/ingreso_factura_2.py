#!/usr/bin/python
# -*- coding: utf-8 -*-

from facturas.DTE import DTE
from facturas.compra.TectonImapClient import TectonImapClient
from facturas.compra.IntegradorFacturaCompra import IntegradorFacturaCompra

import os, shutil, logging
from logging.config import fileConfig


def ingresar_fc_por_referencias_a_guia(dte):

    for referencia in dte.referencias:

        if (referencia["tipo_doc_referencia"] != "52"): continue

        numero_guia = referencia["folio_referencia"]

        numero_guia = int(numero_guia)

        guias = integrador.buscar_gd(dte.rut_proveedor, numero_guia)

        if len(guias) == 0:
            logger.debug("no se encontro la guia para la factura " + dte.numero_factura + " " + dte.rut_proveedor)
            continue

        gd = guias[0]
        if float(gd["per_billed"]) > 95:
            logger.debug(
                "la guia en referencia ya esta facturada en mas que un 95% " + dte.numero_factura + " del proveedor " + dte.rut_proveedor)
            continue

        factura = integrador.crear_factura_desde_gd(gd, dte.numero_factura, dte.fecha)
        os.rename("./" + file, "./INGRESADAS_POR_REFERENCIA_GUIA/" + file)

        logger.debug("factura ingresada" + dte.numero_factura + " " + dte.rut_proveedor)

        return factura

    return None

def ingresar_fc_por_referencias_oc(dte):

    for referencia in dte.referencias:
        if (referencia["tipo_doc_referencia"] != "801"):
            continue

        numero_oc = referencia["folio_referencia"]
        ocs = integrador.buscar_oc(dte.rut_proveedor, numero_oc)

        if len(ocs) == 0:
            logger.debug("no se encontro la OC para la factura " + dte.numero_factura + " " + dte.rut_proveedor)
            continue

        oc = ocs[0]
        if float(oc["per_billed"]) > 95:
            logger.debug(
                "la guia en referencia ya esta facturada en mas que un 95% " + dte.numero_factura + " del proveedor " + dte.rut_proveedor)
            continue

        factura = integrador.crear_factura_desde_oc(oc, dte.numero_factura, dte.fecha)
        logger.debug(
            "factura ingresada" + dte.numero_factura + " " + dte.rut_proveedor)
        os.rename("./" + file, "./INGRESADAS_POR_REFERENCIA_OC/" + file)

        return factura

    return None

fileConfig('logging_config.ini')
logger = logging.getLogger()
logger.debug("ejecutando programa")

## primero leer el correo y descargar los XML
os.chdir("./DESCARGA_DTES")
TectonImapClient().descargar_xml_dtes()

integrador = IntegradorFacturaCompra()

for file in os.listdir("."):

    try:

        # si el archivo no existe o es un directorio, sigo adelante con el siguiente archivo
        if not os.path.exists(file) or os.path.isdir(file):
            continue

        # si el archivo no es XML, lo elimino y sigo con el siguiente archivo
        if not file.endswith(".xml") and not file.endswith(".XML"):
            os.remove(file)
            continue

        dte = DTE(file)

        # si hubo un error al leer el DTE, sigo adelante con el siguiente archivo y muevo el actual a BASURA
        if not dte.bien_formado == 1:
            os.rename("./" + file, "./BASURA/" + file)
            continue

        # si el DTE no es 33 (factura de compra), prosigo con el siguiente
        if dte.tipo_dte != 33 or dte.es_respuesta():
            os.rename("./" + file, "./BASURA/" + file)
            continue

        facturas = integrador.get_facturas(dte.numero_factura, dte.rut_proveedor)

        # si ya hay una factura ingresada en el ERP para el DTE, mover a INGRESADO y continuar con el siguiente archivo
        if len(facturas) > 0:
            os.rename("./" + file, "./FACTURA_YA_EXISTE_EN_ERP/" + dte.fecha + "_" + dte.rut_proveedor + "_" + dte.numero_factura + ".xml")
            continue

        # ingreso las facturas que tienen referencias a guias de despacho, desde la guia
        if dte.numero_referencias_GD() > 0:
            factura = ingresar_fc_por_referencias_a_guia(dte)
            if not factura is None: continue

        # ingreso las facturas que tienen referencias a ordenes de compra, desde la oc
        if dte.numero_referencias_OC() > 0:
            factura = ingresar_fc_por_referencias_oc(dte)
            if not factura is None: continue

        os.rename("./" + file, "./FACTURAS_PROCESADAS_CON_PROBLEMAS/" + dte.fecha + "_" + dte.rut_proveedor + "_" + dte.numero_factura + ".xml")

    except Exception as e:
        logger.error("ERROR AL CREAR FACTURA, ARCHIVO: " + file)
        os.rename("./" + file, "./FACTURAS_PROCESADAS_CON_PROBLEMAS/" + file)

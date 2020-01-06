#!/usr/bin/python
# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET


class DTE:

    def __init__(self, tree_path):

        try:
            self.tree_path = tree_path
            self.tree = ET.parse(tree_path)
            self.es_respuesta()
            self.parse_encabezado()
            self.asignar_tipo_dte_palabras()
            self.parse_items()
            self.parse_referencias()
            self.bien_formado = 1
        except:
            print("ERROR AL LEER EL XML")
            self.bien_formado = 0

    def asignar_tipo_dte_palabras(self):
        if self.tipo_dte == 33:
            self.tipo_dte_palabras = "Electrónica"
        elif self.tipo_dte == 34:
            self.tipo_dte_palabras = "Electrónica Exenta"
        elif self.tipo_dte == 30:
            self.tipo_dte_palabras = "Afecta"
        elif self.tipo_dte == 52:
            self.tipo_dte_palabras = "Guia"

    def parse_encabezado(self):

        self.rut_proveedor = self.tree.find('.//{http://www.sii.cl/SiiDte}RUTEmisor').text
        self.monto_neto = self.tree.find('.//{http://www.sii.cl/SiiDte}MntNeto').text \
            if self.tree.find('.//{http://www.sii.cl/SiiDte}MntNeto') is not None else 0
        self.numero_factura = self.tree.find('.//{http://www.sii.cl/SiiDte}Folio').text.lstrip("0")
        self.fecha = self.tree.find('.//{http://www.sii.cl/SiiDte}FchEmis').text
        self.tipo_dte = int(self.tree.find('.//{http://www.sii.cl/SiiDte}TipoDTE').text)


    def parse_items(self):

        self.items = []

        for i in self.tree.findall('.//{http://www.sii.cl/SiiDte}Detalle'):
            qty = i.find("{http://www.sii.cl/SiiDte}QtyItem")
            rate = i.find("{http://www.sii.cl/SiiDte}PrcItem")
            description = i.find("{http://www.sii.cl/SiiDte}NmbItem").text
            total = i.find("{http://www.sii.cl/SiiDte}MontoItem").text

            qtytext = qty.text if qty is not None else str(1)
            ratetext = rate.text if rate is not None else total

            #print (
            #    "qty = " + qtytext + ", rate = " + ratetext + ", description = " + description + ", total = " + total)

            #"warehouse": "Bodega Generica - T",

            self.items.append(
                {"qty": qtytext,
                 "rate": ratetext,
                 "item_code": "Item Generico",
                 "project": "Oficina",
                 "cost_center": "Oficina - T",
                 "description": description}
            )
    def parse_referencias(self):

        self.referencias = []

        for r in self.tree.findall('.//{http://www.sii.cl/SiiDte}Referencia'):

            tipo_doc_referencia = r.find('{http://www.sii.cl/SiiDte}TpoDocRef').text if r.find('{http://www.sii.cl/SiiDte}TpoDocRef') is not None else ""
            folio_referencia = r.find('{http://www.sii.cl/SiiDte}FolioRef').text if r.find('{http://www.sii.cl/SiiDte}FolioRef') is not None else ""
            fecha_referencia = r.find('{http://www.sii.cl/SiiDte}FchRef').text if r.find('{http://www.sii.cl/SiiDte}FchRef') is not None else ""


            self.referencias.append({"tipo_doc_referencia": tipo_doc_referencia,
                                     "folio_referencia": folio_referencia,
                                     "fecha_referencia": fecha_referencia})

    def numero_referencias_GD(self):
        n_ref = 0
        for r in self.referencias:
            if r["tipo_doc_referencia"] == "50" or r["tipo_doc_referencia"] == "52":
                n_ref += 1

        return n_ref

    def numero_referencias_OC(self):
        n_ref = 0
        for r in self.referencias:
            if r["tipo_doc_referencia"] == "801":
                n_ref += 1

        return n_ref

    def es_respuesta(self):
        return not self.tree.find('.//{http://www.sii.cl/SiiDte}NmbEnvio') is None
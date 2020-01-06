#!/usr/bin/python
# -*- coding: utf-8 -*-
from frappeclient import FrappeClient
from operator import itemgetter
import datetime


class IntegradorFacturaCompra:
    def __init__(self):

        try:
            self.client = FrappeClient("https://erp.tecton.cl", "lizquierdo@tecton.cl", "tecton")
        except:
            print("ERROR LOGEARSE AL ERP")
            raise


    def get_facturas(self, numero_factura, rut_proveedor):

        facturas = self.client.get_doc("Purchase Invoice",
                                       filters=[["Purchase Invoice", "bill_no", "=", numero_factura],
                                                ["Purchase Invoice", "rut", "=", rut_proveedor],],
                                       fields=["name"])
        return facturas


    def crear_factura(self, dte):

        nombre_proveedor = self.get_nombre_proveedor(dte.rut_proveedor)

        factura = {"title": nombre_proveedor,
                   "doctype": "Purchase Invoice",
                   "supplier_name": nombre_proveedor,
                   "supplier": nombre_proveedor,
                   "rut": dte.rut_proveedor,
                   "items": dte.items,
                   "bill_no": dte.numero_factura,
                   "company": "Constructora Tecton SpA",
                   "docstatus": 0,
                   "tipo_factura": dte.tipo_dte_palabras,
                   "bill_date": dte.fecha,
                   "taxes_and_charges": "IVA"
                   }

        return self.client.insert(factura)

    def crear_guia(self, dte):

        nombre_proveedor = self.get_nombre_proveedor(dte.rut_proveedor)

        guia = {"doctype": "Purchase Receipt",
                "currency": "CLP",
                "title": nombre_proveedor,
                "supplier": nombre_proveedor,
                "docstatus": 0,
                "taxes_and_charges": "IVA",
                "company": "Constructora Tecton SpA",
                "supplier_name": nombre_proveedor,
                "rut": dte.rut_proveedor,
                "items": dte.items,
                "numero_guia": dte.numero_factura,
                "taxes": [
                    {"doctype": "Purchase Taxes and Charges",
                     "rate": 19.0,
                     "tax_amount_after_discount_amount": 22227.15,
                     "cost_center": "",
                     "total": 139212.15,
                     "category": "Total",
                     "base_total": 139212.15,
                     "docstatus": 0,
                     "charge_type": "On Net Total",
                     "description": "IVA",
                     "base_tax_amount_after_discount_amount": 22227.15,
                     "add_deduct_tax": "Add",
                     "base_tax_amount": 22227.15,
                     "account_head": "1.1.5.1 IVA Credito Fiscal - T",
                     "tax_amount": 22227.15,
                     "parenttype": "Purchase Receipt",
                     "parentfield": "taxes"}],
                }

    def crear_factura_desde_oc(self, oc, bill_no, bill_date):

        purchase_invoice = self.client.get_api(
            "erpnext.buying.doctype.purchase_order.purchase_order.make_purchase_invoice", {"source_name": oc["name"]}
        )

        purchase_invoice['bill_no'] = bill_no
        purchase_invoice['bill_date'] = bill_date

        due_date = datetime.datetime.strptime(bill_date, "%Y-%m-%d") + datetime.timedelta(days=30)
        due_date = due_date.strftime("%Y-%m-%d")
        purchase_invoice['due_date'] = due_date

        return self.client.insert(purchase_invoice)

    def crear_factura_desde_gd(self, gd, bill_no, bill_date):

        name_gd = gd["name"]

        purchase_invoice = self.client.get_api(
            "erpnext.stock.doctype.purchase_receipt.purchase_receipt.make_purchase_invoice", {"source_name": name_gd}
        )

        purchase_invoice['bill_no'] = bill_no
        purchase_invoice['bill_date'] = bill_date

        return self.client.insert(purchase_invoice)

    def buscar_oc_monto_rut(self, monto, rut):

        ocs = self.client.get_doc("Purchase Order",
                                       filters=[["Purchase Order", "rut", "=", rut],
                                                ["Purchase Order", "docstatus", "=", 1]],
                                       fields=["name", "total"])
        resultados = []
        for oc in ocs:
            diff = abs(float(oc["total"]) - float(monto)) /  float(oc["total"])
            resultados.append([diff, oc])

        return sorted(resultados, key = itemgetter(0))[0]

    def buscar_gd_monto_rut(self, monto, rut):

        gds = self.client.get_doc("Purchase Receipt",
                                       filters=[["Purchase Receipt", "rut", "=", rut],
                                                ["Purchase Receipt", "docstatus", "=", 1]],
                                       fields=["name", "total", "numero_guia"])
        resultados = []
        for gd in gds:
            diff = abs(float(gd["total"]) - float(monto)) /  float(gd["total"])
            resultados.append([diff, gd])

        return sorted(resultados, key = itemgetter(0))[0]

    def buscar_oc(self, rut, numero_oc):
        oc = self.client.get_doc("Purchase Order",
                                  filters=[["Purchase Order", "rut", "=", rut],
                                           ["Purchase Order", "name", "like", "%" + str(numero_oc) + "%"],
                                           ["Purchase Order", "docstatus", "=", 1]],
                                            fields=["name", "total", "per_billed"])
        return oc

    def buscar_gd(self, rut, numero_guia):
        gd = self.client.get_doc("Purchase Receipt",
                                  filters=[["Purchase Receipt", "rut", "=", rut],
                                           ["Purchase Receipt", "numero_guia", "=", numero_guia],
                                           ["Purchase Receipt", "docstatus", "=", 1]],
                                            fields=["name", "total", "numero_guia", "per_billed"])
        return gd

    def get_nombre_proveedor(self, rut):
        try:
            return self.client.get_doc("Supplier",
                                               filters=[["Supplier", "rut", "=", rut]],
                                               fields=["name"])[0]["name"]
        except:
            raise Exception("RUT Proveedor " + rut + " no existe")
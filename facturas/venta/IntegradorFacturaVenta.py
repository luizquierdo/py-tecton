#!/usr/bin/python
# -*- coding: utf-8 -*-
from frappeclient import FrappeClient


class IntegradorFacturaVenta:

    def __init__(self):

        try:
            self.client = FrappeClient("https://erp.tecton.cl", "lizquierdo@tecton.cl", "tecton")
        except:
            print("ERROR LOGEARSE AL ERP")
            raise

    def crear_factura_venta_desde_so(self, datos):

        try:

            # CREAR SALES INVOICE DESDE SALES ORDER
            sales_invoice = self.client.get_api(
                "erpnext.selling.doctype.sales_order.sales_order.make_sales_invoice",
                {"source_name":datos["sales_order"]})

            # PARA CADA ITEM, ACTUALIZAR LAS CANTIDADES SEGUN AVANCE ESPECIFICACO EN ARCHIVO FACTURA.JSON
            for i in sales_invoice["items"]:

                if not i["description"] in datos["items"]:
                    i["qty"] = 0
                    #sales_invoice["items"].pop(i)

                i["qty"] = datos["items"][i["description"]]
                i["cost_center"] = i["description"]

            # INGRESAR DATOS DE ENCABEZADOS DE FACTURA
            sales_invoice["due_date"] = datos["date"]
            sales_invoice["posting_date"] = datos["date"]
            sales_invoice["numero_factura"] = datos["numero_factura"]

            # INSERTAR LA NUEVA FACTURA EN EL SISTEMA
            f = self.client.insert(sales_invoice)

            # INGRESAR CORRECCION MONETARIA
            saldo = datos["total_neto"] - f["net_total"]

            if saldo > 0:
                f["items"].append(
                    {"qty": 1,
                     "rate": saldo,
                     "item_code": "Corrección Monetaria UF",
                     "project": datos["project"],
                     "cost_center": "Oficina - T"}
                )

                self.client.update(f)

            return f

        except Exception as e:
            print("no funcionó... " + e.message)

    def crear_factura_venta(self, idSalesOrder, avances):

        so = self.client.get_doc("Sales Order",idSalesOrder)
        print(so["project"])

        items_sinv = []

        for items in so["items"]:

            if not items["description"] in avances["items"]:
                continue

            items_sinv.append(
                {"qty": avances["items"][items["description"]],
                 "rate": items["rate"],
                 "item_code": items["item_code"],
                 "project": so["project"],
                 "cost_center": items["description"],
                 "description": items["description"],
                 "sales_order": idSalesOrder}
            )

        factura = {
                  "title": "Hidroeléctrica Arrayán SpA",
                "due_date": "2017-03-06",
                "doctype": "Sales Invoice",
                "items": items_sinv,
                "rut": "76013193-8",
                "company": "Constructora Tecton SpA",
                "customer": "Hidroeléctrica Arrayán SpA",
                "numero_factura": 0,
                "project": "Central Hidroeléctrica de Pasada El Arrayán",
                "posting_date": "2017-03-06",
                "docstatus": 0,
            }

        f = self.client.insert(factura)

        return f
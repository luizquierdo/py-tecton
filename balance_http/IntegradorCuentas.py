#!/usr/bin/python
# -*- coding: utf-8 -*-
from frappeclient import FrappeClient

class IntegradorCuentas:
    def __init__(self):

        try:
            self.client = FrappeClient("https://erp.tecton.cl", "lizquierdo@tecton.cl", "tecton")
        except:
            print("ERROR LOGEARSE AL ERP")
            raise

    def obtener_saldo_cuenta(self, cuenta):

        saldo = self.client.get_api(
            "erpnext.accounts.utils.get_balance_on",
            {"account":cuenta,
             "date":"2017-04-30",
             "company":"Constructora Tecton SpA",
             "in_account_currency":True})

        return saldo

    def get_cuentas_non_group(self):

        cuentas = self.client.get_doc("Account",
                                       filters=[["Account", "is_group", "=", "False"],
                                                ["Account", "company", "=", "Constructora Tecton SpA"]],
                                       fields=["name"])

        return cuentas
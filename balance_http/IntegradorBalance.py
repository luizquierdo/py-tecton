#!/usr/bin/python
# -*- coding: utf-8 -*-
from frappeclient import FrappeClient


class IntegradorBalance:

    def __init__(self):

        try:
            self.client = FrappeClient("http://erp.tecton.cl", "lizquierdo@tecton.cl", "tecton")
        except:
            print("ERROR LOGEARSE AL ERP")
            raise

    def obtener_saldos_cuentas(self):
        params = {}
        params["source_name"] = self
        resultado = self.client.get_api("erpnext.accounts.doctype.journal_entry.journal_entry.get_account_balance_and_party_type", params)
        return resultado


    def obtener_lista_cuentas(self):
        params = {}
        params["source_name"] = self
        resultado = self.client.get_api("erpnext.accounts.utils.get_account_name", params)
        return resultado


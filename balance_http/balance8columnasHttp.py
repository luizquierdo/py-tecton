#!/usr/bin/env python
# -*- coding: utf-8 -*-


import locale
import datetime

from IntegradorBalance import IntegradorBalance

locale.setlocale(locale.LC_ALL, 'es_CL.utf8')

integradorBalance = IntegradorBalance()
fecha_inicio = datetime.date(2016, 1, 1)
fecha_termino = datetime.date(2016, 8, 31)


#   return collections.OrderedDict(sorted(d.items()))
def generarData8ColumnasHttp(integradorBalance, fecha_inicial, fecha_final, company):
    apertura = {}
    cierre = {}
    account = []
    account = integradorBalance.obtener_lista_cuentas()


#    apertura = IntegradorBalance.obtener_saldos_cuentas(account(1), fecha_inicial, company, debit=None, credit=None, exchange_rate=None)
#    cierre = IntegradorBalance.obtener_saldos_cuentas(account(1), fecha_final, company, debit=None, credit=None, exchange_rate=None)
#    return a



generarData8ColumnasHttp(integradorBalance, fecha_inicio, fecha_termino, None)

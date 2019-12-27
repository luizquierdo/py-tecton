#!/usr/bin/env python
# -*- coding: utf-8 -*-

import MySQLdb
import collections
import locale
from Cheetah.Template import Template
import subprocess
import shlex
import os
import datetime
locale.setlocale(locale.LC_ALL, 'es_CL.utf8')

fecha_inicio = datetime.date(2016, 01, 01)
fecha_termino = datetime.date(2016, 12, 31)

db = MySQLdb.connect(host="localhost",    
                     user="root",        
                     passwd="v25lkKrAa33MTE2S", 
                     db="42c0542b9b")        

# funcion que obtiene los datos agrupados por cuenta, desde la base de datos
def getDataBase(fecha_inicial, fecha_final, company):
   c = db.cursor()
   c.execute("""
    select g.account, a.root_type, round(sum(g.debit)) as debitos, 
          round(sum(g.credit)) as creditos, round((sum(g.debit) - sum(g.credit))) as saldo 
    from `tabGL Entry` g, tabAccount a 
    where a.name = g.account 
       and g.company = '""" + company + """'
       and g.posting_date <= '""" + fecha_final + """'
       and g.posting_date >= '""" + fecha_inicial + """'
       and g.docstatus = 1 
    group by g.account 
    order by g.account, a.root_type;""")
   d = {}
   for row in c.fetchall():
      d[row[0]] = [row[1], row[2], row[3], row[4]]
      print(row)
   
   return collections.OrderedDict(sorted(d.items()))
def generarData8ColumnasHttp(fecha_inicial, fecha_final, company):
    a = []

    return a

# funcion que genera las 8 columnas del balance
def generarData8Columnas(fecha_inicial, fecha_final, company):
    a = []
    d = getDataBase("2000-01-01", fecha_final, company)
    apertura = getDataBase("2000-01-01", fecha_inicial, company) 
  
    for key, value in d.iteritems():
        e = {}
        saldo_apertura = float(apertura[key][3]) if key in apertura else 0
        debito_apertura = float(apertura[key][1]) if key in apertura else 0
        credito_apertura = float(apertura[key][2]) if key in apertura else 0

        debito_total = float(value[1])
        credito_total = float(value[2])
        tipo_cuenta = value[0]

        debito_periodo = debito_total - debito_apertura + (saldo_apertura if saldo_apertura > 0 else 0)
        credito_periodo = credito_total - credito_apertura + (-saldo_apertura if saldo_apertura < 0 else 0)
        
        e['cuenta'] = key.replace(" - T", "")[:40]
        e['debitos'] = locale.format("%d", debito_periodo, grouping=True)
        e['creditos'] = locale.format("%d", credito_periodo, grouping=True)

        saldo = float(value[3])
        str_saldo = locale.format("%d", saldo if saldo >= 0 else -saldo, grouping=True)
        if saldo >= 0:
             if tipo_cuenta == "Asset" or tipo_cuenta == "Liability" or tipo_cuenta == "Equity":
                  e['deudor'] = e['activo'] = str_saldo
                  e['acreedor'] = e['pasivo'] = e['perdida'] = e['ganancia'] = 0
             elif tipo_cuenta == "Expense" or tipo_cuenta == "Income":
                  e['deudor'] = e['perdida'] = str_saldo
                  e['acreedor'] = e['activo'] = e['pasivo'] = e['ganancia'] = 0
        else:
             if tipo_cuenta == "Asset" or tipo_cuenta == "Liability" or tipo_cuenta == "Equity":
                  e['deudor'] = e['activo'] = e['perdida'] = e['ganancia'] = 0
                  e['acreedor'] = e['pasivo'] = str_saldo
             elif tipo_cuenta == "Expense" or tipo_cuenta == "Income":
                  e['deudor'] = e['activo'] = e['pasivo'] = e['perdida'] = 0
                  e['acreedor'] = e['ganancia'] = str_saldo
        a.append(e)
	
    return a

def suma_columna(data, variable):
    suma = 0;
    for r in data:
        d = r[variable] if r[variable] != 0 else '0,0'
        suma = suma + locale.atof(d)

    return suma

data = generarData8Columnas(fecha_inicio.strftime('%Y-%m-%d'), fecha_termino.strftime('%Y-%m-%d'), "Consorcio HLI Hydrogroup SpA")

t = Template(file="balance8columnas.tpl.tex", searchList=[ { 'row': data}])

t.debitos = locale.format("%d", suma_columna(data, 'debitos'), grouping=True)
t.creditos = locale.format("%d", suma_columna(data, 'creditos'), grouping=True)
t.deudor = locale.format("%d", suma_columna(data, 'deudor'), grouping=True)
t.acreedor = locale.format("%d", suma_columna(data, 'acreedor'), grouping=True)
t.activo = locale.format("%d", suma_columna(data, 'activo'), grouping=True)
t.pasivo = locale.format("%d", suma_columna(data, 'pasivo'), grouping=True)
t.perdida = locale.format("%d", suma_columna(data, 'perdida'), grouping=True)
t.ganancia = locale.format("%d", suma_columna(data, 'ganancia'), grouping=True)
t.utilidad = locale.format("%d", suma_columna(data, 'ganancia') - suma_columna(data, 'perdida'), grouping=True)
t.fecha_inicio= fecha_inicio.strftime('%d-%m-%Y')
t.fecha_termino = fecha_termino.strftime('%d-%m-%Y')

file = open("balance.tex", "w")
file.write(str(t))
file.close()
db.close()

proc = subprocess.Popen(shlex.split('pdflatex balance.tex'))
proc.communicate()
proc = subprocess.Popen(shlex.split('pdflatex balance.tex'))
proc.communicate()

os.unlink('balance.log')
os.unlink('balance.aux')
os.unlink('balance.tex')

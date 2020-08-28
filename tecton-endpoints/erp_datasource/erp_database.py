#!/usr/bin/env python
# -*- coding: utf-8 -*-
import Cheetah
import MySQLdb
import locale
from Cheetah.Template import Template
import subprocess
import shlex
import os
import pandas as pd

locale.setlocale(locale.LC_ALL, 'es_CL.utf8')

db = MySQLdb.connect(host="localhost",
                     user="root",
                     passwd="",
                     db="dd422756b6b88fae")

# funcion que obtiene los datos agrupados por cuenta, desde la base de datos
def getDataBalance(fecha_inicial, fecha_final, company):


    c = db.cursor()
    c.execute("""
    select g.account, a.root_type, round(sum(g.debit)) as debitos, 
          round(sum(g.credit)) as creditos, round((sum(g.debit) - sum(g.credit))) as saldo 
    from `tabGL Entry` g, tabAccount a 
    where a.name = g.account 
       and g.company = '""" + company + """'
       and g.posting_date <= '""" + fecha_final + """'
       and g.posting_date > '""" + fecha_inicial + """'
       and g.docstatus = 1 
    group by g.account 
    order by g.account, a.root_type;""")

    data = pd.DataFrame(c.fetchall())
    data.columns = ["account", "type", "debitos", "creditos", "saldo"]

    c.close()

    return data


def getPeriodClosingVoucher(fecha_inicial, fecha_final, company):

    c = db.cursor()

    c.execute("""
        SELECT account, round(sum(credit)), round(sum(debit)), round(sum(debit)-sum(credit)) as saldo
        FROM `tabGL Entry` 
        WHERE voucher_type = 'Period Closing Voucher' 
            AND posting_date <= '""" + fecha_final + """'
            AND posting_date > '""" + fecha_inicial + """'
            AND company = '""" + company + """'
        GROUP BY account;""")

    data = pd.DataFrame(c.fetchall())

    if data.size > 0:
        data.columns = ["account", "debitos", "creditos", "saldo"]
    else:
        data = pd.DataFrame(columns=["account", "debitos", "creditos", "saldo"])

    c.close()

    return data


def getComprasPorItemGroup(obra):

    query = 'SELECT left(t2.item_group,3) as tipo, round(sum(qty*rate)) as suma_facturas ' \
            'FROM `tabPurchase Invoice` as t1 INNER JOIN `tabPurchase Invoice Item` as t2 on t2.parent = t1.name ' \
            'WHERE t2.cost_center LIKE ' + obra + \
                ' AND t1.docstatus = 1 ' \
            'GROUP BY tipo;'
    df = pd.read_sql(query, con=db)

    return ({"item_group": d.tipo, "suma_facturas": d.suma_facturas} for index, d in df.iterrows())


def generar_balance(fecha_inicial, fecha_final, company):

    # obtengo desde la base de datos los saldos del periodo y los saldos de apertura
    periodo = getDataBalance(fecha_inicial, fecha_final, company)
    apertura = getDataBalance("2000-01-01", fecha_inicial, company)
    period_closing = getPeriodClosingVoucher(fecha_inicial, fecha_final, 'Constructora Tecton SpA')

    # Merge del periodo y la apertura, luego el resultado con el cierre del periodo
    b = pd.merge(left=periodo, right=apertura, how='outer', left_on='account', right_on='account')
    b = pd.merge(left=b, right=period_closing, how='outer', left_on='account', right_on='account')

    # realizo manualmente el marge de la columna type, que estaba quedando con NaN
    b.loc[(b["type_x"].isnull()), "type_x"] = b["type_y"]

    pd.options.display.float_format = '{:,.0f}'.format
    with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.expand_frame_repr', False):
        print(b)

    b = b.drop(columns=["debitos_y", "creditos_y", "saldo_x", "type_y", "debitos", "creditos"]).fillna(0)

    b.columns = ["cuenta", "type", "debitos", "creditos", "saldo_apertura", "period_closing"]

    b["cuenta"] = b.apply(lambda row: str.replace(row["cuenta"][:40], " - T", ""), axis=1)
    convert_dict = {'debitos': float, 'creditos': float, "saldo_apertura": float, "period_closing": float}
    b = b.astype(convert_dict)

    # genero las columnas debitos y creditos, agregando los saldos de apertura
    b.loc[b["saldo_apertura"] > 0, "debitos"] = b["debitos"] + b["saldo_apertura"]
    b.loc[b["saldo_apertura"] < 0, "creditos"] = b["creditos"] - b["saldo_apertura"]

    # NUEVO genero las columnas debitos y creditos, agregando los saldos de apertura
    b.loc[b["period_closing"] > 0, "debitos"] = b["debitos"] - b["period_closing"]
    b.loc[b["period_closing"] < 0, "creditos"] = b["creditos"] + b["period_closing"]

    # genero las columnas deudor y acreedor
    b["deudor"] = b.apply(lambda row: max(row["debitos"] - row["creditos"], 0), axis=1)
    b["acreedor"] = b.apply(lambda row: max(row["creditos"] - row["debitos"], 0), axis=1)

    # genero las columnas de activos, pasivos, perdida y ganancia, a partir de las columnas deudor y acreedor
    b.loc[(b["type"] == "Asset") | (b["type"] == "Liability") | (b["type"] == "Equity"), "activos"] = b["deudor"]
    b.loc[(b["type"] == "Asset") | (b["type"] == "Liability") | (b["type"] == "Equity"), "pasivos"] = b["acreedor"]
    b.loc[(b["type"] == "Income") | (b["type"] == "Expense"), "perdida"] = b["deudor"]
    b.loc[(b["type"] == "Income") | (b["type"] == "Expense"), "ganancia"] = b["acreedor"]

    # limpio el balance
    b = b.drop(columns=["saldo_apertura", "period_closing"])
    b = b.fillna(0)
    # elimino las filas que tienen puros ceros
    b = b[(b.deudor + b.acreedor + b.debitos + b.creditos) != 0]
    # ordeno las cuentas
    b = b.sort_values(by=['cuenta'])

    return b


class MyFilter(Cheetah.Filters.Filter):

    def filter(self,val,numDigits=0,**kw):
        if isinstance(val,float):
            return f"{val:,.{numDigits}f}"

        return super().filter(val,**kw)

def generarLaTex(data, fecha_inicio, fecha_termino):

    t = Template(file="balance8columnas.tpl.tex", searchList=[{'row': data.to_dict('records')}], filter=MyFilter)

    t.debitos = locale.format("%d", data['debitos'].sum(), grouping=True)
    t.creditos = locale.format("%d", data['creditos'].sum(), grouping=True)
    t.deudor = locale.format("%d",  data['deudor'].sum(), grouping=True)
    t.acreedor = locale.format("%d", data['acreedor'].sum(), grouping=True)
    t.activo = locale.format("%d", data['activos'].sum(), grouping=True)
    t.pasivo = locale.format("%d", data['pasivos'].sum(), grouping=True)
    t.perdida = locale.format("%d", data['perdida'].sum(), grouping=True)
    t.ganancia = locale.format("%d", data['ganancia'].sum(), grouping=True)
    t.utilidad = locale.format("%d", data['ganancia'].sum() - data['perdida'].sum(), grouping=True)
    t.fecha_inicio = fecha_inicio
    t.fecha_termino = fecha_termino

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

 #descomentando estas lineas se puede probar generando el balance
#generarLaTex(
#   pandasBalance("2020-01-01", "2020-12-31", "Constructora Tecton SpA"), "2020-01-01", "2020-12-31"
#)

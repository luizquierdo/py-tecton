import requests
from pandas import json_normalize
import json
import numpy as np


def obtener_datos_buk(month, year, rut_empresa):

    headers = {'content-type': 'application/json', 'auth_token': 'daSY92P7JMXZzFBkZCDDMYiU'}
    url = 'https://tecton.buk.cl/api/v1/accounting/export?month=' + str(month) + '&year=' + str(
        year) + '&company_id=' + rut_empresa
    r = requests.get(url, headers=headers)

    buk = json.loads(r.content)

    data = json_normalize(buk["data"]["76.407.152-2"]["Constructora Tecton S.p.A."])

    data["deber"] = data["deber"].replace({'': 0})
    data["haber"] = data["haber"].replace({'': 0})

    return data


def reemplazar_relaciones(data):

    with open("relaciones_cuentas.json", "r") as read_file:
        relaciones_cuentas = json.load(read_file)

    data["cuenta_contable"] = data["cuenta_contable"].replace(relaciones_cuentas)

    with open("relaciones_centros_de_costos.json", "r") as read_file:
        relaciones_centros_de_costo = json.load(read_file)

    data["centro_costo"] = data["centro_costo"].replace(relaciones_centros_de_costo)

    return data


# rut, last_name, first_name, area_full_name, cuenta_contable, deber, haber, centro_costo, glosa
data = obtener_datos_buk(3, 2020, "76.407.152-2")

data = reemplazar_relaciones(data)
print(data.groupby(["centro_costo", "cuenta_contable"])["deber", "haber"].agg(np.sum))

print(data.centro_costo.unique())

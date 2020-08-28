import datetime
from erp_datasource.erp_database import generar_balance, getComprasPorItemGroup
import graphene


class Cuenta(graphene.ObjectType):
    nombre = graphene.String()
    debitos = graphene.Float()
    creditos = graphene.Float()
    deudor = graphene.Float()
    acreedor = graphene.Float()
    activo = graphene.Float()
    pasivo = graphene.Float()
    perdida = graphene.Float()
    ganancia = graphene.Float()


class Balance(graphene.ObjectType):
    nombre_empresa = graphene.NonNull(graphene.String)
    fecha_inicio = graphene.NonNull(graphene.Date)
    fecha_termino = graphene.NonNull(graphene.Date)
    cuentas = graphene.List(Cuenta)
    total_creditos = graphene.Float()
    total_debitos = graphene.Float()
    total_deudor = graphene.Float()
    total_acreedor = graphene.Float()
    total_activo = graphene.Float()
    total_pasivo = graphene.Float()
    total_perdida = graphene.Float()
    total_ganancia = graphene.Float()


class ComprasPorItemGroup(graphene.ObjectType):
    obra = graphene.NonNull(graphene.String)
    item_group = graphene.String()
    suma_facturas = graphene.Float()


class Query(graphene.ObjectType):

    balance = graphene.Field(Balance, nombre_empresa=graphene.String(), fecha_inicio=graphene.Date(),
                             fecha_termino=graphene.Date())

    def resolve_balance(parent, info, nombre_empresa, fecha_inicio, fecha_termino):
        data = generar_balance(fecha_inicio.strftime('%Y-%m-%d'),
                               fecha_termino.strftime('%Y-%m-%d'),
                               nombre_empresa
                               )

        cuentas = []
        for index, d in data.iterrows():
            cuentas.append(Cuenta(nombre=d["cuenta"],
                                  debitos=d['debitos'],
                                  creditos=d['creditos'],
                                  deudor=d['deudor'],
                                  acreedor=d['acreedor'],
                                  activo=d['activos'],
                                  pasivo=d['pasivos'],
                                  perdida=d['perdida'],
                                  ganancia=d['ganancia']
                                  )
                           )

        totales = data.sum()

        return {"nombre_empresa": nombre_empresa, "fecha_inicio": datetime.date(2019, 12, 31),
                "fecha_termino": datetime.date(2019, 12, 31),
                "cuentas": cuentas,
                "total_debitos": totales['debitos'],
                "total_creditos": totales['creditos'],
                "total_deudor": totales['deudor'],
                "total_acreedor": totales['acreedor'],
                "total_activo": totales['activos'],
                "total_pasivo": totales['pasivos'],
                "total_perdida": totales['perdida'],
                "total_ganancia": totales['ganancia']
                }

    compras_por_item_group = graphene.List(ComprasPorItemGroup, obra=graphene.String())

    def resolve_compras_por_item_group(parent, info, obra):
        return getComprasPorItemGroup(obra)


schema = graphene.Schema(query=Query)

import datetime
from erp_datasource.erp_database import generar_balance, getComprasPorItemGroup, \
    getComprasPorCentroCosto, getComprasMensualesPorCentroCosto, getComprasMensualesPorItemGroup, getOrdenesCompraNoFacturadasPorCentroCosto
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


class ComprasPorCentroCosto(graphene.ObjectType):
    obra = graphene.NonNull(graphene.String)
    cost_center = graphene.String()
    suma_facturas = graphene.Float()


class ComprasMensualesPorCentroCosto(graphene.ObjectType):
    obra = graphene.NonNull(graphene.String)
    cost_center = graphene.String()
    mes = graphene.String()
    suma_facturas = graphene.Float()

class OrdenDeCompra(graphene.ObjectType):
    nombre = graphene.NonNull(graphene.String)
    supplier = graphene.String()
    total_neto = graphene.Float()

class ComprasMensualesPorItemGroup(graphene.ObjectType):
    obra = graphene.NonNull(graphene.String)
    item_group = graphene.String()
    mes = graphene.String()
    suma_facturas = graphene.Float()

class OrdenesCompraNoFacturadasPorCentroCosto(graphene.ObjectType):
    obra = graphene.NonNull(graphene.String)
    cost_center = graphene.String()
    suma_ordenes_compra = graphene.Float()
    cantidad_oc_pendientes = graphene.Int()
    lista_ocs_pendientes = graphene.List(OrdenDeCompra)

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

    compras_por_centro_costo = graphene.List(ComprasPorCentroCosto, obra=graphene.String())

    def resolve_compras_por_centro_costo(parent, info, obra):
        return getComprasPorCentroCosto(obra)

    compras_mensuales_por_centro_costo = graphene.List(ComprasMensualesPorCentroCosto, obra=graphene.String())

    def resolve_compras_mensuales_por_centro_costo(parent, info, obra):
        return getComprasMensualesPorCentroCosto(obra)

    compras_mensuales_por_item_group = graphene.List(ComprasMensualesPorItemGroup, obra=graphene.String())

    def resolve_compras_mensuales_por_item_group(parent, info, obra):
        return getComprasMensualesPorItemGroup(obra)

    oc_pendientes_facturar_por_centro_costo = graphene.List(OrdenesCompraNoFacturadasPorCentroCosto, obra=graphene.String())

    def resolve_oc_pendientes_facturar_por_centro_costo(parent, info, obra):
        return getOrdenesCompraNoFacturadasPorCentroCosto(obra)


schema = graphene.Schema(query=Query)

import unittest
from facturas.DTE import DTE
from facturas.compra.IntegradorFacturaCompra import IntegradorFacturaCompra

class TestCompras(unittest.TestCase):

    def setUp(self):
        self.dte_guia = DTE('./XML_PRUEBAS/guia.xml')
        self.dte_falabella_descuentos = DTE('./XML_PRUEBAS/falabella_descuentos.xml')
        self.dte_melon_referencias = DTE('./XML_PRUEBAS/melon_referencias.xml')
        self.dte_nota_credito = DTE('./XML_PRUEBAS/nota_credito.xml')
        self.dte_petroleo = DTE('./XML_PRUEBAS/petroleo.xml')
        self.dte_supermercado = DTE('./XML_PRUEBAS/supermercado.xml')
        self.integrador = IntegradorFacturaCompra()

    def test_guia(self):
        print("running test guia")
        self.assertEqual(self.dte_guia.tipo_dte_palabras, "Guia")

    def test_crear_factura_desde_oc(self):
        po = self.integrador.crear_factura_desde_oc("OC-07490", 1234, "2019-12-26")
        print(po)

    def test_buscar_oc_por_monto(self):
        oc = self.integrador.buscar_oc_monto_rut(self.dte_melon_referencias.monto_neto, self.dte_melon_referencias.rut_proveedor)
        print(oc)

    def test_buscar_gd_por_monto(self):
        gd = self.integrador.buscar_gd_monto_rut(self.dte_melon_referencias.monto_neto, self.dte_melon_referencias.rut_proveedor)
        print(gd)

    def test_referencias(self):

        print("running test referencias")

        self.dte_melon_referencias.parse_referencias()
        self.assertGreater(self.dte_melon_referencias.referencias.__len__(), 0)
        self.assertEquals(self.dte_melon_referencias.referencias[0]["tipo_doc_referencia"], "801")
        self.assertEquals(self.dte_melon_referencias.referencias[0]["fecha_referencia"], "2016-08-31")
        self.assertEquals(self.dte_melon_referencias.referencias[0]["folio_referencia"], "508")

        self.dte_supermercado.parse_referencias()
        self.assertEquals(self.dte_supermercado.referencias.__len__(), 0)

    def test_get_nombre_proveedor(self):
        nombre_proveedor = self.integrador.get_nombre_proveedor("80565900-9")
        self.assertEquals(nombre_proveedor, "Yolito Balart Hermanos Limitada")

if __name__ == '__main__':
    unittest.main()

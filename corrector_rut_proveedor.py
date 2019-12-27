from frappeclient import FrappeClient


client = FrappeClient("https://hli.erpnext.com", "lizquierdo@hli.cl", "!M0r3m4g1c,")

proveedores = client.get_doc("Supplier")

for proveedor in proveedores:
   p = client.get_doc("Supplier", proveedor.get("name"))
   rut = p["rut"]
   p["rut"] = rut.replace(".", "")
   print(p)
   client.update(p)


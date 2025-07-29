class Precios:
    @staticmethod
    def calcula_precio_final(precio_base,impuesto,descuento):
        return precio_base + impuesto - descuento
import unittest

from Aplicacion_Ventas.gestor_de_ventas import GestorVentas
from Aplicacion_Ventas.excepciones import ImpuestoInválidoError,DescuentoInválidoError

class TestGestorVentas(unittest.TestCase):
    def test_calculo_precio_final(self):
        gestor = GestorVentas(100.0,0.05,0.10)
        self.assertEqual(gestor.calcular_precio_final(),95.0)#Valores iguales con assertEqual
    
    def test_impuesto_inválido(self):
        with self.assertRaises(ImpuestoInválidoError):#Comprobar si se genera la excepción
            GestorVentas(100.0,1.5,0.10)
    
    def test_descuento_inválido(self):
        with self.assertRaises(DescuentoInválidoError):
            GestorVentas(100.0,0.05,1.5)

if __name__ == "__main__":
    unittest.main()
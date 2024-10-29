import pandas as pd
from experta import *

# Definimos la clase del sistema experto
class GastoExperto(KnowledgeEngine):

    @Rule(AND(
        Fact('compras_mensuales', lambda x: x > 100),
        Fact('promedio_mensual', lambda x: x > 50)
    ))
    def regla_compras_altas(self):
        print("El cliente es probable que realice una compra significativa el próximo mes.")

    @Rule(Fact('historial_alto_precio', True))
    def regla_categoria_alta(self):
        print("Asignará un presupuesto estimado más alto para sus futuras compras.")

    @Rule(Fact('tarjeta_fidelidad', True))
    def regla_tarjeta_fidelidad(self):
        print("Es más probable que aumente su gasto debido a los incentivos.")

def calcular_promedio_compras(datos, cliente_id):
    compras_cliente = datos[datos['Cliente_ID'] == cliente_id].copy()
    compras_cliente.loc[:, 'Fecha'] = pd.to_datetime(compras_cliente['Fecha'], dayfirst=True)
    compras_recientes = compras_cliente[compras_cliente['Fecha'] >= (pd.Timestamp.now() - pd.DateOffset(months=3))]
    
    total_gasto = compras_recientes[['Conservas', 'Panadería', 'Congelados', 'Higiene', 'Hogar']].replace({'€': '', ',': '.'}, regex=True).astype(float).sum(axis=1).sum()
    
    promedio = total_gasto / len(compras_recientes) if len(compras_recientes) > 0 else 0
    return promedio

# Cargar datos desde el CSV
datos = pd.read_csv('compras.csv')

# Limpiar y convertir los tipos de datos al cargar el CSV
for col in ['Conservas', 'Panadería', 'Congelados', 'Higiene', 'Hogar']:
    datos[col] = datos[col].replace({'€': '', ',': '.'}, regex=True).astype(float)

# Crear el motor del sistema experto
gasto_experto = GastoExperto()

# Solicitar el ID del cliente por consola
cliente_id = int(input("Introduce el ID del cliente que quieres evaluar: "))
compras_cliente = datos[datos['Cliente_ID'] == cliente_id]

# Imprimir información del cliente
print(f"\nInformación del Cliente ID {cliente_id}:")
print(compras_cliente)

# Calcular promedio y compras mensuales
promedio = calcular_promedio_compras(datos, cliente_id)
compras_mensuales = datos[datos['Cliente_ID'] == cliente_id][['Conservas', 'Panadería', 'Congelados', 'Higiene', 'Hogar']].sum(axis=1).iloc[0]

# Hechos a añadir
gasto_experto.reset()
gasto_experto.declare(Fact('compras_mensuales', compras_mensuales))
gasto_experto.declare(Fact('promedio_mensual', promedio))

# Verifica si el cliente tiene historial de compras en categorías de alto precio
categorias_altas = ['Conservas', 'Panadería', 'Congelados', 'Higiene', 'Hogar']
historial_alto_precio = any(datos.loc[datos['Cliente_ID'] == cliente_id, categorias_altas].sum() > 100)
gasto_experto.declare(Fact('historial_alto_precio', historial_alto_precio))

# Verifica si el cliente tiene tarjeta de fidelidad
tarjeta_fidelidad = any(datos['Tarjeta_Fidelidad'][datos['Cliente_ID'] == cliente_id])
gasto_experto.declare(Fact('tarjeta_fidelidad', tarjeta_fidelidad))

# Ejecutar el motor
gasto_experto.run()

# Imprimir los hechos para verificar
print("Hechos declarados:")
print(f"Compras mensuales: {compras_mensuales}")
print(f"Promedio mensual: {promedio}")
print(f"Historial alto precio: {historial_alto_precio}")
print(f"Tarjeta de fidelidad: {tarjeta_fidelidad}")

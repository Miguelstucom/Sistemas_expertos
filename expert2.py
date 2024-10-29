import pandas as pd
from experta import *

# Definimos la clase del sistema experto para clasificación
class FidelidadExperto(KnowledgeEngine):

    @Rule(AND(
        Fact('uso_tarjeta', lambda x: x > 0.5),
        Fact('descuentos_recibidos', True)
    ))
    def regla_probabilidad_alta(self):
        print("Es probable que el cliente use la tarjeta de fidelidad en futuras compras.")

    @Rule(AND(
        Fact('uso_tarjeta', lambda x: x <= 0.5),
        Fact('compra_gran_valor', True)
    ))
    def regla_notificacion(self):
        print("Enviar notificación recordando los beneficios de la tarjeta de fidelidad.")

def calcular_fidelidad(datos, cliente_id):
    compras_cliente = datos[datos['Cliente_ID'] == cliente_id].copy()
    
    # Calcular el total de compras y el total de compras con tarjeta de fidelidad
    total_compras = len(compras_cliente)
    compras_con_tarjeta = compras_cliente['Tarjeta_Fidelidad'].sum()

    # Calcular el uso de la tarjeta de fidelidad
    uso_tarjeta = compras_con_tarjeta / total_compras if total_compras > 0 else 0
    
    # Verificar si hubo una compra de gran valor sin usar la tarjeta
    gran_valor = any(compras_cliente[['Conservas', 'Panadería', 'Congelados', 'Higiene', 'Hogar']].sum(axis=1) > 100) and not compras_cliente['Tarjeta_Fidelidad'].any()
    
    # Verificar si el cliente ha recibido descuentos
    descuentos_recibidos = any(compras_cliente['Tarjeta_Fidelidad'] & (compras_cliente[['Conservas', 'Panadería', 'Congelados', 'Higiene', 'Hogar']].sum(axis=1) > 50))
    
    return uso_tarjeta, gran_valor, descuentos_recibidos

# Cargar datos desde el CSV
datos = pd.read_csv('compras.csv')

# Limpiar y convertir los tipos de datos al cargar el CSV
for col in ['Conservas', 'Panadería', 'Congelados', 'Higiene', 'Hogar']:
    datos[col] = datos[col].replace({'€': '', ',': '.'}, regex=True).astype(float)

# Crear el motor del sistema experto
fidelidad_experto = FidelidadExperto()

# Solicitar el ID del cliente por consola
cliente_id = int(input("Introduce el ID del cliente que quieres evaluar: "))
compras_cliente = datos[datos['Cliente_ID'] == cliente_id]

# Imprimir información del cliente
print(f"\nInformación del Cliente ID {cliente_id}:")
print(compras_cliente)

# Calcular uso de tarjeta, gran valor y descuentos recibidos
uso_tarjeta, compra_gran_valor, descuentos_recibidos = calcular_fidelidad(datos, cliente_id)

# Hechos a añadir
fidelidad_experto.reset()
fidelidad_experto.declare(Fact('uso_tarjeta', uso_tarjeta))
fidelidad_experto.declare(Fact('compra_gran_valor', compra_gran_valor))
fidelidad_experto.declare(Fact('descuentos_recibidos', descuentos_recibidos))

# Ejecutar el motor
fidelidad_experto.run()

# Imprimir los hechos para verificar
print("Hechos declarados:")
print(f"Uso de tarjeta: {uso_tarjeta}")
print(f"Compra de gran valor: {compra_gran_valor}")
print(f"Descuentos recibidos: {descuentos_recibidos}")

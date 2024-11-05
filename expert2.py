import PySimpleGUI as sg
import pandas as pd
from experta import Fact, KnowledgeEngine, Rule, AND


# Definimos la clase del sistema experto para clasificación
class FidelidadExperto(KnowledgeEngine):

    @Rule(
        AND(Fact("uso_tarjeta", lambda x: x > 0.5), Fact("descuentos_recibidos", True))
    )
    def regla_probabilidad_alta(self):
        sg.popup(
            "Es probable que el cliente use la tarjeta de fidelidad en futuras compras."
        )

    @Rule(AND(Fact("uso_tarjeta", lambda x: x <= 0.5), Fact("compra_gran_valor", True)))
    def regla_notificacion(self):
        sg.popup(
            "Enviar notificación recordando los beneficios de la tarjeta de fidelidad."
        )


# Función para calcular fidelidad
def calcular_fidelidad(datos, cliente_id):
    compras_cliente = datos[datos["Cliente_ID"] == cliente_id].copy()

    # Calcular el total de compras y el total de compras con tarjeta de fidelidad
    total_compras = len(compras_cliente)
    compras_con_tarjeta = compras_cliente["Tarjeta_Fidelidad"].sum()

    # Calcular el uso de la tarjeta de fidelidad
    uso_tarjeta = compras_con_tarjeta / total_compras if total_compras > 0 else 0

    # Verificar si hubo una compra de gran valor sin usar la tarjeta
    gran_valor = (
        any(
            compras_cliente[
                ["Conservas", "Panadería", "Congelados", "Higiene", "Hogar"]
            ].sum(axis=1)
            > 100
        )
        and not compras_cliente["Tarjeta_Fidelidad"].any()
    )

    # Verificar si el cliente ha recibido descuentos
    descuentos_recibidos = any(
        compras_cliente["Tarjeta_Fidelidad"]
        & (
            compras_cliente[
                ["Conservas", "Panadería", "Congelados", "Higiene", "Hogar"]
            ].sum(axis=1)
            > 50
        )
    )

    return uso_tarjeta, gran_valor, descuentos_recibidos


# Cargar datos desde el CSV
datos = pd.read_csv("compras.csv")

# Limpiar y convertir los tipos de datos al cargar el CSV
for col in ["Conservas", "Panadería", "Congelados", "Higiene", "Hogar"]:
    datos[col] = datos[col].replace({"€": "", ",": "."}, regex=True).astype(float)

# Crear el layout de PySimpleGUI
layout = [
    [sg.Text("Introduce el ID del cliente:"), sg.InputText(key="cliente_id")],
    [sg.Button("Evaluar fidelidad"), sg.Exit()],
]

# Crear la ventana
window = sg.Window("Sistema Experto de Fidelidad", layout)

# Loop de eventos
while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, "Exit"):
        break

    if event == "Evaluar fidelidad":
        try:
            cliente_id = int(values["cliente_id"])
            compras_cliente = datos[datos["Cliente_ID"] == cliente_id]

            if compras_cliente.empty:
                # Si el cliente no existe, buscar el ID más cercano
                ids_disponibles = datos["Cliente_ID"].unique()
                id_mas_cercano = min(ids_disponibles, key=lambda x: abs(x - cliente_id))

                # Mostrar mensaje de error con el ID sugerido
                sg.popup(
                    f"No existe el Cliente ID {cliente_id}.",
                    f"Quizás querías introducir el ID {id_mas_cercano}.",
                    title="Error de ID",
                    background_color="#c2191c",  # Color rojo suave
                )
            else:
                # Calcular fidelidad
                uso_tarjeta, compra_gran_valor, descuentos_recibidos = (
                    calcular_fidelidad(datos, cliente_id)
                )

                # Crear el motor del sistema experto y declarar hechos
                fidelidad_experto = FidelidadExperto()
                fidelidad_experto.reset()
                fidelidad_experto.declare(Fact("uso_tarjeta", uso_tarjeta))
                fidelidad_experto.declare(Fact("compra_gran_valor", compra_gran_valor))
                fidelidad_experto.declare(
                    Fact("descuentos_recibidos", descuentos_recibidos)
                )

                # Ejecutar el motor
                fidelidad_experto.run()

                # Convertir uso_tarjeta a "Sí" o "No"
                uso_tarjeta_texto = "Sí" if uso_tarjeta > 0 else "No"

                # Mostrar resultados
                sg.popup(
                    f"Cliente ID {cliente_id}",
                    f"Uso de tarjeta: {uso_tarjeta_texto}",
                    f"Compra de gran valor: {'Sí' if compra_gran_valor else 'No'}",
                    f"Descuentos recibidos: {'Sí' if descuentos_recibidos else 'No'}",
                )

        except ValueError:
            sg.popup("Por favor, introduce un ID de cliente válido.")

window.close()
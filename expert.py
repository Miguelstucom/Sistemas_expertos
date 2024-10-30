import pandas as pd
from experta import *
import PySimpleGUI as sg

class GastoExperto(KnowledgeEngine):

    @Rule(AND(
        Fact('compras_mensuales', lambda x: x > 100),
        Fact('promedio_mensual', lambda x: x > 50)
    ))
    def regla_compras_altas(self):
        sg.popup("El cliente es probable que realice una compra significativa el próximo mes.")

    @Rule(Fact('historial_alto_precio', True))
    def regla_categoria_alta(self):
        sg.popup("Asignará un presupuesto estimado más alto para sus futuras compras.")

    @Rule(Fact('tarjeta_fidelidad', True))
    def regla_tarjeta_fidelidad(self):
        sg.popup("Es más probable que aumente su gasto debido a los incentivos.")

def calcular_promedio_compras(datos, cliente_id):
    compras_cliente = datos[datos['Cliente_ID'] == cliente_id].copy()
    compras_cliente.loc[:, 'Fecha'] = pd.to_datetime(compras_cliente['Fecha'], dayfirst=True)
    compras_recientes = compras_cliente[compras_cliente['Fecha'] >= (pd.Timestamp.now() - pd.DateOffset(months=3))]
    
    total_gasto = compras_recientes[['Conservas', 'Panadería', 'Congelados', 'Higiene', 'Hogar']].replace({'€': '', ',': '.'}, regex=True).astype(float).sum(axis=1).sum()
    
    promedio = total_gasto / len(compras_recientes) if len(compras_recientes) > 0 else 0
    return promedio

datos = pd.read_csv('compras.csv')

for col in ['Conservas', 'Panadería', 'Congelados', 'Higiene', 'Hogar']:
    datos[col] = datos[col].replace({'€': '', ',': '.'}, regex=True).astype(float)

layout = [
    [sg.Text("Introduce el ID del cliente que quieres evaluar:")],
    [sg.Input(key='cliente_id')],
    [sg.Button("Evaluar"), sg.Exit()],
    [sg.Text("Información del cliente:", size=(40, 1))],
    [sg.Table(
        headings=['Cliente_ID', 'Compra_ID', 'Conservas', 'Panadería', 'Congelados', 'Higiene', 'Hogar', 'Cross_Selling', 'Tarjeta_Fidelidad', 'Fecha'],
        values=[],
        key='info_cliente',
        display_row_numbers=False,
        auto_size_columns=False,
        col_widths=[9, 9, 8, 8, 9, 8, 8, 10, 13, 10],
        justification='center'
    )],
    [sg.Text("Resultados del sistema experto:", size=(40, 1))],
    [sg.Multiline(size=(40, 5), key='resultado', disabled=True)],
]

window = sg.Window("Sistema Experto de Gastos del Cliente", layout)
gasto_experto = GastoExperto()

while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED or event == 'Exit':
        break
    if event == "Evaluar":
        try:
            cliente_id = int(values['cliente_id'])
            compras_cliente = datos[datos['Cliente_ID'] == cliente_id]
            
            compras_cliente_values = compras_cliente.values.tolist()
            window['info_cliente'].update(compras_cliente_values)
            
            promedio = calcular_promedio_compras(datos, cliente_id)
            compras_mensuales = compras_cliente[['Conservas', 'Panadería', 'Congelados', 'Higiene', 'Hogar']].sum(axis=1).iloc[0]
            
            gasto_experto.reset()
            gasto_experto.declare(Fact('compras_mensuales', compras_mensuales))
            gasto_experto.declare(Fact('promedio_mensual', promedio))
            
            categorias_altas = ['Conservas', 'Panadería', 'Congelados', 'Higiene', 'Hogar']
            historial_alto_precio = any(compras_cliente[categorias_altas].sum() > 100)
            gasto_experto.declare(Fact('historial_alto_precio', historial_alto_precio))
            
            tarjeta_fidelidad = any(compras_cliente['Tarjeta_Fidelidad'])
            gasto_experto.declare(Fact('tarjeta_fidelidad', tarjeta_fidelidad))
            
            gasto_experto.run()
            resultados = (
                f"Compras mensuales: {compras_mensuales}\n"
                f"Promedio mensual: {promedio}\n"
                f"Historial alto precio: {historial_alto_precio}\n"
                f"Tarjeta de fidelidad: {tarjeta_fidelidad}\n"
            )
            window['resultado'].update(resultados)
            
        except Exception as e:
            sg.popup_error(f"Error: {str(e)}")

window.close()

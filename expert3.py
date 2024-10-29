import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Cargar datos desde el CSV
datos = pd.read_csv('compras.csv')

# Limpiar y convertir los tipos de datos al cargar el CSV
for col in ['Conservas', 'Panadería', 'Congelados', 'Higiene', 'Hogar']:
    datos[col] = datos[col].replace({'€': '', ',': '.'}, regex=True).astype(float)

# Seleccionar solo las columnas de precios
precios = datos[['Conservas', 'Panadería', 'Congelados', 'Higiene', 'Hogar']]

# Escalar los datos
scaler = StandardScaler()
precios_escalados = scaler.fit_transform(precios)

# Aplicar K-Means
k = 3  # Número de clústeres
kmeans = KMeans(n_clusters=k, random_state=42)
kmeans.fit(precios_escalados)

# Asignar clústeres a los datos originales
datos['Cluster'] = kmeans.labels_

# Imprimir los resultados
print("Datos con clústeres asignados:")
print(datos[['Cliente_ID', 'Cluster']])

# Visualizar los clústeres
plt.figure(figsize=(10, 6))
plt.scatter(precios['Conservas'], precios['Hogar'], c=datos['Cluster'], cmap='viridis', marker='o')
plt.title('Clustering de Precios utilizando K-Means')
plt.xlabel('Conservas')
plt.ylabel('Hogar')
plt.colorbar(label='Cluster')
plt.grid(True)
plt.show()

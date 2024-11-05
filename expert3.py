import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
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
k = 2  # Número de clústeres
kmeans = KMeans(n_clusters=k, random_state=42)
kmeans.fit(precios_escalados)

# Asignar clústeres a los datos originales
datos['Cluster'] = kmeans.labels_

# Imprimir los resultados
print("Datos con clústeres asignados:")
print(datos[['Cliente_ID', 'Cluster']])

# Visualizar los clústeres en un gráfico 3D
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')

# Elegir las tres categorías para visualizar
x = precios['Conservas']
y = precios['Hogar']
z = precios['Congelados']

# Graficar los datos
scatter = ax.scatter(x, y, z, c=datos['Cluster'], cmap='viridis', marker='o')
ax.set_title('Clustering de Precios utilizando K-Means (3D)')
ax.set_xlabel('Conservas')
ax.set_ylabel('Hogar')
ax.set_zlabel('Congelados')
plt.colorbar(scatter, label='Cluster')
plt.show()

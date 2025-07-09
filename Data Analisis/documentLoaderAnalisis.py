import pandas as pd
import matplotlib.pyplot as plt

# Cargar los datos
df_con = pd.read_csv('D:\RepoUnir\TFM---Educational-chatbot\LLM_testing\Times\documen_loader\PyPDFtiempos_con_images.csv')
df_sin = pd.read_csv('D:\RepoUnir\TFM---Educational-chatbot\LLM_testing\Times\documen_loader\PyPDFtiempos_sin_images.csv')

# Resumen descriptivo
print('Resumen descriptivo - Con imágenes')
print(df_con.describe())

print('\nResumen descriptivo - Sin imágenes')
print(df_sin.describe())

# Crear el gráfico
plt.figure(figsize=(12,6))
plt.plot(df_con['Documento'], df_con['Tiempo (s)'], label='Con imágenes', color='blue')
plt.plot(df_sin['Documento'], df_sin['Tiempo (s)'], label='Sin imágenes', color='red')

plt.title('Tiempos de procesamiento de documentos')
plt.xlabel('Documento')
plt.ylabel('Tiempo (s)')
plt.legend()
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()

# Guardar y mostrar el gráfico
plt.savefig('grafico_tiempos_pypdf.png')
plt.show()

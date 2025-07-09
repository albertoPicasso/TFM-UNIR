import pandas as pd
import matplotlib.pyplot as plt

# Cargar los datos
df_deepseek = pd.read_csv('D:/RepoUnir/TFM---Educational-chatbot/LLM_testing/Times/generation/DeepSeekV3-extended-tokens.csv')
df_gemma = pd.read_csv('D:/RepoUnir/TFM---Educational-chatbot/LLM_testing/Times/generation/gemma-2-9b-it-free-extended-tokens.csv')
df_llama = pd.read_csv('D:/RepoUnir/TFM---Educational-chatbot/LLM_testing/Times/generation/LLama70B-instruct-free-extended-tokens.csv')
df_mistral = pd.read_csv('D:/RepoUnir/TFM---Educational-chatbot/LLM_testing/Times/generation/mistral-24B-extended-tokens.csv')
df_gp4o = pd.read_csv('D:/RepoUnir/TFM---Educational-chatbot/LLM_testing/Times/generation/gp4o-mini-extended-tokens.csv')

# Resumen descriptivo
print('Resumen descriptivo - DeepSeekV3')
print(df_deepseek["time(s)"].describe())

print('\nResumen descriptivo - Gemma')
print(df_gemma["time(s)"].describe())

print('\nResumen descriptivo - LLama70B')
print(df_llama["time(s)"].describe())

print('\nResumen descriptivo - Mistral')
print(df_mistral["time(s)"].describe())

print('\nResumen descriptivo - GP4O-Mini')
print(df_gp4o["time(s)"].describe())

# Crear el gráfico
plt.figure(figsize=(12,6))
plt.plot(range(1, len(df_deepseek) + 1), df_deepseek['time(s)'], label='DeepSeekV3', color='blue')
plt.plot(range(1, len(df_gemma) + 1), df_gemma['time(s)'], label='Gemma', color='red')
plt.plot(range(1, len(df_llama) + 1), df_llama['time(s)'], label='LLama70B', color='green')
plt.plot(range(1, len(df_mistral) + 1), df_mistral['time(s)'], label='Mistral', color='purple')
plt.plot(range(1, len(df_gp4o) + 1), df_gp4o['time(s)'], label='GP4O-Mini', color='orange')

plt.title('Tiempos de procesamiento de generación')
plt.xlabel('Pregunta')
plt.ylabel('Tiempo (s)')
plt.legend()
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()

# Guardar y mostrar el gráfico
plt.savefig('grafico_tiempos_generacion.png')
plt.show()

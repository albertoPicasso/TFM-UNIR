# TFM — Educational RAG Chatbot

Trabajo de Fin de Máster (UNIR). Sistema de chatbot educativo basado en **Retrieval-Augmented Generation (RAG)** orientado a asignaturas de programación. Proporciona respuestas contextualizadas sobre teoría, información organizativa y ejercicios prácticos a partir de documentación del curso.

---

## Arquitectura

El sistema sigue una **arquitectura por capas** con separación entre lógica de negocio e infraestructura.

```
┌──────────────────────────────────────────────────────────────────┐
│                        PRESENTACIÓN                              │
│                                                                  │
│   ┌─────────────────────────┐   ┌───────────────────────────┐   │
│   │     FastAPI REST API    │   │      Streamlit UI         │   │
│   │  /getAnswer             │   │  Panel alumno             │   │
│   │  /replaceContent        │   │  Panel admin              │   │
│   └────────────┬────────────┘   └───────────────────────────┘   │
└────────────────│─────────────────────────────────────────────────┘
                 │
┌────────────────▼─────────────────────────────────────────────────┐
│                       CONTROLADORES                              │
│                                                                  │
│   ┌──────────────────────────┐   ┌────────────────────────────┐  │
│   │    AnswerController      │   │    UpdateController        │  │
│   │  classify → retrieve     │   │  load → split → index      │  │
│   │         → generate       │   │                            │  │
│   └──────────────┬───────────┘   └──────────────┬─────────────┘  │
└──────────────────│──────────────────────────────│────────────────┘
                   │                              │
┌──────────────────▼──────────────────────────────▼────────────────┐
│                         SERVICIOS                                │
│                                                                  │
│  ┌────────────────────────┐  ┌────────────────────────────────┐  │
│  │  RewriteClassifyService│  │    RegularUpdateService        │  │
│  │  clasifica y reformula │  │    (teoria / info)             │  │
│  └───────────┬────────────┘  └────────────────────────────────┘  │
│              │                                                   │
│  ┌───────────▼────────────┐  ┌────────────────────────────────┐  │
│  │    AnswerService       │  │    PractiseUpdateService       │  │
│  │  regular / practical   │  │    (summary tree JSON)         │  │
│  └────────────────────────┘  └────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
                   │                              │
┌──────────────────▼──────────────────────────────▼────────────────┐
│                      INFRAESTRUCTURA                             │
│                                                                  │
│  ┌──────────────────────┐  ┌───────────────┐  ┌──────────────┐  │
│  │   FAISS / Chroma     │  │  Universal    │  │    Text      │  │
│  │   DatabaseManager    │  │  DocumentLoad │  │   Splitter   │  │
│  │  BM25 + FAISS        │  │  PDF/TXT/     │  │  chunk=1500  │  │
│  │  ensemble + rerank   │  │  .py / URL    │  │  overlap=500 │  │
│  └──────────────────────┘  └───────────────┘  └──────────────┘  │
└──────────────────────────────────────────────────────────────────┘
                   │
┌──────────────────▼────────────────────────────────────────────────┐
│                    CAPA DE MODELOS (LLM)                          │
│                                                                   │
│   LLMTool  ←  LLMFactory                                         │
│                                                                   │
│   ┌────────────┐   ┌───────────────┐   ┌──────────────────────┐  │
│   │   OpenAI   │   │  Together.ai  │   │    HuggingFace       │  │
│   │ GPT-4o-mini│   │ LLaMA / Mistr │   │  (local pipeline)   │  │
│   └────────────┘   └───────────────┘   └──────────────────────┘  │
└───────────────────────────────────────────────────────────────────┘
```

### Estructura de directorios

```
Final_product/
├── main.py                          # Punto de entrada + argparse
├── API/
│   └── api.py                       # FastAPI — endpoints REST
├── controllers/
│   ├── answer_controller.py         # Orquesta classify → retrieve → generate
│   └── update_controller.py         # Orquesta carga → split → indexado
├── services/
│   ├── answer_services/
│   │   ├── rewrite_classify_service.py   # Clasifica y reformula la pregunta
│   │   ├── answer_service.py             # Retrieval + generación de respuesta
│   │   └── utils_prompts.py              # Plantillas de prompts
│   └── update_services/
│       ├── regular_update_service.py     # Indexado teoria/info (vector store)
│       ├── practise_update_service.py    # Indexado practica (summary tree)
│       └── utils_practise.py             # Árbol JSON + prompts de resumen
├── interfaces/                      # ABCs: DatabaseManager, DocumentsLoader, Splitter
├── infrastructure/
│   ├── databaseManagers/
│   │   ├── faiss_database_manager.py    # FAISS + BM25 ensemble + reranking L2
│   │   ├── chroma_database_manager.py   # ChromaDB (alternativa)
│   │   └── practise_database_manager.py # Lectura/escritura summary_tree.json
│   ├── documentLoaders/
│   │   └── universal_documents_loader.py  # PDF / TXT / .py / URL
│   └── Splitters/
│       └── text_splitter.py             # RecursiveCharacterTextSplitter
├── factories/
│   └── LLMFactory.py                # Instancia LLMs: OpenAI / HuggingFace / Together
├── tools/
│   └── LLM_tool.py                  # Wrapper genérico sobre LangChain LLMs
└── configs/
    ├── config.json                  # Configuración del sistema
    └── main_config.py               # Lectura y exposición de la config
```

```
Front_end/          # Interfaz Streamlit (panel alumno + panel admin)
PlayGround - Tests/ # Pipeline de evaluación RAGAS + benchmarks
Data Analisis/      # Scripts de análisis y gráficas comparativas
```

---

## Pipeline RAG

### Ingesta de documentos (`--update`)

```
  content/teoria/          content/info/            content/practica/
  PDF · TXT · .py          PDF · TXT · .py          PDF · TXT · .py
        │                        │                        │
        ▼                        ▼                        ▼
  DocumentLoader           DocumentLoader           DocumentLoader
  (recursive=False)        (recursive=False)        (recursive=True)
        │                        │                        │
        ▼                        ▼                        ▼
  TextSplitter             TextSplitter             merge_pages()
  chunk=1500               chunk=1500               (1 doc por fichero)
  overlap=500              overlap=500                    │
        │                        │                        ▼
        ▼                        ▼               LLM genera resumen
  Embeddings               Embeddings            pedagógico por fichero
  (mpnet-base-v2)          (mpnet-base-v2)                │
        │                        │                        ▼
        ▼                        ▼               summary_tree.json
  FAISS / Chroma           FAISS / Chroma        (árbol JSON con resúmenes)
  database/teoria/         database/info/         database/practica/
```

Formatos soportados: `.pdf`, `.txt`, `.py`, `.url`.

### Flujo de respuesta (`POST /tfm/service/getAnswer`)

```
                   Cliente (Streamlit / curl / cualquier HTTP)
                                      │
                          POST /tfm/service/getAnswer
                          { "messages": [ {role, content}, ... ] }
                                      │
                                      ▼
                             AnswerController.launch()
                                      │
                   ┌──────────────────▼──────────────────┐
                   │        RewriteClassifyService        │
                   │          LLM  (classifier)           │
                   │                                      │
                   │  Entrada: historial completo         │
                   │  ┌────────────────────────────────┐  │
                   │  │ Separa mensajes del usuario    │  │
                   │  │ Último mensaje  → pregunta     │  │
                   │  │ Mensajes previos → contexto    │  │
                   │  └────────────────────────────────┘  │
                   │                                      │
                   │  Salidas:                            │
                   │  • pregunta reformulada (autónoma)   │
                   │  • categoría clasificada             │
                   └────────────┬─────────────────────────┘
                                │
      ┌───────────────────────┼───────────────────────┐
      │                       │                       │
      ▼                       ▼                       ▼
 "teoria" /             "practica"             "irrelevante"
 "informacion"               │                       │
      │                       │                       ▼
      │               database/practica/        Respuesta fija
      │               summary_tree.json         de rechazo
      │                       │
      ▼                       ▼
 database/teoria/    ┌─────────────────────────┐
 database/info/      │ LLM lee resúmenes del   │
 (FAISS index)       │ árbol JSON y selecciona │
      │              │ los ficheros relevantes  │
      ▼              └────────────┬────────────┘
 ┌─────────────────┐              │
 │ EnsembleRetriev │              ▼
 │                 │   Carga documentos reales
 │  BM25    50%    │   de content/practica/
 │  FAISS   50%    │              │
 │  k = 10 chunks  │              ▼
 └──────┬──────────┘   ┌──────────────────────┐
        │              │ LLM genera respuesta │
        ▼              │ basada en código     │
 Reranking L2          │ fuente real          │
 (umbral d=6.5)        └──────────┬───────────┘
        │                         │
        ▼                         │
 ┌─────────────────┐              │
 │ LLM genera      │              │
 │ respuesta con   │              │
 │ contexto        │              │
 │ documental      │              │
 └────────┬────────┘              │
          │                       │
          └───────────┬───────────┘
                      │
                      ▼
          { "role": "assistant",
            "content": "..." }
```

### Retrieval híbrido (teoria/info)

El `Faiss_database_manager` implementa un `EnsembleRetriever` de LangChain que combina:

- **BM25Retriever** — búsqueda léxica exacta sobre los documentos del store.
- **FAISS** — búsqueda semántica por similitud coseno sobre embeddings.

Los resultados se fusionan con pesos iguales (0.5/0.5) y se filtran por umbral de distancia L2.

### Indexado de prácticas

El `PractiseUpdateService` no usa vector store. En su lugar:

1. Carga todos los ficheros de `practica/` recursivamente.
2. Fusiona las páginas de cada documento en un único `Document`.
3. Llama al LLM con un prompt estructurado para generar un resumen pedagógico de cada fichero.
4. Escribe los resúmenes en un árbol JSON que replica la estructura de carpetas.

En tiempo de consulta, el LLM recibe este árbol y selecciona los ficheros relevantes antes de leer su contenido real.

---

## Stack tecnológico

| Capa | Tecnología |
|---|---|
| API | FastAPI + Uvicorn |
| Frontend | Streamlit |
| Embeddings | `sentence-transformers/paraphrase-multilingual-mpnet-base-v2` |
| Vector stores | FAISS (`faiss-cpu`) · ChromaDB |
| LLM (producción) | GPT-4o-mini (OpenAI) |
| LLM (benchmarks) | LLaMA 3 70B · DeepSeek V3 · Gemma 2 9B · Mistral 24B (Together.ai) |
| Orquestación LLM | LangChain (`langchain`, `langchain-openai`, `langchain-together`) |
| Evaluación | RAGAS (`faithfulness`, `answer_correctness`, `answer_relevancy`, `context_recall`, `context_precision`) |
| Persistencia frontend | SQLite |

---

## Configuración

Editar `Final_product/configs/config.json`:

```json
{
    "content_path": "Final_product/content/",
    "databases": "Final_product/database/",
    "embedding_model": "paraphrase-multilingual-mpnet-base-v2",
    "database_type": "faiss",

    "summary_model_name": "gpt-4o-mini-2024-07-18",
    "summary_model_type": "openai",
    "summary_api_key": "YOUR_API_KEY",

    "classifier_model_name": "gpt-4o-mini-2024-07-18",
    "classifier_model_type": "openai",
    "classifier_api_key": "YOUR_API_KEY",
    "classifier_temperature": 0.3,

    "answer_model_name": "gpt-4o-mini-2024-07-18",
    "answer_model_type": "openai",
    "answer_api_key": "YOUR_API_KEY",
    "answer_temperature": 0.3
}
```

Los campos `model_type` aceptan: `"openai"`, `"together"`, `"huggingface"`.

La estructura de directorios de contenido y base de datos **debe** respetar:

```
<path>/
├── teoria/
├── info/
└── practica/
```

El sistema valida esta estructura en el arranque y lanza `ValueError` si no la encuentra.

---

## Puesta en marcha

### Backend

```bash
cd Final_product
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 1. Indexar documentos (primera vez o al actualizar contenido)
python main.py --update

# 2. Arrancar el servidor de inferencia
python main.py
# Escucha en http://127.0.0.1:8000
```

Endpoints disponibles:

```
POST /tfm/service/getAnswer
     Body: { "messages": [{"role": "user", "content": "..."}, ...] }

POST /tfm/service/replaceContent
```

### Frontend

```bash
cd Front_end
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run main.py
```

Por defecto apunta a `http://localhost:8000/tfm/service/getAnswer`. Para cambiar el endpoint:

```bash
export RAG_API_URL=http://<host>:<port>/tfm/service/getAnswer
```

---

## Evaluación

El directorio `PlayGround - Tests/` contiene el pipeline de evaluación con RAGAS. Las métricas recogidas son:

- **Faithfulness** — coherencia factual de la respuesta con el contexto recuperado.
- **Answer correctness** — similitud semántica con la respuesta de referencia.
- **Answer relevancy** — relevancia de la respuesta respecto a la pregunta.
- **Context recall** — cobertura del contexto recuperado sobre la respuesta ideal.
- **Context precision** — precisión del contexto recuperado (señal/ruido).

Los resultados de los benchmarks (tiempos, métricas por modelo y base de datos) se encuentran en `PlayGround - Tests/Metrics/` y las gráficas comparativas en `Data Analisis/`.

---

## Licencia

Ver [license.txt](license.txt).

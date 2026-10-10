"""Genera los informes a partir del código, las mediciones y las capturas locales."""
import json
import os
from pathlib import Path
import re
from urllib.parse import quote, unquote

ROOT = Path(__file__).resolve().parents[1]
P1 = ROOT/'rag-chunking-embeddings-vectordb/rag-chunking-embeddings-vectordb'
P2 = ROOT/'rag-knowledge-pipeline (1)/rag-knowledge-pipeline'


def source_ref(project, file, first, last=None):
    lines = (project/file).read_text(encoding='utf-8-sig').splitlines()
    if isinstance(first,str):
        first = next(i for i,line in enumerate(lines,1) if first in line)
    if isinstance(last,str):
        last = next(i for i,line in enumerate(lines,1) if i>=first and last in line)
    last = min(last or first,len(lines))
    assert 1<=first<=last<=len(lines), (file,first,last,len(lines))
    span = f'línea {first}' if first==last else f'líneas {first}–{last}'
    target = quote('../'+file.replace('\\','/'),safe='/')
    return f'[{file}]({target}), {span}'


def number(value, decimals=2):
    return f'{value:,.{decimals}f}'.replace(',','X').replace('.',',').replace('X','.')


def setup(project, n):
    folder = str(project.relative_to(ROOT)).replace('/','\\')
    return f'''### 4.1. Entorno de trabajo en Visual Studio Code

El directorio de trabajo es `C:\\Users\\Usuario\\Desktop\\TrabFin ModII`. En Visual Studio Code se debe seleccionar **Archivo > Abrir carpeta** y abrir este directorio. El proyecto de este informe se encuentra en `{folder}`. La carpeta exterior contiene la carpeta interna del proyecto; los comandos deben ejecutarse en la carpeta interna, donde está el archivo de configuración.

Los archivos se modificaron y las aplicaciones se ejecutaron mediante herramientas de archivos y PowerShell. Esta sección documenta cómo revisar y reproducir ese trabajo en Visual Studio Code. Las imágenes del código son vistas documentales de archivos reales; no se presentan como capturas nativas del editor. Las imágenes de la aplicación sí corresponden a su ejecución real en un navegador de prueba.

Para revisar el código, abrir el archivo desde el panel **Explorador**. Usar **Ctrl+G** para ir a la línea indicada en cada evidencia. Para ejecutar los comandos, abrir **Terminal > Nueva terminal**. Para revisar este informe con sus imágenes, abrir `Docs/Informe.md` y usar **Ctrl+Shift+V**.

El equipo tenía Python 3.14. Se instaló Python 3.12.15 en `.runtime`, dentro del directorio de trabajo, para usar una versión compatible con las dependencias. Cada proyecto tiene su propio entorno `.venv`. Desde la raíz del trabajo, la instalación realizada se puede reproducir con:

```powershell
python -m pip install --target .tools uv
$env:UV_PYTHON_INSTALL_DIR = Join-Path $PWD '.runtime'
$env:UV_CACHE_DIR = Join-Path $PWD '.cache/uv'
& '.tools/bin/uv.exe' python install 3.12
& '.tools/bin/uv.exe' venv --python '.runtime/cpython-3.12.15-windows-x86_64-none/python.exe' '{folder}/.venv'
& '.tools/bin/uv.exe' pip install --python '{folder}/.venv/Scripts/python.exe' -r '{folder}/requirements-lock.txt'
```

`uv` es la herramienta utilizada para instalar Python y las bibliotecas. `requirements.txt` establece las dependencias admitidas. `requirements-lock.txt` registra las versiones instaladas. La primera instalación necesita conexión a Internet.

En Visual Studio Code, abrir **Ctrl+Shift+P > Python: Select Interpreter** y seleccionar el archivo `.venv\\Scripts\\python.exe` de este proyecto. Esta opción requiere la extensión Python del editor. Si la extensión no está disponible, los comandos siguientes siguen indicando de forma expresa el archivo de Python que deben utilizar.

Antes de ejecutar las consultas, ubicar la terminal en la carpeta del proyecto y definir la ubicación del modelo descargado:

```powershell
Set-Location 'C:\\Users\\Usuario\\Desktop\\TrabFin ModII\\{folder}'
$env:HF_HOME = 'C:\\Users\\Usuario\\Desktop\\TrabFin ModII\\.cache\\huggingface'
$env:HF_HUB_OFFLINE = '1'
$env:PYTHONUTF8 = '1'
```

El modo sin conexión indicado funciona porque el modelo ya fue descargado. Para una primera descarga se debe quitar esa variable con `Remove-Item Env:HF_HUB_OFFLINE -ErrorAction SilentlyContinue`. Esta instrucción elimina la variable de la terminal, no archivos del proyecto.

Las bibliotecas principales instaladas fueron Sentence Transformers 6.1.0, PyTorch 2.14.1, Chroma 1.5.9 y Streamlit 1.65.0. Las versiones exactas y las demás dependencias están en [requirements-lock.txt](../requirements-lock.txt).
'''


def screenshot_section(project,n):
    manifest = json.loads((project/'Docs/capturas/manifest.json').read_text(encoding='utf-8'))
    descriptions1 = {
      '01_manual': ('Abrir el manual en el Explorador de Visual Studio Code y comprobar su título y contenido.', 'El documento reúne información de las turbinas SGT-800 y SST-400. La carpeta de ingesta contiene el manual; el ejemplo sobre RAG se conserva en `data/ejemplos`, fuera de esa carpeta.', 'src/utils.py',16,41),
      '02_dependencias': ('Abrir `requirements.txt` y revisar cada grupo de bibliotecas.', 'Se observa la separación entre lectura de documentos, división del texto, creación de vectores, almacenamiento y aplicación web. Streamlit fue añadido para disponer de una interfaz de consulta.', 'requirements.txt',1,29),
      '03_configuracion': ('Abrir `config.py` y usar Ctrl+G para revisar las rutas y los valores de trabajo.', 'La configuración selecciona el modelo multilingüe, la colección del manual y los tamaños de fragmentación. Los comentarios sobre BGE describen una alternativa del material original; el valor ejecutado está en la asignación `EMBEDDING_MODEL`.', 'config.py',18,64),
      '04_fragmentacion': ('Abrir `src/chunking.py` en la función `recursive_character_split`.', 'El código multiplica por cuatro el tamaño aproximado en tokens para trabajar con caracteres. Se prueban separadores de párrafo, línea, oración y palabra. Cada fragmento conserva su fuente, estrategia y posición.', 'src/chunking.py',32,63),
      '05_embeddings': ('Abrir `src/embeddings.py` y revisar la creación de `SentenceTransformer` y la llamada `encode`.', 'El modelo se carga en CPU y genera vectores normalizados. Los vectores del manual y de la pregunta usan el mismo modelo. La dimensión observada fue de 384 valores por vector.', 'src/embeddings.py',21,62),
      '06_ingesta': ('Ejecutar `.venv\\Scripts\\python.exe -m src.ingest --reset` en la terminal del proyecto.', 'La evidencia muestra un documento leído, el modelo cargado y 58 fragmentos almacenados. Para esta comprobación se utilizó una base separada en `Docs/evidencias/base_validacion`, por lo que no se reemplazó la base de la aplicación abierta.', 'src/ingest.py',44,86),
      '07_consulta_terminal': ('Ejecutar `.venv\\Scripts\\python.exe -m src.query "¿Cuántos días duran las inspecciones A, B y C de las SGT-800?" --top-k 5`.', 'Se muestran cinco fragmentos, su similitud y el archivo de origen. La salida es texto recuperado del manual; el programa no crea una respuesta con un modelo generativo.', 'src/query.py',37,58),
      '08_aplicacion_inicio': ('Abrir `http://127.0.0.1:8501` con el servidor iniciado.', 'La pantalla contiene el número de fragmentos indexados, el control de cantidad, las preguntas sugeridas, el campo de pregunta y el botón Buscar. El número mostrado corresponde a la base activa.', 'app.py',6,24),
      '09_busqueda_inspecciones': ('Seleccionar la pregunta sobre inspecciones A, B y C y pulsar Buscar.', 'La aplicación presenta los fragmentos recuperados, el nombre del manual y los valores de similitud. Los tiempos de referencia que deben verificarse en el manual son 3, 26 y 31 días.', 'app.py',26,35),
      '10_busqueda_contratos': ('Escribir la pregunta sobre Offshore y Onshore en el campo Pregunta y pulsar Buscar.', 'Los resultados permiten revisar el suministro de partes y soporte del contrato Offshore, y la mano de obra calificada del contrato Onshore. La consulta cambia; los vectores de los documentos permanecen almacenados.', 'app.py',26,35),
      '11_busqueda_confiabilidad': ('Escribir la pregunta sobre el 96,89 % y pulsar Buscar.', 'La aplicación recupera el indicador y las aclaraciones del manual. El documento no aporta período, población de equipos, fuente de datos ni fórmula de cálculo; esos datos no deben deducirse del porcentaje.', 'app.py',26,35),
      '12_consumo_modelos': ('Abrir `Docs/evidencias/consumo_resumen.json` en Visual Studio Code.', 'La evidencia registra tiempos, memoria del proceso Python, tamaño de los vectores y cantidad de fragmentos. Los valores pertenecen a una ejecución concreta; no son límites garantizados para otros equipos.', 'src/embeddings.py',22,49),
    }
    descriptions2 = {
      '01_manual': ('Abrir el manual de `data/raw` en Visual Studio Code.', 'El documento es la fuente aplicada de conocimiento. La consulta utiliza fragmentos de este archivo y no una base de ejemplos de reembolsos o soporte técnico.', 'ingestion/extractors.py',70,81),
      '02_configuracion': ('Abrir `config/settings.py` y revisar las rutas, los pesos de búsqueda y los modelos.', 'Se observan 500 caracteres por fragmento, 80 de solapamiento, cuatro resultados por defecto, pesos de 0,6 y 0,4, y el modelo `llama3.2:3b`. La configuración permite cambiar estos valores mediante variables del entorno.', 'config/settings.py',16,57),
      '03_ingestion_codigo': ('Abrir `ingestion/pipeline.py` en `run_pipeline`.', 'La función registra cuatro etapas: extracción, limpieza, fragmentación y almacenamiento de vectores. El resumen final permite comprobar cuántos archivos y fragmentos fueron procesados.', 'ingestion/pipeline.py',26,63),
      '04_fragmentacion': ('Abrir `rag/chunking.py` y revisar `split_text` y `_add_overlap`.', 'El programa divide el texto limpio y añade parte del fragmento anterior al siguiente. Los 500 caracteres son el tamaño previo a añadir hasta 80 caracteres de solapamiento y un espacio.', 'rag/chunking.py',66,106),
      '05_recuperacion': ('Abrir `rag/retriever.py` en `hybrid_search` y `search`.', 'La recuperación combina semejanza de vectores y coincidencia de palabras. En preguntas con HGP, MO o RMI, se realiza una búsqueda adicional para incluir la definición sin retirar los principales hitos de la consulta original.', 'rag/retriever.py',84,116),
      '06_generacion': ('Abrir `rag/generator.py` en `generate_answer`.', 'La aplicación crea un cliente Ollama local, envía instrucciones y contexto, y recibe el texto de la respuesta. Las reglas contienen las definiciones del manual, separan EOH de EOC y establecen un máximo de 300 tokens de salida.', 'rag/generator.py',21,50),
      '07_ingesta': ('Ejecutar `.venv\\Scripts\\python.exe cli.py ingest --reset` desde la terminal del proyecto.', 'La comprobación procesó un archivo, obtuvo un documento limpio y guardó 57 fragmentos. Se utilizó `Docs/evidencias/base_validacion` como base separada para conservar la aplicación abierta.', 'ingestion/pipeline.py',26,63),
      '08_aplicacion_inicio': ('Abrir `http://127.0.0.1:8502` con Ollama y Streamlit en ejecución.', 'El panel lateral muestra 57 fragmentos, el modelo de vectores, el modelo de generación y los controles de recuperación. La parte central permite elegir una pregunta sugerida o escribir una nueva.', 'app/streamlit_app.py',22,68),
      '09_respuesta_inspecciones': ('Pulsar Consultar pregunta sugerida para la pregunta sobre inspecciones.', 'La aplicación recupera información, prepara el contexto y genera una respuesta. La captura se toma después de recibir el texto final. Los valores deben revisarse contra el manual, que indica 3, 26 y 31 días.', 'app/streamlit_app.py',70,107),
      '10_fuentes_recuperadas': ('Abrir el panel de fragmentos recuperados debajo de la pregunta.', 'El panel muestra el nombre del manual, el puntaje de cada fragmento y una vista de su texto. La interfaz limita esa vista a 400 caracteres; el contexto enviado al generador utiliza el fragmento completo.', 'app/streamlit_app.py',87,94),
      '11_respuesta_hgp': ('Escribir la pregunta sobre HGP, EOH y EOC en el campo de chat y enviar con Enter.', 'La definición que debe respetarse es Hot Gas Path Inspection. Los hitos HGP del manual son 30.000 EOH/500 EOC y 90.000 EOH/1.500 EOC. La evidencia permite comprobar si la respuesta cubre toda la pregunta.', 'rag/retriever.py',104,116),
      '12_consumo_modelos': ('Abrir `Docs/evidencias/consumo_resumen.json`.', 'El archivo reúne tiempo de recuperación y generación, memoria de Python, tokens de entrada y salida informados por Ollama y comparación de contexto. Las duraciones originales de Ollama están en nanosegundos.', 'rag/generator.py',24,44),
      '13_pruebas': ('Ejecutar `.venv\\Scripts\\python.exe -m pytest -q` en la terminal del proyecto.', 'El resultado registrado fue de 26 pruebas aprobadas. Estas pruebas usan vectores de prueba para revisar la lógica sin descargar modelos; la ejecución real de los modelos se comprobó por separado.', 'tests/conftest.py',32,49),
      '14_contexto': ('Abrir `rag/augmentation.py` y revisar `format_context` y `build_prompt`.', 'Se construyen tres partes: instrucciones, contexto recuperado y pregunta. Cada fragmento incluye su fuente y un número para facilitar la revisión de las afirmaciones de la respuesta.', 'rag/augmentation.py',11,46),
    }
    info = descriptions1 if n==1 else descriptions2
    result = ['### 4.8. Registro detallado de capturas\n',
              f'Se registran **{len(manifest)} capturas** de este proyecto. Cada imagen tiene su archivo PNG, su origen y una referencia verificable al código. Las vistas documentales se obtuvieron leyendo los archivos reales y abriendo una vista HTML local. Las capturas de aplicación proceden de Chromium en una sesión aislada de prueba. No se usaron imágenes generadas por IA.\n',
              'Para repetir una captura del código en Visual Studio Code, abrir el archivo indicado, ir a la línea con Ctrl+G y capturar el área del editor con Herramienta Recortes. Para repetir una captura de aplicación, realizar la acción descrita en el navegador y capturar la pantalla después de terminar la consulta. Las imágenes ya registradas están en `Docs/capturas` de este proyecto.\n']
    for i,m in enumerate(sorted(manifest,key=lambda x:x['archivo']),1):
        key=Path(m['archivo']).stem
        action, explanation, code, start,end = info[key]
        ref=source_ref(project,code,start,end)
        result += [f'#### Captura {i:02d}. {m["titulo"]}\n',
                   f'**Acción para obtenerla:** {action}\n',
                   f'**Origen registrado:** `{m["origen"]}`. **Ruta de la imagen:** `Docs/capturas/{m["archivo"]}`.\n',
                   f'**Código relacionado:** {ref}.\n']
        if m['tipo']!='aplicacion_real':
            result.append(f'**Vista utilizada para la captura:** [capturas/{key}.html](capturas/{key}.html). El archivo de origen se muestra desde la línea {m["linea_inicio"]} hasta la {m["linea_fin"]}.\n')
        result += [f'**Explicación de la evidencia:** {explanation}\n',f'![{m["titulo"]}](capturas/{m["archivo"]})\n']
    result.append('El archivo [manifest.json](capturas/manifest.json) registra el origen, el tipo de imagen y las líneas de cada captura.\n')
    return '\n'.join(result)


def consumption(project,n,data):
    rows=[('Modelo de vectores',data['modelo_embeddings']),('Dimensión de cada vector',str(data['dimension_vector'])),
          ('Carga del modelo y sus bibliotecas',number(data['segundos_carga_embeddings'])+' s'),
          ('Memoria de Python con el modelo cargado',number(data['ram_python_modelo_cargado_mb'],1)+' MiB'),
          ('Memoria máxima de Python durante la medición',number(data['ram_python_maxima_mb'],1)+' MiB'),
          ('Fragmentos de la base activa',str(data['fragmentos_base_activa'])),('Fragmentos de la consulta medida',str(data['fragmentos_recuperados']))]
    if n==1:
        rows += [('Consulta con el modelo ya cargado',number(data['segundos_consulta'],3)+' s'),('Modelo generativo','No se utiliza')]
    else:
        raw=data['ollama']
        rows += [('Recuperación con el modelo ya cargado',number(data['segundos_recuperacion'],3)+' s'),
                 ('Modelo generativo',data['modelo_generacion']),('Tiempo de la llamada de generación',number(data['segundos_generacion'])+' s'),
                 ('Tokens de entrada informados por Ollama',str(raw['prompt_eval_count'])),('Tokens generados informados por Ollama',str(raw['eval_count'])),
                 ('Velocidad durante la generación de tokens',number(raw['tokens_salida_por_segundo'])+' tokens/s'),
                 ('Límite configurado de salida',str(data['limite_tokens_salida'])+' tokens'),('Temperatura',str(data['temperatura']))]
        model=data['ollama_modelos_cargados']['models'][0]
        rows += [('Tamaño del modelo cargado informado por Ollama',number(model['size']/1024**3)+' GiB'),
                 ('Memoria GPU informada por Ollama',str(model['size_vram'])+' bytes'),('Ventana de contexto informada por Ollama',str(model['context_length'])+' tokens')]
    table='| Medida | Resultado registrado |\n|---|---|\n'+'\n'.join(f'| {label} | {value} |' for label,value in rows)
    text=f'''### 4.6. Consumo de los modelos de IA

Los modelos se ejecutan localmente. El modelo de vectores se descarga una vez desde Hugging Face y se reutiliza desde `.cache/huggingface`. La consulta y la ingesta consumen tiempo de CPU, memoria RAM y espacio en disco. En esta ejecución no se usó una API de pago ni se enviaron preguntas a un servicio externo de generación.

La medición se realizó el **10 de octubre de 2026**, con horario de Bolivia. Se utilizó la pregunta «¿Qué significa HGP y en qué hitos EOH y EOC está previsto?». Los tiempos corresponden al estado del equipo en esa ejecución. La carga del modelo incluye la importación de sus bibliotecas. La memoria indicada corresponde al proceso Python completo, no solamente a los pesos del modelo.

{table}

La suma del tamaño de los archivos de la caché de Hugging Face fue de **{number(data['pesos_embeddings_disco_mb'],1)} MiB**. Esta cifra corresponde a los archivos guardados en la caché, incluidos los archivos de configuración; no mide solamente los pesos ni todo el espacio ocupado por Python y sus dependencias. Las dimensiones y tiempos se registraron sin modificar el código de los modelos ni entrenarlos con el manual.

El registro completo está en [consumo_modelos.json](evidencias/consumo_modelos.json) y su selección de campos en [consumo_resumen.json](evidencias/consumo_resumen.json). La medición se puede repetir desde la carpeta del proyecto con:

```powershell
& '.venv/Scripts/python.exe' -u '../../Docs/medir_ejecucion.py' {n}
```

El archivo de medición se encuentra en [Docs/medir_ejecucion.py](../../../Docs/medir_ejecucion.py), dentro del directorio general del trabajo. Usa una base de validación separada para registrar la ingesta.
'''
    if n==1:
        text+='\nEl modelo transforma el texto en números. No redacta respuestas de chat. Esta implementación no registra un contador de tokens de entrada ni produce tokens de salida de una respuesta de chat. Cambiar el tamaño de los fragmentos modifica la cantidad de vectores y el trabajo necesario para crearlos.\n'
    else:
        raw=data['ollama']
        cmp=data['comparacion_tokens']
        text+=f'''\nOllama entrega el número real de tokens procesados y generados por su modelo. El límite de 300 tokens es un máximo configurado, no una cantidad consumida en todas las respuestas. En la consulta medida se generaron {raw['eval_count']} tokens. Las duraciones originales se expresan en nanosegundos; para obtener segundos se dividen entre 1.000.000.000.

La velocidad de {number(raw['tokens_salida_por_segundo'])} tokens por segundo se calcula solamente durante la producción de tokens. No incluye todo el tiempo de carga ni de lectura del contexto. La memoria del proceso Python no incluye la memoria del proceso que ejecuta el modelo dentro de Ollama. La API de Ollama informó un modelo cargado de {number(data['ollama_modelos_cargados']['models'][0]['size']/1024**3)} GiB y cero bytes de memoria GPU.

Para la pregunta sobre WAR42 en 2027, el comando `compare` registró {cmp['tokens_prompt_rag']} tokens en el contexto RAG frente a {cmp['tokens_prompt_contexto_largo']} al reunir todos los fragmentos almacenados. El ahorro calculado fue de {number(cmp['ahorro_de_tokens_pct'],1)} %. Este conteo usa `tiktoken` con `cl100k_base` como referencia; no es el contador de Llama. El contexto largo se construye con todos los fragmentos, incluidos sus solapamientos, y no con una copia única del documento original. Por ello, la comparación describe esta implementación y no una reducción garantizada del tiempo de respuesta.
'''
    return text


def report1():
    p=P1
    data=json.loads((p/'Docs/evidencias/consumo_modelos.json').read_text(encoding='utf-8'))
    r=lambda f,a,b=None:source_ref(p,f,a,b)
    text='''# Informe del proyecto de fragmentación, embeddings y base vectorial

**Proyecto:** `rag-chunking-embeddings-vectordb`  
**Fuente aplicada:** Manual del Programa de Mantenimiento Preventivo de turbinas SGT-800 y SST-400  
**Fecha de documentación:** 10 de octubre de 2026  
**Entorno:** Windows, Python 3.12.15 y ejecución local en CPU

## 1. Introducción

El proyecto organiza el contenido del Manual del Programa de Mantenimiento Preventivo para permitir su consulta mediante preguntas escritas. Lee el documento, lo divide en partes, representa cada parte con números y guarda esas representaciones en una base local. Cuando una persona pregunta, el programa busca las partes del manual que tienen mayor relación con esa pregunta.

La aplicación muestra fragmentos y su fuente. Su alcance termina en la recuperación de información: no utiliza un modelo de lenguaje para redactar una respuesta nueva. Esta diferencia permite revisar directamente el texto del manual antes de interpretar sus datos.

La adaptación realizada utiliza el manual como fuente activa, cambia la configuración del modelo de vectores, crea una colección específica y añade una aplicación web con preguntas sobre mantenimiento. Este informe explica el funcionamiento y presenta evidencia de la ejecución.

## 2. Objetivos

### 2.1. Objetivo general

Implementar y documentar una aplicación local que recupere información del manual de mantenimiento preventivo mediante la búsqueda de fragmentos relacionados con una pregunta.

### 2.2. Objetivos específicos

1. Preparar un entorno de Python separado para el proyecto.
2. Leer el manual y conservar el archivo de origen de cada fragmento.
3. Dividir el contenido con un tamaño y un solapamiento definidos.
4. Crear vectores mediante un modelo multilingüe ejecutado localmente.
5. Guardar los vectores en Chroma y consultar la colección del manual.
6. Presentar los resultados en una aplicación web y en la terminal.
7. Registrar capturas, resultados y consumo medido del modelo.

## 3. Marco Teórico

### 3.1. Ingesta de documentos

La ingesta es la lectura y preparación de archivos para su uso en la aplicación. En este proyecto se admiten archivos de texto, Markdown y PDF. Markdown es un formato de texto que permite escribir títulos, listas y tablas. El manual utilizado está en ese formato.

### 3.2. Fragmentación del texto

La fragmentación, denominada *chunking* en el código, consiste en dividir un documento en partes. El solapamiento repite una porción del texto anterior en el fragmento siguiente. Su propósito es conservar información que podría quedar separada en un corte.

La estrategia principal prueba separadores de párrafo, línea, oración y palabra. También existen funciones para separar por cambios de tema y para guardar fragmentos pequeños con un texto mayor relacionado. La ejecución documentada utiliza la estrategia principal, llamada `recursive`.

### 3.3. Embeddings o vectores de texto

Un embedding es una lista de números calculada por un modelo a partir del texto. Estos números permiten comparar preguntas y fragmentos. El modelo utilizado es multilingüe y puede procesar el contenido en español. En esta ejecución cada vector tiene 384 valores. La normalización ajusta la longitud numérica del vector para facilitar su comparación con otros vectores.

Los documentos y las preguntas deben utilizar el mismo modelo. Si se cambia el modelo, se debe volver a crear la base. El manual se utiliza como contenido de consulta; no se realizó entrenamiento del modelo con sus datos.

### 3.4. Base vectorial y similitud

Chroma almacena los vectores, el texto y datos de origen. En este caso conserva los datos en archivos locales para reutilizarlos después de cerrar la aplicación. La comparación utiliza la distancia de coseno; el código muestra la similitud como uno menos esa distancia.

El valor de similitud sirve para ordenar resultados. No representa la probabilidad de que una afirmación sea correcta. El parámetro `top_k` indica cuántos fragmentos se devuelven.

### 3.5. Relación con RAG

RAG es una forma de preparar respuestas mediante recuperación de información y generación de texto. Este proyecto implementa la lectura, fragmentación, creación de vectores, almacenamiento y recuperación. La generación se realiza en el otro proyecto, denominado `rag-knowledge-pipeline`.

## 4. Implementación Aplicada
'''+setup(p,1)
    text+=f'''
### 4.2. Organización y cambios realizados

| Archivo o carpeta | Función aplicada |
|---|---|
| `data/documentos/` | Contiene el manual usado por la ingesta. |
| `data/ejemplos/` | Conserva el ejemplo sobre RAG fuera de la fuente activa. |
| `config.py` | Define rutas, modelo, colección, tamaños y cantidad de resultados. |
| `src/utils.py` | Lee los documentos y registra su fuente. |
| `src/chunking.py` | Implementa las tres estrategias de división del texto. |
| `src/embeddings.py` | Carga el modelo y obtiene vectores normalizados. |
| `src/vector_store.py` | Guarda y consulta los fragmentos en Chroma. |
| `src/ingest.py` | Ejecuta la ingesta completa desde la terminal. |
| `src/query.py` | Recupera fragmentos para una pregunta. |
| `app.py` | Presenta el buscador web. |
| `consultas_manual.py` | Ejecuta las ocho preguntas y guarda resultados. |

La colección se cambió a `manual_mantenimiento_preventivo`. El modelo activo se cambió de la opción original BGE a `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`. Se añadieron Streamlit y `app.py`, las preguntas aplicadas al mantenimiento, los accesos de ejecución y el registro de resultados. Referencias: {r('config.py',18,46)} y {r('app.py',1,35)}.

El tamaño configurado es 128 tokens aproximados y el solapamiento 25. La función multiplica esos valores por cuatro: trabaja con 512 caracteres y 100 caracteres de solapamiento. Este cálculo no cuenta tokens exactos del modelo. Referencia: {r('src/chunking.py',43,56)}.

### 4.3. Funcionamiento paso a paso

1. **Leer la carpeta de documentos.** `load_documents` busca archivos admitidos y lee su contenido. Para cada documento guarda el texto y la ruta de origen. Referencia: {r('src/utils.py',16,47)}.
2. **Cargar el modelo.** `EmbeddingModel` crea una instancia de Sentence Transformer en CPU. La primera ejecución descarga el modelo; las siguientes usan la caché local. Referencia: {r('src/embeddings.py',22,37)}.
3. **Dividir el manual.** La estrategia `recursive` genera fragmentos con separadores de texto y conserva la fuente, el nombre de la estrategia y un índice. Referencia: {r('src/chunking.py',32,63)}.
4. **Calcular los vectores.** `embed_texts` envía los fragmentos al modelo y normaliza los vectores obtenidos. Referencia: {r('src/embeddings.py',39,49)}.
5. **Guardar los datos.** `add_chunks` asigna identificadores y almacena textos, vectores y datos de origen en Chroma. Referencia: {r('src/vector_store.py',36,55)}.
6. **Recibir una pregunta.** La terminal o la aplicación web obtiene el texto escrito por la persona. Referencia: {r('src/query.py',29,34)} y {r('app.py',24,26)}.
7. **Convertir la pregunta en un vector.** `embed_query` aplica el mismo modelo utilizado para el manual. Referencia: {r('src/embeddings.py',51,62)}.
8. **Buscar los resultados.** Chroma compara el vector de la pregunta con los almacenados y devuelve la cantidad solicitada. Referencia: {r('src/vector_store.py',68,100)}.
9. **Mostrar texto y fuente.** La aplicación presenta los fragmentos completos, la fuente y su similitud. La terminal muestra una vista de los primeros 300 caracteres de cada fragmento. Referencia: {r('app.py',30,35)} y {r('src/query.py',48,58)}.

El código también contiene `semantic_split`, que compara oraciones para detectar cambios de tema, y `parent_child_split`, que conserva un texto mayor junto a fragmentos pequeños. Son opciones disponibles en la ingesta; no fueron las estrategias utilizadas en las capturas ni en la medición de este informe. Sus tamaños deben revisarse antes de usarlas con el modelo activo.

### 4.4. Ejecución en la terminal de Visual Studio Code

Con la terminal situada en la carpeta interna del proyecto, crear o reemplazar la colección del manual:

```powershell
& '.venv/Scripts/python.exe' -m src.ingest --reset
```

El argumento `--reset` reemplaza el contenido de la colección seleccionada. Para documentar una ejecución sin cambiar la aplicación activa se puede usar una base separada:

```powershell
$env:PERSIST_DIR = Join-Path $PWD 'Docs/evidencias/base_validacion'
& '.venv/Scripts/python.exe' -m src.ingest --reset
& '.venv/Scripts/python.exe' -m src.query '¿Cuántos días duran las inspecciones A, B y C de las SGT-800?' --top-k 5
Remove-Item Env:PERSIST_DIR
```

La última instrucción quita la variable de la terminal. La base de validación permanece guardada. La evidencia de ingesta está en [ingesta.txt](evidencias/ingesta.txt) y la consulta en [consulta.txt](evidencias/consulta.txt).

Para repetir las ocho preguntas, ejecutar:

```powershell
& '.venv/Scripts/python.exe' consultas_manual.py
```

El archivo de preguntas común está en [preguntas_manual.json](../../../preguntas_manual.json). Los resultados se guardan en [resultados/proyecto_1_consultas.json](../../../resultados/proyecto_1_consultas.json), dentro del directorio general del trabajo. Referencia: {r('consultas_manual.py',1,23)}.

### 4.5. Ejecución y uso de la aplicación web

Desde la carpeta del proyecto:

```powershell
& '.venv/Scripts/python.exe' -m streamlit run app.py --server.port 8501 --server.address 127.0.0.1 --browser.gatherUsageStats false
```

También existe el acceso [ejecutar-proyecto-1.ps1](../../../ejecutar-proyecto-1.ps1) en la raíz del trabajo. Al iniciar el servidor se debe abrir `http://127.0.0.1:8501`. Si ya está ejecutándose en ese puerto, se utiliza la instancia abierta.

La persona selecciona una pregunta sugerida o escribe otra, elige la cantidad de fragmentos y pulsa **Buscar**. La aplicación carga el modelo y la base una vez por proceso mediante `st.cache_resource`. Después reutiliza esos recursos en las consultas. Para cerrar una instancia iniciada en la terminal, pulsar Ctrl+C en esa terminal.
'''
    text+=consumption(p,1,data)
    text+='''
### 4.7. Resultados de la implementación

La ingesta de comprobación procesó un documento y almacenó 58 fragmentos con vectores reales. La consulta de terminal devolvió cinco resultados con el archivo de origen. La aplicación web permitió consultar inspecciones, contratos y confiabilidad. El registro de ocho preguntas realizado previamente se conserva en la carpeta general `resultados`.

Se verificó el funcionamiento de la aplicación mediante una prueba de carga y búsqueda con Streamlit AppTest y mediante las capturas actuales del navegador. Este proyecto no tiene una suite propia de 26 pruebas; esa suite corresponde al segundo proyecto. La calidad de la recuperación debe evaluarse revisando el conjunto de resultados, no solamente el primer fragmento.

Entre las respuestas documentales contrastadas se encuentran: inspecciones A, B y C con 3, 26 y 31 días de referencia; revisión parcial SST-400 a 25.000 EOH; revisión total a 50.000 EOH; y confiabilidad informada de 96,89 %, sin fórmula de cálculo visible.
'''
    text+=screenshot_section(p,1)
    text+='''
## 5. Conclusiones

El proyecto cumple la función de leer el manual, dividirlo, crear vectores y recuperar partes relacionadas con una pregunta. La configuración aplicada conserva la fuente de cada resultado y permite ejecutar las consultas de manera local.

La ingesta comprobada generó 58 fragmentos y la búsqueda devolvió texto del manual con sus datos de origen. El modelo multilingüe permitió comparar preguntas en español con el contenido del documento. La memoria medida corresponde al proceso completo y confirma que la ejecución local requiere recursos del equipo.

La aplicación facilita la revisión documental, pero no redacta respuestas nuevas ni valida por sí sola una decisión de mantenimiento. La similitud organiza la búsqueda y debe acompañarse de la lectura de los fragmentos y del manual vigente.

## 6. Recomendaciones

1. Mantener una versión identificada del manual y reconstruir la colección cuando cambie su contenido.
2. Revisar las rutas y seleccionar el entorno `.venv` de este proyecto en Visual Studio Code.
3. Medir tokens con el método del modelo antes de cambiar los tamaños de fragmentación; la relación de cuatro caracteres por token es aproximada.
4. Usar una colección separada para comparar estrategias y evitar mezclar vectores de modelos distintos.
5. Revisar varios resultados y confirmar cifras, unidades, fechas y alcances contra el manual.
6. Conservar la caché del modelo, los archivos de versiones y las evidencias para repetir la ejecución.
7. Si se requiere una respuesta redactada, utilizar el sistema RAG del segundo proyecto y revisar sus fuentes.
8. Verificar tiempos y memoria en el equipo de destino; los valores registrados describen una sola ejecución.
'''
    return text


def report2():
    p=P2
    data=json.loads((p/'Docs/evidencias/consumo_modelos.json').read_text(encoding='utf-8'))
    r=lambda f,a,b=None:source_ref(p,f,a,b)
    text='''# Informe del sistema RAG aplicado al mantenimiento preventivo

**Proyecto:** `rag-knowledge-pipeline`  
**Fuente aplicada:** Manual del Programa de Mantenimiento Preventivo de turbinas SGT-800 y SST-400  
**Fecha de documentación:** 10 de octubre de 2026  
**Entorno:** Windows, Python 3.12.15, Chroma y Ollama local

## 1. Introducción

Este proyecto permite formular preguntas sobre el Manual del Programa de Mantenimiento Preventivo y recibir respuestas preparadas con información recuperada de ese documento. Primero lee y limpia el texto, después lo divide y guarda sus vectores. Para cada pregunta, busca fragmentos relacionados, construye un contexto y lo envía a un modelo de lenguaje ejecutado con Ollama.

La aplicación incluye un chat y un panel de fuentes para revisar el contenido utilizado en la respuesta. Su objetivo es apoyar la consulta documental de inspecciones, contratos, cronogramas y datos de confiabilidad. El manual utilizado no se convierte en un procedimiento operativo nuevo mediante este sistema.

La adaptación realizada reemplaza los ejemplos generales por el manual, ajusta la fragmentación, añade preguntas del mantenimiento y refuerza el tratamiento de siglas y unidades. Este informe documenta los archivos, los pasos de ejecución y el consumo real de los modelos.

## 2. Objetivos

### 2.1. Objetivo general

Implementar y documentar un sistema RAG local que responda preguntas sobre mantenimiento preventivo utilizando información recuperada del manual y fuentes que puedan revisarse.

### 2.2. Objetivos específicos

1. Preparar un entorno de Python propio para el proyecto.
2. Extraer, limpiar y dividir el manual con datos de origen.
3. Generar vectores y guardarlos en una base local.
4. Combinar la búsqueda por significado con la búsqueda por palabras.
5. Construir el contexto e instrucciones para el modelo generativo.
6. Ejecutar la generación mediante Ollama sin una API de pago.
7. Mostrar las respuestas y sus fragmentos de apoyo en un chat.
8. Comprobar las pruebas, los resultados y el consumo de recursos.

## 3. Marco Teórico

### 3.1. Sistema RAG

RAG utiliza información recuperada para preparar una respuesta. En esta implementación, la recuperación selecciona fragmentos; la preparación del contexto añade instrucciones y la pregunta; y la generación produce texto a partir de esos datos. El modelo generativo recibe los fragmentos seleccionados, no consulta directamente la base Chroma.

### 3.2. Extracción, limpieza y fragmentación

La extracción obtiene texto de archivos PDF, HTML o Markdown. La limpieza corrige caracteres, quita marcas de formato, organiza espacios y elimina repeticiones exactas. La fragmentación divide el texto para procesarlo y recuperarlo en partes. Cada fragmento conserva el nombre del archivo, su tipo y la página cuando la fuente es un PDF.

El manual aplicado está en Markdown. Por ello, sus fragmentos no tienen números de página de PDF. Los números de fragmento que aparecen en el contexto son identificadores de la consulta, no números de sección del manual.

### 3.3. Vectores y búsqueda híbrida

El modelo de embeddings convierte texto en listas de 384 números. La comparación por vectores permite encontrar textos relacionados aunque la pregunta no repita todas las palabras del manual. La normalización ajusta la longitud numérica del vector para facilitar esa comparación. La búsqueda por palabras utiliza BM25, un método que da prioridad a términos presentes en los documentos.

La búsqueda híbrida combina ambos puntajes. En este proyecto el peso de la búsqueda por vectores es 0,6 y el de la búsqueda por palabras es 0,4. Los resultados se ordenan por el puntaje combinado. Ese puntaje no equivale a una probabilidad de respuesta correcta.

### 3.4. Recuperación iterativa

El modo llamado Agentic RAG en el código revisa el puntaje promedio de los resultados. Si es menor que el umbral, aumenta la cantidad de fragmentos y repite la búsqueda. Esta implementación permite hasta dos rondas y aumenta `top_k` en dos. No ejecuta órdenes de mantenimiento ni transforma la pregunta mediante otro modelo.

### 3.5. Contexto, tokens y generación local

El contexto es el texto seleccionado para que el modelo pueda responder. Un token es una unidad de texto que el modelo procesa; no siempre corresponde a una palabra completa. Un contexto más largo requiere más trabajo de procesamiento.

Ollama ejecuta el modelo generativo en el equipo. La aplicación utiliza `llama3.2:3b`. La temperatura configurada en cero reduce la variación entre respuestas, pero no garantiza exactitud. El límite de salida es de 300 tokens. Los modelos no se entrenaron ni se ajustaron con el manual.

## 4. Implementación Aplicada
'''+setup(p,2)
    text+=f'''
### 4.2. Organización y cambios realizados

| Archivo o carpeta | Función aplicada |
|---|---|
| `data/raw/` | Contiene el manual utilizado como fuente. |
| `config/settings.py` | Define rutas, fragmentación, búsqueda y modelos. |
| `ingestion/extractors.py` | Extrae texto y datos de origen. |
| `ingestion/cleaners.py` | Corrige y limpia el contenido. |
| `ingestion/pipeline.py` | Ejecuta las cuatro etapas de ingesta. |
| `rag/chunking.py` | Divide el texto limpio y agrega solapamiento. |
| `rag/embeddings.py` | Carga el modelo multilingüe y calcula vectores. |
| `rag/vector_store.py` | Guarda, consulta y enumera fragmentos en Chroma. |
| `rag/retriever.py` | Implementa búsqueda semántica, por palabras, híbrida e iterativa. |
| `rag/augmentation.py` | Construye instrucciones, contexto y pregunta. |
| `rag/generator.py` | Llama al modelo mediante el cliente Ollama. |
| `cli.py` | Proporciona los comandos ingest, ask y compare. |
| `app/streamlit_app.py` | Presenta el chat, configuración y fuentes. |
| `consultas_manual.py` | Ejecuta las ocho preguntas y guarda respuestas y fragmentos. |
| `tests/` | Comprueba limpieza, fragmentación, contexto, base y búsqueda. |

La colección se cambió a `manual_mantenimiento_preventivo`. Las rutas se resolvieron desde el archivo de configuración para no depender del lugar desde el que se abre el editor. Se usa un tamaño de 500 caracteres con 80 de solapamiento. El modelo de generación se fijó en `llama3.2:3b`, con temperatura cero. Referencia: {r('config/settings.py',16,57)}.

Se añadieron las preguntas sugeridas del manual, el registro de consultas, el acceso de ejecución y las instrucciones para responder sobre SGT-800 y SST-400. Se corrigió el uso de `OLLAMA_HOST` creando un cliente explícito con ese valor y un tiempo máximo de espera de 180 segundos. Referencia: {r('rag/generator.py',21,44)}.

En las pruebas se detectó un bloqueo de archivos temporales de la base Chroma en Windows. Se corrigió el cierre del cliente Chroma en la preparación de pruebas. Referencia: {r('tests/conftest.py',40,49)}.

Durante la comprobación se observaron respuestas incorrectas o incompletas al desarrollar HGP. Se añadió un conjunto de definiciones del manual y una búsqueda adicional para incluir la definición junto con los principales datos recuperados por la pregunta original. Las instrucciones del generador también separan EOH de EOC. Estas medidas mejoran el contexto y las reglas, pero la respuesta debe seguir revisándose. Referencia: {r('rag/retriever.py',25,36)}, {r('rag/retriever.py',104,116)} y {r('rag/generator.py',28,42)}.

### 4.3. Funcionamiento paso a paso

1. **Extraer el documento.** `extract_directory` revisa archivos admitidos y aplica el lector correspondiente. Para Markdown se conserva el texto y se simplifican enlaces. Referencia: {r('ingestion/extractors.py',70,108)}.
2. **Limpiar el texto.** `clean_corpus` aplica corrección de caracteres, eliminación de marcas, orden de espacios y eliminación de párrafos repetidos. Referencia: {r('ingestion/cleaners.py',124,143)}.
3. **Dividir el contenido.** `chunk_documents` crea fragmentos con identificadores y datos de origen. La función agrega al siguiente fragmento hasta 80 caracteres del anterior. El tamaño final puede superar los 500 caracteres nominales por ese agregado. Referencia: {r('rag/chunking.py',66,106)}.
4. **Crear los vectores.** `get_embedding_model` carga el modelo una vez y `embed_texts` obtiene vectores normalizados. Referencia: {r('rag/embeddings.py',15,36)}.
5. **Guardar los fragmentos.** Chroma conserva identificador, vector, texto, fuente, página y tipo de documento. Referencia: {r('rag/vector_store.py',23,42)}.
6. **Recibir la pregunta.** La terminal o el chat obtiene la pregunta y la cantidad de resultados. Referencia: {r('cli.py',25,43)} y {r('app/streamlit_app.py',57,73)}.
7. **Recuperar información.** El buscador combina vectores y BM25. Si hay una sigla conocida, recupera también su definición. Si está activo el modo iterativo, revisa la evidencia y puede repetir con más resultados. Referencia: {r('rag/retriever.py',84,156)}.
8. **Preparar el contexto.** Se escriben instrucciones, fragmentos con fuentes y la pregunta. Referencia: {r('rag/augmentation.py',25,46)}.
9. **Generar la respuesta.** El cliente Ollama recibe un mensaje de sistema y el contexto como mensaje de usuario. El modelo devuelve texto, que la aplicación presenta en pantalla. Referencia: {r('rag/generator.py',21,44)}.
10. **Conservar el historial.** El chat guarda las preguntas y respuestas en la sesión del navegador. Los fragmentos aparecen en un panel separado. El historial de la interfaz no sustituye el archivo JSON de las consultas de prueba. Referencia: {r('app/streamlit_app.py',50,55)} y {r('app/streamlit_app.py',87,107)}.

Si Ollama no puede responder, la interfaz muestra un mensaje y fragmentos recuperados. La terminal también dispone del argumento `--no-generate`, que permite consultar y revisar el contexto sin llamar al modelo generativo. Referencia: {r('cli.py',50,64)}.

### 4.4. Ejecución en la terminal de Visual Studio Code

Ollama ya estaba instalado en el equipo. Se descargó el modelo con:

```powershell
ollama pull llama3.2:3b
ollama list
```

Ollama debe estar en ejecución en `http://localhost:11434`. Si no se encuentra activo, se puede iniciar con `ollama serve` en otra terminal. Desde la carpeta interna del proyecto, los comandos principales son:

```powershell
& '.venv/Scripts/python.exe' cli.py ingest --reset
& '.venv/Scripts/python.exe' cli.py ask '¿Qué significa HGP y en qué hitos EOH y EOC está previsto?' --top-k 5
& '.venv/Scripts/python.exe' cli.py ask '¿Qué intervención está prevista para WAR42 en 2027?' --agentic
& '.venv/Scripts/python.exe' cli.py ask '¿Qué incluye el contrato Onshore?' --no-generate
& '.venv/Scripts/python.exe' cli.py compare '¿Qué intervención está prevista para WAR42 en 2027?'
& '.venv/Scripts/python.exe' -m pytest -q
```

El argumento `--reset` reemplaza la colección seleccionada. En la comprobación de este informe se estableció `VECTOR_DB_DIR` en `Docs/evidencias/base_validacion` antes de ejecutar la ingesta. Así se registró una base separada sin reemplazar la de la aplicación abierta. Al quitar esa variable, el programa vuelve a la ruta configurada para la base activa.

Los registros reales están en [ingesta.txt](evidencias/ingesta.txt), [consulta_sin_generacion.txt](evidencias/consulta_sin_generacion.txt) y [pruebas.txt](evidencias/pruebas.txt). Para repetir las ocho preguntas, ejecutar `.venv\\Scripts\\python.exe consultas_manual.py`. La lista está en [preguntas_manual.json](../../../preguntas_manual.json) y los resultados generales en [proyecto_2_respuestas.json](../../../resultados/proyecto_2_respuestas.json).

### 4.5. Ejecución y uso de la aplicación web

Desde la carpeta del proyecto:

```powershell
& '.venv/Scripts/python.exe' -m streamlit run app/streamlit_app.py --server.port 8502 --server.address 127.0.0.1 --browser.gatherUsageStats false
```

El acceso [ejecutar-proyecto-2.ps1](../../../ejecutar-proyecto-2.ps1) de la raíz del trabajo prepara la carpeta y la caché antes de iniciar Streamlit. La aplicación se abre en `http://127.0.0.1:8502`. Si ya hay una instancia abierta en ese puerto, se usa esa instancia.

El panel lateral permite activar o desactivar el modo iterativo y cambiar la cantidad de fragmentos. La persona elige una pregunta sugerida y pulsa **Consultar pregunta sugerida**, o escribe una pregunta en el campo de chat y la envía con Enter. El programa recupera el contexto, genera la respuesta y muestra el texto final. El panel de fuentes permite revisar fragmentos y puntajes.

La base y el buscador se conservan mediante `st.cache_resource`. El modelo de vectores también se guarda en memoria con `lru_cache`. Si se reconstruye la colección mientras la aplicación está abierta, se debe reiniciar la aplicación para actualizar el índice de palabras que el buscador mantiene en memoria.
'''
    text+=consumption(p,2,data)
    text+='''
### 4.7. Resultados y revisión de respuestas

La ingesta actual de comprobación procesó un archivo, obtuvo un documento limpio y almacenó 57 fragmentos. Las 26 pruebas del proyecto finalizaron correctamente. Las pruebas utilizan un generador de vectores de prueba, mientras que la ingesta y las consultas de este informe utilizaron el modelo real descargado.

Las preguntas cubren duraciones A/B/C, alcances Offshore/Onshore, hitos SST-400, HGP, WAR42, colores de cronograma, ensayos NDT y confiabilidad. Las respuestas verificadas directamente con el manual están en [PREGUNTAS_Y_RESPUESTAS_VERIFICADAS.md](../../../resultados/PREGUNTAS_Y_RESPUESTAS_VERIFICADAS.md).

Se comprobó que el modelo puede omitir parte de una pregunta, incluso con contexto disponible. Por ejemplo, una respuesta breve sobre HGP puede incluir su definición y horas, pero no todos los ciclos equivalentes. Los resultados del modelo se conservan como evidencia; las respuestas contrastadas con el manual se presentan por separado. Tener temperatura cero y fuentes recuperadas no elimina la necesidad de revisar el contenido.

La comparación de tokens mostró una reducción del contexto enviado en la consulta de WAR42. Ese resultado se limita al método de conteo y al conjunto de fragmentos de esta implementación; no se realizaron mediciones para afirmar una mejora general del tiempo de generación.
'''
    text+=screenshot_section(p,2)
    text+='''
## 5. Conclusiones

El proyecto implementa la lectura, limpieza, fragmentación, almacenamiento, recuperación y generación de respuestas sobre el manual. La búsqueda híbrida combina información por significado y por palabras, y la aplicación permite revisar los fragmentos utilizados.

La ingesta comprobada produjo 57 fragmentos y las 26 pruebas finalizaron correctamente. La generación local mediante Ollama funcionó con el modelo `llama3.2:3b`, sin una API de pago. La medición mostró que la generación consume más tiempo que la recuperación en la consulta registrada.

Las correcciones de siglas y unidades mejoraron la preparación del contexto. Sin embargo, se observaron respuestas que requieren revisión o que no incluyen todos los datos solicitados. El resultado debe contrastarse con el manual antes de utilizarlo como información de mantenimiento.

## 6. Recomendaciones

1. Mantener el manual vigente e identificar su versión antes de reconstruir la base.
2. Usar el entorno Python del proyecto y conservar `requirements-lock.txt`.
3. Revisar los datos de EOH y EOC, las siglas y las duraciones contra los fragmentos originales.
4. Reiniciar la aplicación después de modificar la base para renovar la búsqueda por palabras.
5. Medir tokens con el método del modelo para ajustar fragmentos y contexto sin perder información.
6. Confirmar que Ollama y el modelo configurado estén disponibles antes de consultar.
7. Mantener el modo `--no-generate` para revisar recuperación y contexto cuando la generación falle o sea incompleta.
8. Conservar registros de preguntas, respuestas, fuentes y consumo para comparar cambios.
9. Revisar manualmente respuestas sobre mantenimiento; los puntajes y la temperatura no prueban su exactitud.
10. Repetir las mediciones en el equipo de uso, porque los tiempos y la memoria dependen del estado del sistema y del modelo cargado.
'''
    return text


def root_copy(text,project):
    oldbase=project/'Docs'
    newbase=ROOT/'Docs'
    def replace(match):
        label,target=match.group(1),match.group(2)
        if '://' in target or target.startswith('#'):
            return match.group(0)
        absolute=(oldbase/unquote(target)).resolve()
        relative=os.path.relpath(absolute,newbase).replace('\\','/')
        return f'[{label}]({quote(relative,safe="/")})'
    return re.sub(r'\[([^\]]*)\]\(([^)]+)\)',replace,text)


if __name__=='__main__':
    for project,filename,content in [(P1,'Informe_chucking_embeddings.md',report1()),(P2,'Informe_rag_pipeline.md',report2())]:
        (project/'Docs/Informe.md').write_text(content,encoding='utf-8')
        (ROOT/'Docs'/filename).write_text(root_copy(content,project),encoding='utf-8')
        print(filename,len(content.split()),'palabras',flush=True)

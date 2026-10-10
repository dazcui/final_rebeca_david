"""Registra ejecuciones reales para los informes, sin cambiar la base activa."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from datetime import datetime, timezone, timedelta

ROOT = Path(__file__).resolve().parents[1]
PROJECTS = {
    1: ROOT / 'rag-chunking-embeddings-vectordb/rag-chunking-embeddings-vectordb',
    2: ROOT / 'rag-knowledge-pipeline (1)/rag-knowledge-pipeline',
}


def main(number):
    project = PROJECTS[number]
    os.chdir(project)
    sys.path.insert(0, str(project))
    sys.path.append(str(ROOT / '.tools/capturas/Lib/site-packages'))
    import psutil
    process = psutil.Process()
    evidence = project / 'Docs/evidencias'
    evidence.mkdir(parents=True, exist_ok=True)
    os.environ['HF_HOME'] = str(ROOT / '.cache/huggingface')
    os.environ['HF_HUB_OFFLINE'] = '1'
    os.environ['PYTHONUTF8'] = '1'
    result = {'fecha': datetime.now(timezone(timedelta(hours=-4))).isoformat(),
              'proyecto': number, 'python': sys.version.split()[0]}
    env = os.environ.copy()
    # Una base separada permite registrar la ingesta sin alterar la aplicación abierta.
    env['PERSIST_DIR' if number == 1 else 'VECTOR_DB_DIR'] = str(evidence / 'base_validacion')
    ingest_command = ['-m', 'src.ingest', '--reset'] if number == 1 else ['cli.py', 'ingest', '--reset']
    commands = [('ingesta', ingest_command)]
    if number == 1:
        commands.append(('consulta', ['-m', 'src.query', '¿Cuántos días duran las inspecciones A, B y C de las SGT-800?', '--top-k', '5']))
    else:
        commands += [('consulta_sin_generacion', ['cli.py', 'ask', '¿Qué significa HGP y en qué hitos EOH y EOC está previsto?', '--no-generate', '--top-k', '5']),
                     ('pruebas', ['-m', 'pytest', '-q'])]
    result['comandos'] = []
    for name, command in commands:
        start = time.perf_counter()
        run = subprocess.run([sys.executable, '-u', *command], env=env, capture_output=True, text=True, encoding='utf-8')
        record = {'comando': [sys.executable, *command], 'segundos': round(time.perf_counter()-start, 3), 'codigo_salida': run.returncode}
        result['comandos'].append(record)
        (evidence / f'{name}.txt').write_text('COMANDO REAL:\n'+' '.join(record['comando'])+'\n\n'+run.stdout+'\n'+run.stderr, encoding='utf-8')
        print(name, record, flush=True)
        if run.returncode:
            raise RuntimeError(f'Falló {name}: {run.stderr[-1500:]}')
    question = '¿Qué significa HGP y en qué hitos EOH y EOC está previsto?'
    start = time.perf_counter()
    cpu_start = time.process_time()
    if number == 1:
        from src.embeddings import EmbeddingModel
        from src.vector_store import VectorStore
        model = EmbeddingModel()
        load_seconds = time.perf_counter()-start
        ram_loaded = process.memory_info().rss / 1024**2
        store = VectorStore()
        query_start = time.perf_counter()
        vector = model.embed_query(question)
        hits = store.similarity_search(vector, top_k=5)
        result['modelo_embeddings'] = model.model_name
        result['dimension_vector'] = len(vector)
        result['segundos_carga_embeddings'] = round(load_seconds, 3)
        result['ram_python_modelo_cargado_mb'] = round(ram_loaded, 1)
        result['segundos_consulta'] = round(time.perf_counter()-query_start, 3)
        result['fragmentos_base_activa'] = store.count()
        result['fragmentos_recuperados'] = len(hits)
        result['usa_modelo_generativo'] = False
        store.client.close()
    else:
        from config.settings import settings
        from rag.embeddings import get_embedding_model
        from rag.vector_store import VectorStore
        from rag.retriever import Retriever
        from rag.augmentation import build_prompt
        from rag.generator import generate_answer
        import ollama
        model = get_embedding_model()
        result['segundos_carga_embeddings'] = round(time.perf_counter()-start, 3)
        result['ram_python_modelo_cargado_mb'] = round(process.memory_info().rss/1024**2, 1)
        result['dimension_vector'] = model.get_embedding_dimension()
        result['modelo_embeddings'] = settings.EMBEDDING_MODEL
        store = VectorStore()
        query_start = time.perf_counter()
        hits = Retriever(store).search(question, top_k=5)
        result['segundos_recuperacion'] = round(time.perf_counter()-query_start, 3)
        result['fragmentos_base_activa'] = store.count()
        result['fragmentos_recuperados'] = len(hits)
        original_chat = ollama.Client.chat
        raw = {}
        def tracked_chat(client, *args, **kwargs):
            response = original_chat(client, *args, **kwargs)
            raw.update(response.model_dump())
            return response
        ollama.Client.chat = tracked_chat
        gen_start = time.perf_counter()
        answer = generate_answer(build_prompt(question, hits))
        result['segundos_generacion'] = round(time.perf_counter()-gen_start, 3)
        result['modelo_generacion'] = settings.OLLAMA_MODEL
        result['limite_tokens_salida'] = 300
        result['temperatura'] = settings.GENERATION_TEMPERATURE
        result['ollama'] = {name: raw.get(name) for name in ('prompt_eval_count', 'eval_count', 'total_duration', 'load_duration', 'prompt_eval_duration', 'eval_duration')}
        if raw.get('eval_duration'):
            result['ollama']['tokens_salida_por_segundo'] = round(raw['eval_count']/(raw['eval_duration']/1e9), 2)
        result['respuesta_medida'] = answer
        client = ollama.Client(host=settings.OLLAMA_HOST)
        result['ollama_modelos_cargados'] = client.ps().model_dump(mode='json')
        ram_ollama = []
        for p in psutil.process_iter(['name', 'memory_info']):
            try:
                if 'ollama' in p.info['name'].lower():
                    ram_ollama.append({'proceso': p.info['name'], 'ram_mb': round(p.info['memory_info'].rss/1024**2,1)})
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                pass
        result['ram_procesos_ollama_mb'] = ram_ollama
        from comparison.rag_vs_long_context import compare
        result['comparacion_tokens'] = compare('¿Qué intervención está prevista para WAR42 en 2027?', top_k=4)
        store.client.close()
    result['segundos_cpu_proceso_medicion'] = round(time.process_time()-cpu_start, 3)
    result['ram_python_final_mb'] = round(process.memory_info().rss/1024**2, 1)
    result['ram_python_maxima_mb'] = round(process.memory_info().peak_wset/1024**2, 1)
    result['pesos_embeddings_disco_mb'] = round(sum(p.stat().st_size for p in (ROOT/'.cache/huggingface/hub').rglob('*') if p.is_file())/1024**2,1)
    (evidence/'consumo_modelos.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Medición guardada:', evidence/'consumo_modelos.json', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('proyecto', type=int, choices=(1,2))
    main(parser.parse_args().proyecto)

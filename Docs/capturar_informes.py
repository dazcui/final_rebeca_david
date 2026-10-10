"""Capturas de aplicaciones locales en Chromium aislado y vistas del código real."""
from pathlib import Path
import html
import json
import re
import os
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
P1 = ROOT/'rag-chunking-embeddings-vectordb/rag-chunking-embeddings-vectordb'
P2 = ROOT/'rag-knowledge-pipeline (1)/rag-knowledge-pipeline'
MANIFEST = {1: [], 2: []}


def code_capture(page, project, number, name, title, file, start, end):
    path = project/file
    lines = path.read_text(encoding='utf-8-sig').splitlines()
    end = min(end, len(lines))
    body = ''.join(f'<tr><td class="num">{i}</td><td><pre>{html.escape(lines[i-1])}</pre></td></tr>' for i in range(start,end+1))
    document = f'''<!doctype html><html lang="es"><meta charset="utf-8"><style>
    body{{margin:0;background:#f5f7fa;color:#17253a;font-family:Arial,sans-serif}}
    header{{padding:24px 34px;background:#12243b;color:white}} h1{{font-size:24px;margin:0 0 12px}}
    header p{{margin:6px 0;font-size:16px}} .note{{color:#c3d6ec;font-size:14px}}
    main{{margin:22px 28px;background:white;border:1px solid #ccd4df;padding:10px 0}}
    table{{border-collapse:collapse;width:100%}}td{{vertical-align:top}}pre{{font:16px/24px Consolas,monospace;margin:0;white-space:pre-wrap;overflow-wrap:anywhere}}
    .num{{width:50px;padding:0 16px;color:#617184;text-align:right;border-right:1px solid #dce2ea;font:16px/24px Consolas}}
    td+td{{padding:0 20px}}footer{{margin:20px 30px;font-size:14px;color:#536171}}
    </style><header><h1>{html.escape(title)}</h1><p>{html.escape(file)} · líneas {start}–{end}</p><p class="note">Vista documental del archivo real. Esta imagen no es una captura de Visual Studio Code.</p></header><main><table>{body}</table></main><footer>Proyecto {number} · Evidencia local · 10 de octubre de 2026</footer></html>'''
    folder = project/'Docs/capturas'
    folder.mkdir(parents=True,exist_ok=True)
    source = folder/(name+'.html')
    source.write_text(document,encoding='utf-8')
    page.goto(source.as_uri())
    page.screenshot(path=str(folder/(name+'.png')),full_page=True)
    MANIFEST[number].append({'archivo':name+'.png','titulo':title,'tipo':'vista_codigo' if file.endswith('.py') else 'vista_archivo', 'origen':file, 'linea_inicio':start,'linea_fin':end, 'vista_html':'capturas/'+name+'.html'})
    (folder/'manifest.json').write_text(json.dumps(MANIFEST[number],ensure_ascii=False,indent=2),encoding='utf-8')
    print('Captura:',number,name,flush=True)


def app_capture(page, project, number, name, title, file, start, end):
    folder = project/'Docs/capturas'
    folder.mkdir(parents=True,exist_ok=True)
    page.screenshot(path=str(folder/(name+'.png')),full_page=True)
    MANIFEST[number].append({'archivo':name+'.png','titulo':title,'tipo':'aplicacion_real','origen':page.url,'codigo':file,'linea_inicio':start,'linea_fin':end})
    (folder/'manifest.json').write_text(json.dumps(MANIFEST[number],ensure_ascii=False,indent=2),encoding='utf-8')
    print('Captura aplicación:',number,name,flush=True)


def main():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True,executable_path=str(ROOT/'.cache/playwright/chromium-1243/chrome-win64/chrome.exe'))
        context = browser.new_context(viewport={'width':1400,'height':1000},device_scale_factor=1)
        page = context.new_page()
        only_app2 = os.getenv('SOLO_APP2') == '1'
        if only_app2:
            for number, project in [(1,P1),(2,P2)]:
                MANIFEST[number] = json.loads((project/'Docs/capturas/manifest.json').read_text(encoding='utf-8'))
            MANIFEST[2] = [m for m in MANIFEST[2] if m['tipo'] != 'aplicacion_real']
        # Estas vistas se crean leyendo directamente el código y los registros.
        p1 = [
            ('01_manual','Documento utilizado como fuente','data/documentos/MANUAL_PROGRAMA_MANTENIMIENTO_PREVENTIVO.md',1,30),
            ('02_dependencias','Dependencias instaladas y necesarias','requirements.txt',1,35),
            ('03_configuracion','Rutas, modelo y tamaño de fragmentos','config.py',18,64),
            ('04_fragmentacion','División del manual por separadores','src/chunking.py',32,63),
            ('05_embeddings','Carga del modelo y creación de vectores','src/embeddings.py',21,62),
            ('06_ingesta','Registro real de la ingesta del manual','Docs/evidencias/ingesta.txt',1,45),
            ('07_consulta_terminal','Consulta real y fuentes recuperadas','Docs/evidencias/consulta.txt',1,45),
            ('12_consumo_modelos','Consumo medido del modelo de embeddings','Docs/evidencias/consumo_resumen.json',1,60),
        ]
        p2 = [
            ('01_manual','Manual utilizado por el sistema RAG','data/raw/MANUAL_PROGRAMA_MANTENIMIENTO_PREVENTIVO.md',1,30),
            ('02_configuracion','Configuración de recuperación y modelos','config/settings.py',16,57),
            ('03_ingestion_codigo','Etapas de extracción, limpieza e ingesta','ingestion/pipeline.py',26,69),
            ('04_fragmentacion','Solapamiento y división del texto limpio','rag/chunking.py',66,109),
            ('05_recuperacion','Búsqueda híbrida y tratamiento de siglas','rag/retriever.py',84,116),
            ('06_generacion','Consumo de Ollama y reglas de respuesta','rag/generator.py',21,50),
            ('07_ingesta','Registro real de la base de validación','Docs/evidencias/ingesta.txt',1,45),
            ('12_consumo_modelos','Tiempo, memoria y tokens medidos','Docs/evidencias/consumo_resumen.json',1,75),
            ('13_pruebas','Resultado real de las pruebas del proyecto','Docs/evidencias/pruebas.txt',1,20),
            ('14_contexto','Construcción del contexto enviado al modelo','rag/augmentation.py',11,46),
        ]
        for number, project, captures in [(1,P1,p1),(2,P2,p2)]:
            for name,title,file,start,end in captures:
                if not only_app2:
                    code_capture(page,project,number,name,title,file,start,end)
        # Aplicación 1: fotografías del navegador de prueba, no vistas recreadas.
        if not only_app2:
            capture_app1(page)
        # Aplicación 2: envío de preguntas y consulta de las fuentes reales.
        page.goto('http://127.0.0.1:8502',wait_until='domcontentloaded')
        page.get_by_role('button',name='Consultar pregunta sugerida',exact=True).wait_for(timeout=120000)
        page.get_by_text('57',exact=True).wait_for(timeout=120000)
        app_capture(page,P2,2,'08_aplicacion_inicio','Chat, modelos y base de conocimiento','app/streamlit_app.py',22,68)
        page.get_by_role('button',name='Consultar pregunta sugerida',exact=True).click()
        wait_answer(page,2)
        app_capture(page,P2,2,'09_respuesta_inspecciones','Respuesta generada sobre las inspecciones','app/streamlit_app.py',70,107)
        expanders = page.locator('[data-testid="stExpander"] details summary')
        expanders.last.click()
        page.locator('[data-testid="stExpander"] [data-testid="stText"]').first.wait_for(timeout=30000)
        app_capture(page,P2,2,'10_fuentes_recuperadas','Fuentes y fragmentos que sustentan la respuesta','app/streamlit_app.py',80,94)
        chat = page.get_by_role('textbox',name='Pregunta sobre inspecciones, contratos o cronogramas...')
        chat.fill('¿Qué significa HGP y en qué hitos EOH y EOC está previsto?')
        chat.press('Enter')
        wait_answer(page,4)
        app_capture(page,P2,2,'11_respuesta_hgp','Consulta de HGP con horas y ciclos equivalentes','app/streamlit_app.py',64,107)
        for number,project in [(1,P1),(2,P2)]:
            rows=sorted(MANIFEST[number],key=lambda x:x['archivo'])
            (project/'Docs/capturas/manifest.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
            assert len(rows)>=10
        browser.close()


def wait_answer(page, count):
    page.wait_for_function('''(count) => {
        const messages = document.querySelectorAll('[data-testid="stChatMessage"]');
        if(messages.length < count) return false;
        return [...messages[messages.length-1].querySelectorAll('[data-testid="stMarkdownContainer"]')]
          .some(el => !el.closest('[data-testid="stExpander"]') && !el.closest('[data-testid="stSpinner"]') && el.innerText.trim().length > 25);
    }''',arg=count,timeout=210000)


def capture_app1(page):
        page.goto('http://127.0.0.1:8501',wait_until='domcontentloaded')
        page.get_by_role('button',name='Buscar',exact=True).wait_for(timeout=120000)
        page.get_by_text('58',exact=True).wait_for(timeout=120000)
        app_capture(page,P1,1,'08_aplicacion_inicio','Inicio del buscador y base indexada','app.py',6,24)
        page.get_by_role('button',name='Buscar',exact=True).click()
        page.get_by_role('heading',name='Fragmento 5',exact=True).wait_for(timeout=60000)
        app_capture(page,P1,1,'09_busqueda_inspecciones','Resultados reales sobre inspecciones A, B y C','app.py',26,35)
        page.get_by_role('textbox',name='Pregunta',exact=True).fill('¿Qué diferencia hay entre los contratos Offshore y Onshore?')
        page.get_by_role('textbox',name='Pregunta',exact=True).press('Enter')
        page.get_by_role('button',name='Buscar',exact=True).click()
        page.get_by_role('heading',name='Fragmento 5',exact=True).wait_for(timeout=60000)
        app_capture(page,P1,1,'10_busqueda_contratos','Comparación documental de Offshore y Onshore','app.py',26,35)
        page.get_by_role('textbox',name='Pregunta',exact=True).fill('¿Qué significa la confiabilidad operativa de 96,89 %?')
        page.get_by_role('textbox',name='Pregunta',exact=True).press('Enter')
        page.get_by_role('button',name='Buscar',exact=True).click()
        page.get_by_role('heading',name='Fragmento 5',exact=True).wait_for(timeout=60000)
        app_capture(page,P1,1,'11_busqueda_confiabilidad','Recuperación del indicador y sus límites','app.py',26,35)


if __name__=='__main__':
    main()

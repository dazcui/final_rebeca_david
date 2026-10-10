"""Revisa que las imágenes de los informes se carguen en su vista HTML."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
output=[]
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,executable_path=str(ROOT/'.cache/playwright/chromium-1243/chrome-win64/chrome.exe'))
    page=browser.new_page(viewport={'width':1440,'height':1100})
    for name,count in [('Informe_chucking_embeddings',12),('Informe_rag_pipeline',14)]:
        page.goto((ROOT/'Docs'/f'{name}.html').as_uri())
        page.wait_for_function('Array.from(document.images).every(image => image.complete && image.naturalWidth > 0)')
        actual=page.locator('img').count()
        assert actual==count,(name,actual)
        page.screenshot(path=str(ROOT/'Docs'/f'{name}_vista.png'))
        capture=page.get_by_role('heading',name='Captura 01. Documento utilizado como fuente' if count==12 else 'Captura 01. Manual utilizado por el sistema RAG',exact=True)
        capture.scroll_into_view_if_needed()
        page.screenshot(path=str(ROOT/'Docs'/f'{name}_capturas_vista.png'))
        output.append({'informe':name,'imagenes_cargadas':actual,'ancho_pagina':1440})
    browser.close()
(ROOT/'Docs/validacion_presentacion.json').write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(output,ensure_ascii=False,indent=2))

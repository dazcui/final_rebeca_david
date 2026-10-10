"""Comprueba enlaces, secciones, imágenes y metadatos de los informes."""
from pathlib import Path
from urllib.parse import unquote
import json
import re

ROOT = Path(__file__).resolve().parents[1]
FILES = [ROOT/'Docs/Informe_chucking_embeddings.md',ROOT/'Docs/Informe_rag_pipeline.md',
         ROOT/'rag-chunking-embeddings-vectordb/rag-chunking-embeddings-vectordb/Docs/Informe.md',
         ROOT/'rag-knowledge-pipeline (1)/rag-knowledge-pipeline/Docs/Informe.md']
required = ['Introducción','Objetivos','Marco Teórico','Implementación Aplicada','Conclusiones','Recomendaciones']
errors = []
summary = []
for file in FILES:
    content = file.read_text(encoding='utf-8')
    for section in required:
        if section not in content:
            errors.append(f'{file}: falta {section}')
    images = re.findall(r'!\[[^\]]*\]\(([^)]+)\)',content)
    if len(images)<10:
        errors.append(f'{file}: menos de 10 capturas')
    for target in re.findall(r'\]\(([^)]+)\)',content):
        if '://' not in target and not target.startswith('#'):
            resolved = (file.parent/unquote(target)).resolve()
            if not resolved.exists():
                errors.append(f'{file}: enlace roto {target}')
    if content.count('```') % 2:
        errors.append(f'{file}: bloque de código sin cerrar')
    summary.append({'informe':str(file.relative_to(ROOT)),'capturas':len(images),'palabras':len(content.split()),'bytes':file.stat().st_size})
for project in (FILES[2].parent.parent,FILES[3].parent.parent):
    manifest=json.loads((project/'Docs/capturas/manifest.json').read_text(encoding='utf-8'))
    for shot in manifest:
        png=project/'Docs/capturas'/shot['archivo']
        if png.read_bytes()[:8] != b'\x89PNG\r\n\x1a\n':
            errors.append(f'PNG inválido: {png}')
        source=project/shot.get('codigo',shot['origen'])
        if not str(source).startswith('http') and shot['tipo']!='aplicacion_real':
            lines=source.read_text(encoding='utf-8-sig').splitlines()
            if not 1<=shot['linea_inicio']<=shot['linea_fin']<=len(lines):
                errors.append(f'Líneas inválidas: {source}')
assert not errors, '\n'.join(errors)
(ROOT/'Docs/validacion_informes.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
print('Secciones, rutas, enlaces, imágenes y bloques de código verificados.')

# Se genera una vista HTML adicional para facilitar la lectura y la revisión visual.
try:
    from markdown_it import MarkdownIt
    md=MarkdownIt('commonmark').enable('table')
    css='''body{margin:0;background:#eef2f6;color:#17253a;font:17px/1.6 Arial,sans-serif}
    main{max-width:1080px;margin:30px auto;padding:36px 48px;background:white}
    h1,h2,h3,h4{line-height:1.25;color:#12304f}h2{margin-top:44px;border-bottom:2px solid #ccd8e3;padding-bottom:10px}
    img{display:block;max-width:100%;height:auto;border:1px solid #d5dce5;margin:22px 0}
    pre{background:#f2f5f8;padding:18px;overflow:auto;line-height:1.5}code{font-family:Consolas,monospace}
    table{border-collapse:collapse;width:100%;font-size:15px}td,th{border:1px solid #ccd5df;padding:10px;text-align:left}
    a{color:#125993} @media print{main{margin:0;padding:0}h2,h3,h4{break-after:avoid}img{break-inside:avoid}}'''
    for file in FILES:
        rendered='<!doctype html><html lang="es"><meta charset="utf-8"><title>'+file.stem+'</title><style>'+css+'</style><main>'+md.render(file.read_text(encoding='utf-8'))+'</main></html>'
        file.with_suffix('.html').write_text(rendered,encoding='utf-8')
    print('Vistas HTML de lectura creadas.')
except ImportError:
    print('La validación terminó; el intérprete no incluye el visor Markdown para generar HTML.')

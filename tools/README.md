# Diagramas en Excalidraw (generación y exportación)

- `gen_harness_excalidraw.py` — genera `Diagramas/harness.excalidraw` y las variantes con un happy path resaltado (`harness-hp1`, `hp2`, `hp3`, `sin-llm`) con la notación del profesor (iteraciones en el mismo lienzo, backlog a la izquierda, monigotes, services azules, BD amarillas, APIs rojas, colas/jobs verdes, SPOF/riesgo en rojo, patrones de reliability como etiquetas de flecha).
- `render-excalidraw.mjs` — abre el `.excalidraw` con la librería oficial de Excalidraw en Chrome headless y exporta `harness.svg`, `harness.png` y `harness.pdf` (una página, texto seleccionable). Requiere Google Chrome y acceso a esm.sh.

```sh
python3 tools/gen_harness_excalidraw.py
for v in harness harness-hp1 harness-hp2 harness-hp3 harness-sin-llm; do node tools/render-excalidraw.mjs Diagramas/$v.excalidraw; done
```

Para editar a mano: abrir `Diagramas/harness.excalidraw` en https://excalidraw.com (menú → Open) y exportar desde ahí.

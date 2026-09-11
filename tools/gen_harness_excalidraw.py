#!/usr/bin/env python3
"""Genera Diagramas/harness.excalidraw (estilo del profesor: iteraciones, backlog, monigotes,
services azules, BD amarillas, APIs rojas, colas/jobs verdes, SPOF/riesgo en rojo).
Uso: python3 tools/gen_harness_excalidraw.py   (desde la raíz de lab05)"""
import json, math, random, time, os

random.seed(5)
NOW = int(time.time() * 1000)
FONT = 3            # Cascadia (monoespaciada), como en los Excalidraw del profesor
BLUE, BLUE_BG = "#1971c2", "#a5d8ff"
GREEN, GREEN_BG = "#2f9e44", "#b2f2bb"
RED, RED_BG = "#e03131", "#ffc9c9"
ORANGE, YELLOW_BG = "#f08c00", "#ffec99"
BLACK = "#1e1e1e"
elements = []
_id = 0

def nid(p="e"):
    global _id; _id += 1; return f"{p}{_id:04d}"

def base(t, x, y, w, h, stroke=BLUE, bg="transparent", **kw):
    e = dict(id=nid(), type=t, x=x, y=y, width=w, height=h, angle=0, strokeColor=stroke,
             backgroundColor=bg, fillStyle="solid", strokeWidth=2, strokeStyle="solid",
             roughness=1, opacity=100, groupIds=[], frameId=None, roundness=None,
             seed=random.randint(1, 2**31), version=1, versionNonce=random.randint(1, 2**31),
             isDeleted=False, boundElements=[], updated=NOW, link=None, locked=False)
    e.update(kw); elements.append(e); return e

def tsize(text, fs):
    lines = text.split("\n")
    return 0.6 * fs * max(len(l) for l in lines), 1.25 * fs * len(lines)

def text(x, y, s, fs=16, color=BLUE, align="left", container=None, cx=None, cy=None):
    w, h = tsize(s, fs)
    if cx is not None: x = cx - w / 2
    if cy is not None: y = cy - h / 2
    t = base("text", x, y, w, h, stroke=color, text=s, fontSize=fs, fontFamily=FONT,
             textAlign=align, verticalAlign="middle", containerId=container["id"] if container else None,
             originalText=s, autoResize=True, lineHeight=1.25)
    t["boundElements"] = None
    if container: container["boundElements"].append({"id": t["id"], "type": "text"})
    return t

def box(cx, cy, label, w=190, h=70, stroke=BLUE, bg=BLUE_BG, fs=16, tcolor=None):
    b = base("rectangle", cx - w / 2, cy - h / 2, w, h, stroke, bg, roundness={"type": 3})
    b["_c"] = (cx, cy); b["_kind"] = "rect"
    text(0, 0, label, fs, tcolor or stroke, "center", b, cx, cy)
    return b

def db(cx, cy, label, w=120, h=90, fs=14):
    e = base("ellipse", cx - w / 2, cy - h / 2, w, h, ORANGE, YELLOW_BG)
    e["_c"] = (cx, cy); e["_kind"] = "ellipse"
    text(0, 0, label, fs, ORANGE, "center", e, cx, cy)
    return e

def user(cx, cy, label):
    g = nid("g")
    head = base("ellipse", cx - 20, cy - 45, 40, 40, BLUE, BLUE_BG, groupIds=[g])
    body = base("line", cx, cy - 5, 0, 45, BLUE, points=[[0, 0], [0, 45]], groupIds=[g], lastCommittedPoint=None,
                startBinding=None, endBinding=None, startArrowhead=None, endArrowhead=None)
    t = text(0, 0, label, 16, BLUE, "center", None, cx, cy + 56); t["groupIds"] = [g]
    head["_c"] = (cx, cy - 25); head["_kind"] = "ellipse"; head["_r"] = (cx - 20, cy - 45, 40, 90)
    return head

def edge_point(el, tx, ty):
    """Punto del borde de `el` en dirección a (tx,ty)."""
    cx, cy = el["_c"]
    if "_r" in el: x, y, w, h = el["_r"]; cx, cy = x + w / 2, y + h / 2
    else: x, y, w, h = el["x"], el["y"], el["width"], el["height"]
    dx, dy = tx - cx, ty - cy
    if dx == 0 and dy == 0: return cx, cy
    if el["_kind"] == "ellipse" and "_r" not in el:
        a, b = w / 2, h / 2
        k = 1 / math.sqrt((dx / a) ** 2 + (dy / b) ** 2)
        return cx + dx * k, cy + dy * k
    sx = (w / 2) / abs(dx) if dx else math.inf
    sy = (h / 2) / abs(dy) if dy else math.inf
    k = min(sx, sy)
    return cx + dx * k, cy + dy * k

def arrow(a, b, label=None, color=BLUE, dashed=False, fs=13, lcolor=None, offset=(0, 0), width=2, at=None, via=None):
    ax, ay = a["_c"] if "_r" not in a else (a["_r"][0] + a["_r"][2] / 2, a["_r"][1] + a["_r"][3] / 2)
    bx, by = b["_c"] if "_r" not in b else (b["_r"][0] + b["_r"][2] / 2, b["_r"][1] + b["_r"][3] / 2)
    if via:
        sx, sy = edge_point(a, *via[0]); ex, ey = edge_point(b, *via[-1])
        pts = [[0, 0]] + [[vx - sx, vy - sy] for vx, vy in via] + [[ex - sx, ey - sy]]
    else:
        sx, sy = edge_point(a, bx, by); ex, ey = edge_point(b, ax, ay)
        pts = [[0, 0], [ex - sx, ey - sy]]
    e = base("arrow", sx, sy, ex - sx, ey - sy, color, "transparent", roundness=None if via else {"type": 2},
             points=pts, lastCommittedPoint=None,
             startBinding={"elementId": a["id"], "focus": 0, "gap": 4},
             endBinding={"elementId": b["id"], "focus": 0, "gap": 4},
             startArrowhead=None, endArrowhead="arrow", elbowed=False)
    e["strokeWidth"] = width
    if dashed: e["strokeStyle"] = "dashed"
    a["boundElements"].append({"id": e["id"], "type": "arrow"}); b["boundElements"].append({"id": e["id"], "type": "arrow"})
    e["_ends"] = (a["id"], b["id"])
    if label and at:                      # etiqueta libre en posición absoluta (Excalidraw centra las ligadas)
        e["_label"] = text(0, 0, label, fs, lcolor or color, "center", None, at[0], at[1])["id"]
    elif label:
        mx, my = (sx + ex) / 2 + offset[0], (sy + ey) / 2 + offset[1]
        text(0, 0, label, fs, lcolor or color, "center", e, mx, my)
    return e

def note(cx, cy, s, fs=13, color=RED): return text(0, 0, s, fs, color, "center", None, cx, cy)

def draw(focus=None, title=None, skip=()):
    """focus: lista ordenada de nombres de piezas del happy path; lo demás se atenúa y se numeran los pasos."""
    # ───────────────────────── Título y backlog (izquierda) ─────────────────────────
    text(40, 40, "Genius-x — HARNESS DEL LLM\nTOP DOWN DESIGN · Reliability / Fault tolerance", 22, BLACK)
    text(40, 110, "Lab 05 · Arquitectura de Software UTEC 2026-II · Fabian Alvarado · Mauricio Salazar", 13, BLACK)
    backlog = [
     "RF01 consulta de estado (7 campos)", "RF02 estado siempre actual (<=30s)", "RF03 fuente, fecha y vigencia",
     "RF04 respuestas aprobadas con dueno", "RF05 historial del incidente", "RF06 conocimiento vivo y versionado",
     "RF07 clasificacion + SLA 1d/3d", "RF08 escalar con contexto", "RF09 alertas SLA 50/80/100 %",
     "RF10 lista de acciones permitidas", "RF11 aprobacion humana para escribir", "RF12 permisos por rol",
     "RF13 queries solo lectura (copia)", "RF14 E2E tests en ambiente aparte", "RF15 auditoria por incidente",
     "RF16 feedback validado", "RF17 cola de preguntas (urgentes 1o)", "RF18 responde sin LLM + /incident",
     "RF19 filtro de entrada / revision", "RF20 pruebas diarias (gate <95 %)", "RF21 panel de salud (semaforo)",
     "RF22 pasos a seguir por tipo", "RF23 misma pregunta, misma respuesta", "RF24 tablero de SLA",
     "RF25 skills: guias por tipo de tarea", "RF26 alta de usuarios con su rol",
    ]
    text(40, 160, "Requerimientos (backlog) — cubiertos en iteracion #2:", 15, BLACK)
    text(40, 190, "\n".join(f"- {b}  DONE" for b in backlog), 14, BLUE)
    text(40, 640, "RNF: carga 3x probada · P95 <1s/<5s/<10s · 99,9 % estado · sin SPOF\n"
                  "timeouts + retry + circuit breaker · RTO <5 min, RPO 0 · minimo privilegio\n"
                  "(ver Requirements/ReqNoFunc.md)", 13, BLACK)

    # Leyenda
    ly = 760
    text(40, ly, "Leyenda", 16, BLACK)
    box(110, ly + 55, "Service", 130, 40, BLUE, BLUE_BG, 14)
    db(110, ly + 125, "BD", 130, 55, 13)
    box(110, ly + 195, "API externa", 130, 40, RED, RED_BG, 14)
    box(110, ly + 250, "cola / job", 130, 40, GREEN, GREEN_BG, 14)
    user(330, ly + 80, "usuario")
    text(240, ly + 175, "texto rojo = SPOF /\nriesgo alto", 13, RED)
    text(240, ly + 225, "flecha punteada =\naviso / async", 13, BLACK)
    text(240, ly + 275, "etiqueta en flecha =\ncondicion o patron\nde reliability", 13, BLACK)
    box(110, ly + 330, "CIRCUIT BREAKER", 190, 42, RED, "transparent", 12)
    text(240, ly + 330, "rectangulo rojo sin relleno =\ncircuit breaker", 13, BLACK)

    # ───────────────────────── Iteración #1: harness actual ─────────────────────────
    text(700, 60, "iteracion #1 — harness actual (enunciado)", 20, BLACK)
    u1 = user(720, 260, "Soporte /\nSRE")
    api = box(1000, 240, "API", 140, 60)
    llm = box(1300, 240, "LLM local", 160, 60)
    mcpdb = box(1620, 165, "MCP\nDatabase", 150, 60)
    dbase = db(1900, 165, "Database")
    mcps = box(1620, 330, "MCP\nSlack", 150, 60)
    slack1 = box(1900, 330, "Slack", 140, 60, RED, RED_BG)
    arrow(u1, api); arrow(api, llm); arrow(llm, mcpdb); arrow(mcpdb, dbase); arrow(llm, mcps); arrow(mcps, slack1)
    note(1000, 300, "SPOF: una sola API"); note(1300, 305, "SPOF: un solo LLM\nsin cola, sin respuestas guardadas,\nsin plan B -> no responde en el pico")
    note(1620, 110, "nadie revisa ni aprueba"); note(1920, 95, "SPOF + riesgo alto: credencial admin,\nel LLM puede borrar la BD")
    note(1620, 385, "sin circuit breaker:\nSlack caido = Genius caido"); note(1900, 385, "estado viejo: nadie avisa\ncuando cambia un incidente")

    # ───────────────────────── Iteración #2: nuevo harness ─────────────────────────
    t2 = text(700, 450, title or "iteracion #2 — nuevo harness con reliability y fault tolerance", 20, BLACK)
    C = [700, 1000, 1340, 1680, 2020, 2360, 2700, 3120, 3500]
    R0, R1, R2, R3, R4, R5 = 530, 720, 970, 1210, 1450, 1690

    # apoyo (arriba)
    aprend = box(C[3], R0, "Aprendizaje Service\n(feedback validado por\nuna persona, <=1 dia)", 220, 80, fs=13)
    indexar = box(C[7], R0, "Indexar Job <15 min>\nlo nuevo entra, lo viejo\nqueda marcado", 220, 80, GREEN, GREEN_BG, 13)
    pruebasd = box(C[8], R0, "Pruebas Diarias Job\npreguntas comunes vs\nrespuesta esperada", 220, 80, GREEN, GREEN_BG, 13)
    resp_g = db(C[4], R1, "Cache de\nRespuestas", fs=13)
    hist = db(C[5], R1, "Historial", fs=14)
    conoc = db(C[6], R1, "Base de\nConocimiento", fs=13)
    skills = db(C[7], R1, "Skills\n(guias por tarea)", fs=12)
    # camino principal
    u_sop = user(C[0], R2 - 150, "Diego Ramos\nSoporte N2"); u_sre = user(C[0], R2, "Valeria Torres\nSRE on-call")
    u_im = user(C[0], R2 + 150, "Marco Salas\nIncident manager")
    app = box(C[1], R2, "Genius App\n(Slack / Web)", 170, 70)
    login = box(C[2], R2, "Login\nService", 170, 70)
    u_adm = user(C[0], R1 - 60, "Admin de Genius")
    registro = box(C[1], R1, "Registro de Usuarios\nService (crea la cuenta\ny le pone el rol)", 220, 80, fs=13)
    usuarios = db(C[2], R1, "Usuarios\ny roles", fs=13)
    filtro = box(C[3], R2, "Filtro\nService", 170, 70)
    consulta = box(C[4], R2, "Consulta\nService", 170, 70)
    contexto = box(C[5], R2, "Contexto\nService", 170, 70)
    cola = box(C[6], R2, "Cola de\nPreguntas", 170, 70, GREEN, GREEN_BG)
    llm1 = box(C[7], R2 - 50, "LLM local #1", 170, 55)
    llm2 = box(C[7], R2 + 50, "LLM local #2", 170, 55)
    revision = box(C[8], R2, "Revision\nService", 170, 70)
    # acciones
    estado = db(C[3], R3, "Estado\nActual", fs=13)
    slackapi = box(C[4], R3, "Slack API", 150, 60, RED, RED_BG)
    mensajes = box(C[5], R3, "Mensajes\nService", 170, 70, GREEN, GREEN_BG)
    aprob = box(C[7], R3, "Aprobacion\nService", 170, 70)
    acciones = box(C[8], R3, "Acciones\nService", 170, 70)
    panel = box(C[1], R3 + 120, "Tablero SLA +\nPanel de salud", 190, 70)
    reportes = box(C[2], R3, "Reportes\nService", 170, 70)
    monit = box(C[0], R3 + 80, "Monitoreo Service\nhealth · Availability\nReliability · P95", 200, 80, fs=12)
    # estado / avisos
    rep_sync = db(C[0], R4, "Replica\nsincrona", fs=13)
    bdinc = db(C[1], R4, "BD\nIncidentes", fs=13)
    incid = box(C[2], R4, "Incidentes\nService", 170, 70)
    cambios = box(C[3], R4, "Cola de\nCambios", 170, 70, GREEN, GREEN_BG)
    sla = box(C[4], R4, "SLA\nService", 170, 70)
    email = box(C[5], R4, "Email\nService", 170, 70, GREEN, GREEN_BG)
    pruebas = box(C[7], R4, "Pruebas Service\n(E2E, ambiente aparte)", 200, 70, fs=13)
    copia = db(C[8], R4, "Copia de\nlectura", fs=13)
    audit = db(C[3], R5, "Auditoria\n(solo se agrega)", fs=12)

    # Flechas: camino de una pregunta
    arrow(u_sop, app); arrow(u_sre, app); arrow(u_im, app)
    arrow(u_adm, registro, "crea la cuenta", offset=(0, -16)); arrow(registro, usuarios, "guarda rol")
    arrow(login, usuarios, "valida contra\nusuarios y roles", offset=(46, 0))
    arrow(app, login, "quien es", offset=(0, -18)); arrow(login, filtro, "rol OK", offset=(0, -18)); arrow(filtro, consulta, "pregunta OK", offset=(0, -18))
    arrow(consulta, resp_g, "ya existe?", offset=(70, 0))
    note(C[4] + 90, R1 - 85, "CACHE de Respuestas: protege el cuello de botella (LLM)", 12, BLUE)
    note(C[4] + 165, R1 + 40, "ya existe -> responde\nigual que siempre", 12, BLUE)
    arrow(consulta, contexto, "no existe", offset=(0, -18))
    arrow(contexto, hist, "lo ya hecho", offset=(65, 0)); arrow(contexto, conoc, "runbooks con\nfecha y version", offset=(60, -20))
    arrow(contexto, estado, "estado real", offset=(-60, -10))
    arrow(contexto, skills, "guia de la tarea")
    arrow(indexar, skills, "", dashed=True)
    arrow(consulta, estado, "")
    note(C[4] + 130, R2 + 62, "si el LLM no responde:\nestado + respuesta guardada", 12, BLUE)
    arrow(contexto, cola, "pregunta +\ncontexto", offset=(0, -30))
    cb_llm = box((C[6] + C[7]) / 2, R2, "CIRCUIT BREAKER\ntimeout 5 s · si #1 no\nresponde, retry en #2", 230, 74, RED, "transparent", 12)
    arrow(cola, cb_llm, ""); arrow(cb_llm, llm1, ""); arrow(cb_llm, llm2, "")
    arrow(llm1, revision, "respuesta"); arrow(llm2, revision, "")
    arrow(aprend, resp_g, "correccion\nvalidada", dashed=True, offset=(-70, 0))
    arrow(indexar, conoc, "", dashed=True)
    arrow(pruebasd, llm1, "cada dia", dashed=True, color=GREEN, offset=(60, -10))
    note(C[2], R2 + 55, "riesgo alto: si se equivoca de rol")
    note(C[7], R2 + 118, "CUELLO DE BOTELLA (bottleneck): el LLM se satura en el pico\nlo aguantan la Cola, las 2 copias, el CIRCUIT BREAKER y el CACHE de Respuestas")
    note(C[4] + 150, R3 + 66, "SPOF: Slack API es de un tercero y es el unico canal\nlo aguantan el CIRCUIT BREAKER y el Email Service de respaldo")
    # camino de una accion
    arrow(revision, app, "es texto: la respuesta vuelve al ingeniero con fuente y fecha", dashed=True,
          via=[(C[8], R2 - 180), (C[1], R2 - 180)], at=(1750, R2 - 155))
    arrow(revision, acciones, "es una accion", offset=(75, 0))
    arrow(acciones, copia, "lectura", offset=(50, 0))
    arrow(acciones, pruebas, "pruebas E2E", offset=(40, 14))
    arrow(acciones, aprob, "escritura", offset=(0, -18))
    arrow(acciones, incid, "bajo riesgo (escalar, comentar): crea o actualiza el incidente sin aprobacion", via=[(C[8] + 120, R3), (C[8] + 120, R5 - 90), (C[2], R5 - 90)], at=(2200, R5 - 108))
    note(C[8] + 210, R3, "BORRAR / CAMBIAR\nESTRUCTURA:\nBLOQUEADO\n(riesgo muy alto)")
    arrow(aprob, mensajes, "pide OK a\notro SRE", offset=(0, -30))
    cb_slack = box((C[4] + C[5]) / 2, R3, "CIRCUIT BREAKER\nretry", 150, 52, RED, "transparent", 11)
    arrow(mensajes, cb_slack, ""); arrow(cb_slack, slackapi, "")
    arrow(mensajes, email, "si Slack falla", offset=(55, 0))
    note(C[7], R3 + 62, "aprobado -> Acciones ejecuta\nsi nadie aprueba en 30 min, se cancela", 12, BLUE)
    note(C[8] - 60, R4 + 70, "solo SELECT · 1000 filas\ntimeout 10 s")
    # camino de un cambio de incidente
    arrow(app, incid, "/incident <id>\ncamino directo\n(sin LLM)", offset=(-120, 0))
    arrow(incid, bdinc, "guarda", offset=(0, -18)); arrow(bdinc, rep_sync, "sincrona ·\nfailover auto", offset=(0, -32))
    arrow(incid, cambios, "creado / cambiado\n/ cerrado", dashed=True, offset=(0, -32))
    arrow(cambios, estado, "actualiza", dashed=True, offset=(40, 0))
    arrow(cambios, sla, "plazos 1d / 3d", dashed=True, offset=(0, -18))
    arrow(cambios, audit, "todo queda\nregistrado", dashed=True, offset=(80, 0))
    note(C[3], R4 + 62, "tambien borra las Respuestas\nGuardadas de ese incidente", 12, BLUE)
    arrow(sla, mensajes, "alertas 50/80/100 %")
    arrow(sla, reportes, "")
    arrow(monit, panel, "semaforo", offset=(0, -16))
    arrow(reportes, panel, "")
    arrow(u_im, panel, "")
    note(C[3] + 170, R3 + 78, "riesgo alto: si no\nse actualiza"); note(C[1], R4 + 62, "riesgo alto: RPO 0")

    named = dict(u_sop=u_sop, u_sre=u_sre, u_im=u_im, u_adm=u_adm, registro=registro, usuarios=usuarios,
                 cb_llm=cb_llm, cb_slack=cb_slack, app=app, login=login, filtro=filtro, consulta=consulta, resp_g=resp_g,
                 contexto=contexto, estado=estado, hist=hist, conoc=conoc, cola=cola, llm1=llm1, llm2=llm2, revision=revision,
                 acciones=acciones, copia=copia, skills=skills, pruebas=pruebas, aprob=aprob, mensajes=mensajes, slackapi=slackapi, email=email,
                 incid=incid, bdinc=bdinc, rep_sync=rep_sync, cambios=cambios, sla=sla, reportes=reportes, panel=panel,
                 audit=audit, aprend=aprend, indexar=indexar, pruebasd=pruebasd, monit=monit)
    if focus:
        keep_ids = {t2["id"]}; groups = set(); order = {}
        skip_ids = {(named[a]["id"], named[b]["id"]) for a, b in skip}
        for i, name in enumerate(focus, 1):
            el = named[name]; keep_ids.add(el["id"]); order[el["id"]] = i
            groups.update(el.get("groupIds", []))
        for e in elements:
            if e["type"] == "arrow" and "_ends" in e and e["_ends"][0] in keep_ids and e["_ends"][1] in keep_ids and e["_ends"] not in skip_ids:
                keep_ids.add(e["id"]); e["strokeWidth"] = 4
                if "_label" in e: keep_ids.add(e["_label"])
        for e in elements:
            if e.get("containerId") in keep_ids: keep_ids.add(e["id"])
            if set(e.get("groupIds", [])) & groups: keep_ids.add(e["id"])
        for e in elements:
            if e["id"] not in keep_ids and e["y"] > 430:      # atenuar solo la iteración #2 (el resto queda legible)
                e["opacity"] = 22
            if e["id"] in order:
                r = e.get("_r"); x, y = (r[0], r[1]) if r else (e["x"], e["y"])
                n = text(0, 0, str(order[e["id"]]), 18, RED, "center", None, x - 6, y - 8)
                n["strokeColor"] = RED
    return None

# ───────────────────────── Salida ─────────────────────────
HP = {
 "harness": (None, None, []),
 "harness-hp1": (["u_sop", "app", "login", "filtro", "consulta", "resp_g", "contexto", "estado", "hist", "conoc", "skills", "cola", "cb_llm", "llm1", "revision", "acciones", "incid", "usuarios"],
                 "happy path 1 — soporte responde al cliente y escala (Diego)", [("app", "incid")]),
 "harness-hp2": (["u_sre", "app", "login", "filtro", "consulta", "contexto", "hist", "skills", "cola", "cb_llm", "llm1", "revision", "acciones", "copia", "aprob", "mensajes", "cb_slack", "slackapi", "usuarios"],
                 "happy path 2 — SRE ejecuta una query y una escritura aprobada (Valeria)", [("app", "incid")]),
 "harness-hp3": (["incid", "bdinc", "rep_sync", "cambios", "estado", "sla", "mensajes", "audit", "u_im", "app", "login", "filtro", "consulta", "reportes", "panel"],
                 "happy path 3 — se cierra un incidente y todos ven lo mismo (Marco)", []),
 "harness-sin-llm": (["u_sop", "app", "login", "filtro", "consulta", "estado", "resp_g", "incid"],
                 "camino de falla — el LLM no responde: respuesta sin LLM y /incident directo", []),
}
os.makedirs("Diagramas", exist_ok=True)
for name, (focus, title, skip) in HP.items():
    elements.clear(); _id = 0
    draw(focus, title, skip)
    for e in elements:
        for k in ("_c", "_kind", "_r", "_ends", "_label"): e.pop(k, None)
    xs = [e["x"] for e in elements] + [e["x"] + e["width"] for e in elements]
    ys = [e["y"] for e in elements] + [e["y"] + e["height"] for e in elements]
    doc = {"type": "excalidraw", "version": 2, "source": "https://excalidraw.com",
           "elements": elements, "appState": {"gridSize": None, "viewBackgroundColor": "#ffffff"}, "files": {}}
    with open(f"Diagramas/{name}.excalidraw", "w", encoding="utf-8") as f: json.dump(doc, f, ensure_ascii=False, indent=1)
    print(f"{name}: elements={len(elements)} bounds=({min(xs):.0f},{min(ys):.0f})-({max(xs):.0f},{max(ys):.0f})")

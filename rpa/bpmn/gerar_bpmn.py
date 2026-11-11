"""Gera os diagramas BPMN 2.0 (As-Is e To-Be) com posições (BPMN DI).

Os arquivos .bpmn abrem no Camunda Modeler, no bpmn.io e no Bizagi.
Para mudar um fluxo, edite as listas abaixo e rode: python3 gerar_bpmn.py
"""

from pathlib import Path
from xml.sax.saxutils import escape

TAM = {"start": (36, 36), "end": (36, 36), "task": (130, 80), "user": (130, 80),
       "service": (130, 80), "gateway": (50, 50), "timer": (36, 36), "data": (50, 60)}
TAG = {"start": "startEvent", "end": "endEvent", "task": "task", "user": "userTask",
       "service": "serviceTask", "gateway": "exclusiveGateway", "timer": "intermediateCatchEvent"}
X0, COL, LANE_H, POOL_X, LANE_X = 220, 170, 150, 120, 150


def gerar(nome, titulo, lanes, elementos, fluxos, arquivo):
    lane_y = {l: 80 + i * LANE_H for i, l in enumerate(lanes)}
    pos = {}
    for eid, tipo, _, lane, col in elementos:
        w, h = TAM[tipo]
        cx = X0 + col * COL
        pos[eid] = (cx - w / 2, lane_y[lane] + LANE_H / 2 - h / 2, w, h)
    largura = X0 + max(e[4] for e in elementos) * COL + 120 - LANE_X

    proc = []
    for eid, tipo, rotulo, _, _ in elementos:
        entra = [f for f in fluxos if f[1] == eid]
        sai = [f for f in fluxos if f[0] == eid]
        filhos = "".join(f"<bpmn:incoming>{f[0]}_{f[1]}</bpmn:incoming>" for f in entra)
        filhos += "".join(f"<bpmn:outgoing>{f[0]}_{f[1]}</bpmn:outgoing>" for f in sai)
        if tipo == "timer":
            filhos += f'<bpmn:timerEventDefinition id="{eid}_def"><bpmn:timeCycle xsi:type="bpmn:tFormalExpression">R/PT15M</bpmn:timeCycle></bpmn:timerEventDefinition>'
        proc.append(f'    <bpmn:{TAG[tipo]} id="{eid}" name="{escape(rotulo, {chr(34): "&quot;"})}">{filhos}</bpmn:{TAG[tipo]}>')
    for a, b, rotulo in fluxos:
        nome_attr = f' name="{escape(rotulo)}"' if rotulo else ""
        proc.append(f'    <bpmn:sequenceFlow id="{a}_{b}"{nome_attr} sourceRef="{a}" targetRef="{b}" />')
    lanes_xml = "".join(
        f'<bpmn:lane id="lane_{i}" name="{escape(l)}">'
        + "".join(f"<bpmn:flowNodeRef>{e[0]}</bpmn:flowNodeRef>" for e in elementos if e[3] == l)
        + "</bpmn:lane>"
        for i, l in enumerate(lanes)
    )

    di = [f'      <bpmndi:BPMNShape id="pool_di" bpmnElement="pool" isHorizontal="true"><dc:Bounds x="{POOL_X}" y="80" width="{largura + LANE_X - POOL_X}" height="{LANE_H * len(lanes)}" /></bpmndi:BPMNShape>']
    for i, l in enumerate(lanes):
        di.append(f'      <bpmndi:BPMNShape id="lane_{i}_di" bpmnElement="lane_{i}" isHorizontal="true"><dc:Bounds x="{LANE_X}" y="{lane_y[l]}" width="{largura}" height="{LANE_H}" /></bpmndi:BPMNShape>')
    for eid, tipo, *_ in elementos:
        x, y, w, h = pos[eid]
        extra = ' isMarkerVisible="true"' if tipo == "gateway" else ""
        di.append(f'      <bpmndi:BPMNShape id="{eid}_di" bpmnElement="{eid}"{extra}><dc:Bounds x="{x:.0f}" y="{y:.0f}" width="{w}" height="{h}" /></bpmndi:BPMNShape>')
    for a, b, _ in fluxos:
        ax, ay, aw, ah = pos[a]
        bx, by, bw, bh = pos[b]
        if bx > ax:  # para a frente
            p1, p2 = (ax + aw, ay + ah / 2), (bx, by + bh / 2)
            meio = (p1[0] + p2[0]) / 2
            pts = [p1, p2] if abs(p1[1] - p2[1]) < 1 else [p1, (meio, p1[1]), (meio, p2[1]), p2]
        elif abs(bx - ax) < 1:  # mesma coluna, outra raia
            de_cima = by > ay
            p1 = (ax + aw / 2, ay + ah if de_cima else ay)
            p2 = (bx + bw / 2, by if de_cima else by + bh)
            pts = [p1, p2]
        elif by > ay:  # volta para uma raia de baixo: sai pela esquerda e desce no destino
            pts = [(ax, ay + ah / 2), (bx + bw / 2, ay + ah / 2), (bx + bw / 2, by)]
        else:  # volta: passa por baixo das duas formas
            base = max(ay + ah, by + bh) + 25
            pts = [(ax + aw / 2, ay + ah), (ax + aw / 2, base), (bx + bw / 2, base), (bx + bw / 2, by + bh)]
        wps = "".join(f'<di:waypoint x="{x:.0f}" y="{y:.0f}" />' for x, y in pts)
        di.append(f'      <bpmndi:BPMNEdge id="{a}_{b}_di" bpmnElement="{a}_{b}">{wps}</bpmndi:BPMNEdge>')

    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL"
  xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI"
  xmlns:dc="http://www.omg.org/spec/DD/20100524/DC"
  xmlns:di="http://www.omg.org/spec/DD/20100524/DI"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  id="defs_{nome}" targetNamespace="https://github.com/zela/bpmn" exporter="gerar_bpmn.py" exporterVersion="1">
  <bpmn:collaboration id="colab">
    <bpmn:participant id="pool" name="{escape(titulo)}" processRef="proc_{nome}" />
  </bpmn:collaboration>
  <bpmn:process id="proc_{nome}" name="{escape(titulo)}" isExecutable="false">
    <bpmn:laneSet id="lanes">{lanes_xml}</bpmn:laneSet>
{chr(10).join(proc)}
  </bpmn:process>
  <bpmndi:BPMNDiagram id="diagrama">
    <bpmndi:BPMNPlane id="plano" bpmnElement="colab">
{chr(10).join(di)}
    </bpmndi:BPMNPlane>
  </bpmndi:BPMNDiagram>
</bpmn:definitions>
'''
    Path(arquivo).write_text(xml, encoding="utf-8")


AQUI = Path(__file__).parent

# ---------------------------------------------------------------- As-Is
gerar(
    "as_is", "As-Is: relato de dano na via sem o Zela",
    ["Cidadão", "Equipe de zeladoria", "Portal de manutenção"],
    [
        ("a_ini", "start", "Vê um dano na via", "Cidadão", 0),
        ("a_msg", "task", "Manda mensagem (WhatsApp, e-mail ou conversa)", "Cidadão", 1),
        ("a_ler", "user", "Lê a mensagem e tenta entender o local", "Equipe de zeladoria", 2),
        ("a_gw", "gateway", "Tem foto e local claros?", "Equipe de zeladoria", 3),
        ("a_resp", "task", "Recebe pedido de foto ou referência e responde (às vezes não)", "Cidadão", 3),
        ("a_dig", "user", "Redigita local, tipo e descrição e anexa a foto", "Equipe de zeladoria", 4),
        ("a_os", "service", "Registra a ordem de serviço", "Portal de manutenção", 5),
        ("a_anota", "user", "Anota o número à parte (planilha ou papel)", "Equipe de zeladoria", 6),
        ("a_fim", "end", "Cidadão não sabe se foi encaminhado", "Cidadão", 7),
    ],
    [
        ("a_ini", "a_msg", ""), ("a_msg", "a_ler", ""), ("a_ler", "a_gw", ""),
        ("a_gw", "a_dig", "sim"), ("a_gw", "a_resp", "não: pede foto ou local"),
        ("a_resp", "a_ler", ""), ("a_dig", "a_os", ""), ("a_os", "a_anota", ""), ("a_anota", "a_fim", ""),
    ],
    AQUI / "as_is.bpmn",
)

# ---------------------------------------------------------------- To-Be
gerar(
    "to_be", "To-Be: relato pelo Zela com encaminhamento por robô",
    ["Cidadão", "Zela (app + API)", "Equipe de triagem", "Robô UiPath", "Portal de manutenção"],
    [
        ("t_ini", "start", "Vê um dano na via e lê o QR", "Cidadão", 0),
        ("t_env", "task", "Envia foto e local pelo app", "Cidadão", 1),
        ("t_cv", "service", "Visão sugere dano na pista, gera protocolo", "Zela (app + API)", 2),
        ("t_conf", "task", "Confirma ou corrige a categoria", "Cidadão", 3),
        ("t_fila", "service", "Relato fica como recebido", "Zela (app + API)", 4),
        ("t_tri", "user", "Revisa foto, local e categoria no painel", "Equipe de triagem", 5),
        ("t_gw", "gateway", "Relato válido?", "Equipe de triagem", 6),
        ("t_desc", "end", "Descartado (duplicado, fora do território)", "Equipe de triagem", 7),
        ("t_tim", "timer", "A cada 15 min", "Robô UiPath", 7),
        ("t_get", "service", "Lê GET /robo/reports em triagem", "Robô UiPath", 8),
        ("t_form", "service", "Preenche formulário e anexa a foto", "Robô UiPath", 9),
        ("t_os", "service", "Gera número da ordem de serviço", "Portal de manutenção", 10),
        ("t_patch", "service", "Grava OS via PATCH /robo/reports/{id}/service-order", "Robô UiPath", 11),
        ("t_enc", "service", "Status vira encaminhado", "Zela (app + API)", 12),
        ("t_fim", "end", "Cidadão vê 'Encaminhado' pelo protocolo", "Cidadão", 13),
    ],
    [
        ("t_ini", "t_env", ""), ("t_env", "t_cv", ""), ("t_cv", "t_conf", ""), ("t_conf", "t_fila", ""),
        ("t_fila", "t_tri", ""), ("t_tri", "t_gw", ""), ("t_gw", "t_desc", "não"), ("t_gw", "t_tim", "sim: em_triagem"),
        ("t_tim", "t_get", ""), ("t_get", "t_form", ""), ("t_form", "t_os", ""), ("t_os", "t_patch", ""),
        ("t_patch", "t_enc", ""), ("t_enc", "t_fim", ""),
    ],
    AQUI / "to_be.bpmn",
)
print("as_is.bpmn e to_be.bpmn gerados")

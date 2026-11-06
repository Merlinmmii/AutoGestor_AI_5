import streamlit as st
import psutil
import os
import json
import time
import datetime
import threading
import edge_tts
import asyncio
import tempfile
import graphviz

# --- IMPORTACIÓN SEGURA DE NVIDIA ---
# Intentamos usar la librería nueva (nvidia-ml-py), si no, caemos en la antigua (pynvml)
try:
    import nvidia_ml_py as pynvml
    pynvml_installed = True
except ImportError:
    try:
        import pynvml
        pynvml_installed = True
    except ImportError:
        pynvml = None
        pynvml_installed = False

import importlib.util

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="AutoGestor AI 5.0", layout="wide")

# Traducciones (ES, EN, FR)
T = {
    "es": {
        "title": "🍃 AutoGestor AI 5.0",
        "gov": "🧠 Gobernador",
        "design": "🎨 Diseñador",
        "lib": "📚 Biblioteca",
        "lang": "Idioma",
        "limits": "Límites",
        "cpu": "CPU (%)", "mem": "RAM (%)", "temp": "Temp (°C)",
        "monitor": "Monitor",
        "cpu_v": "CPU", "mem_v": "RAM", "temp_v": "Temp", "gpu_v": "GPU",
        "restart": "🔄 Reiniciar",
        "execute": "▶️ Ejecutar",
        "prompt": "Comando",
        "logs": "📝 Logs del Sistema", # <-- ETIQUETA CORREGIDA AQUÍ
        "workflow": "🌐 Diseño Visual",
        "node_name": "Nombre",
        "node_type": "Tipo",
        "add_node": "Agregar",
        "add_edge": "Conectar",
        "run_graph": "Ejecutar",
        "safe": "✅ Seguro",
        "paused": "⏸️ Pausado",
        "resumed": "🔁 Retomado",
        "library_scripts": "📂 Scripts",
        "empty_lib": "Sin scripts.",
        "generate_sample": "Crear Script"
    },
    "en": {
        "title": "🍃 AutoGestor AI 5.0",
        "gov": "🧠 Governor",
        "design": "🎨 Designer",
        "lib": "📚 Library",
        "lang": "Language",
        "limits": "Limits",
        "cpu": "CPU (%)", "mem": "RAM (%)", "temp": "Temp (°C)",
        "monitor": "Monitor",
        "cpu_v": "CPU", "mem_v": "RAM", "temp_v": "Temp", "gpu_v": "GPU",
        "restart": "🔄 Restart",
        "execute": "▶️ Execute",
        "prompt": "Command",
        "logs": "📝 System Logs",
        "workflow": "🌐 Visual Design",
        "node_name": "Name",
        "node_type": "Type",
        "add_node": "Add",
        "add_edge": "Connect",
        "run_graph": "Run",
        "safe": "✅ Safe",
        "paused": "⏸️ Paused",
        "resumed": "🔁 Resumed",
        "library_scripts": "📂 Scripts",
        "empty_lib": "No scripts.",
        "generate_sample": "Create Script"
    },
    "fr": {
        "title": "🍃 AutoGestor AI 5.0",
        "gov": "🧠 Gouverneur",
        "design": "🎨 Concepteur",
        "lib": "📚 Bibliothèque",
        "lang": "Langue",
        "limits": "Limites",
        "cpu": "CPU (%)", "mem": "RAM (%)", "temp": "Temp (°C)",
        "monitor": "Moniteur",
        "cpu_v": "CPU", "mem_v": "RAM", "temp_v": "Temp", "gpu_v": "GPU",
        "restart": "🔄 Redémarrer",
        "execute": "▶️ Exécuter",
        "prompt": "Commande",
        "logs": "📝 Logs Système",
        "workflow": "🌐 Conception Visuelle",
        "node_name": "Nom",
        "node_type": "Type",
        "add_node": "Ajouter",
        "add_edge": "Connecter",
        "run_graph": "Exécuter",
        "safe": "✅ Sûr",
        "paused": "⏸️ En Pause",
        "resumed": "🔁 Repris",
        "library_scripts": "📂 Scripts",
        "empty_lib": "Pas de scripts.",
        "generate_sample": "Créer Script"
    }
}

if "language" not in st.session_state:
    st.session_state.language = "es"

lang = st.session_state.language
t = T[lang]

# --- ESTADO Y PERSISTENCIA ---
STATE_FILE = "auto_state.json"
if "logs" not in st.session_state: st.session_state.logs = []
if "workflow_step" not in st.session_state: st.session_state.workflow_step = 0
if "is_paused" not in st.session_state: st.session_state.is_paused = False
if "nodes" not in st.session_state: st.session_state.nodes = []
if "edges" not in st.session_state: st.session_state.edges = []

# Cargar estado previo
if os.path.exists(STATE_FILE):
    try:
        with open(STATE_FILE, "r") as f:
            saved = json.load(f)
            st.session_state.workflow_step = saved.get("step", 0)
            st.session_state.nodes = saved.get("nodes", [])
            st.session_state.edges = saved.get("edges", [])
            st.session_state.logs.append(f"[{t['resumed']}] Estado cargado.")
    except: pass

def save_state():
    with open(STATE_FILE, "w") as f:
        json.dump({
            "step": st.session_state.workflow_step,
            "nodes": st.session_state.nodes,
            "edges": st.session_state.edges
        }, f)
save_state()

# --- MONITOR DE RECURSOS ---
stats = {"cpu": 0, "mem": 0, "temp": 0, "gpu": 0}
limits = {"cpu": 75, "mem": 75, "temp": 80}

def monitor_loop():
    global stats
    while True:
        try:
            stats["cpu"] = psutil.cpu_percent(interval=0.2)
            stats["mem"] = psutil.virtual_memory().percent
            temps = psutil.sensors_temperatures()
            current_temps = []
            for cat in temps.values():
                for entry in cat:
                    current_temps.append(entry.current)
            stats["temp"] = max(current_temps) if current_temps else 0
            
            # GPU Monitor
            if pynvml_installed and pynvml:
                try:
                    pynvml.nvmlInit()
                    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                    stats["gpu"] = pynvml.nvmlDeviceGetUtilizationRates(handle).gpu
                except:
                    stats["gpu"] = 0
            else:
                stats["gpu"] = 0
                
        except: pass
        time.sleep(0.5)

threading.Thread(target=monitor_loop, daemon=True).start()

# --- UI PRINCIPAL ---
st.title(t["title"])
st.sidebar.selectbox(t["lang"], ["es", "en", "fr"], index=["es","en","fr"].index(lang), 
                     key="language", on_change=lambda: st.rerun())

tab1, tab2, tab3 = st.tabs([t["gov"], t["design"], t["lib"]])

# === TAB 1: GOBERNADOR ===
with tab1:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader(t["monitor"])
        st.metric(t["cpu_v"], f"{stats['cpu']:.1f}%")
        st.metric(t["mem_v"], f"{stats['mem']:.1f}%")
        st.metric(t["temp_v"], f"{stats['temp']:.1f}°C")
        st.metric(t["gpu_v"], f"{stats['gpu']:.1f}%")
        
        st.subheader(t["limits"])
        limits["cpu"] = st.slider(t["cpu"], 0, 100, limits["cpu"])
        limits["mem"] = st.slider(t["mem"], 0, 100, limits["mem"])
        limits["temp"] = st.slider(t["temp"], 50, 95, limits["temp"])
        
        st.divider()
        inp = st.text_input(t["prompt"])
        if st.button(t["execute"], type="primary"):
            st.session_state.is_paused = False
            st.session_state.workflow_step = 0
            st.session_state.logs.append(f"[INICIO] Ejecutando: {inp}")
            time.sleep(0.5)
            
            for i in range(3):
                if st.session_state.is_paused: break
                
                st.session_state.logs.append(f"[PASO {i+1}] Procesando...")
                
                status = "SAFE"
                if stats["cpu"] > limits["cpu"]: status = "HIGH_CPU"
                elif stats["mem"] > limits["mem"]: status = "HIGH_MEM"
                elif stats["temp"] > limits["temp"]: status = "CRITICAL"
                
                if status != "SAFE":
                    st.session_state.is_paused = True
                    st.session_state.logs.append(f"[{t['paused']}] {status}")
                    time.sleep(3)
                    st.session_state.logs.append(f"[{t['safe']}] Recuperado.")
                else:
                    time.sleep(1.5)
                    st.session_state.logs.append(f"✅ {t['safe']}")
                
                st.session_state.workflow_step = i
                save_state()
                
            st.session_state.logs.append("🏁 Tarea terminada.")
            st.rerun()

    with c2:
        st.subheader(t["restart"])
        if st.button("🔄 Forzar Retomar"):
            st.session_state.is_paused = False
            st.rerun()
        
        st.subheader(t["logs"])
        # CORRECCIÓN DE ERROR: Etiqueta t["logs"]
        st.text_area(t["logs"], value="\n".join(st.session_state.logs[-15:]), height=350)

# === TAB 2: DISEÑADOR (GRÁFICO) ===
with tab2:
    st.markdown(f"### {t['workflow']}")
    
    c_n1, c_n2 = st.columns(2)
    with c_n1:
        nid = st.text_input(t["node_name"])
        nname = st.text_input(t["label_node_name"]) if "label_node_name" in t else t["node_name"] # Fallback
        ntype = st.selectbox(t["node_type"], ["Executor", "LLM", "Data"])
    with c_n2:
        src = st.selectbox(t["add_edge"]+" (Origen)", [n["id"] for n in st.session_state.nodes], key="src") if st.session_state.nodes else ""
        tgt = st.selectbox(t["add_edge"]+" (Destino)", [n["id"] for n in st.session_state.nodes if n["id"] != src], key="tgt") if st.session_state.nodes else ""
        
        if st.button(t["add_node"]):
            if nid and nname:
                st.session_state.nodes.append({"id": nid, "name": nname, "type": ntype})
                save_state()
                st.rerun()
        
        if src and tgt and st.button("➕ Conectar"):
            if not any(e["src"]==src and e["tgt"]==tgt for e in st.session_state.edges):
                st.session_state.edges.append({"src": src, "tgt": tgt})
                save_state()
                st.rerun()

    st.divider()
    if st.session_state.nodes:
        dot = graphviz.Digraph("Flow")
        dot.attr(rankdir="LR", bgcolor="#1e1e1e", fontcolor="white")
        for n in st.session_state.nodes:
            color = "#4CAF50" if n["type"]=="Executor" else "#2196F3" if n["type"]=="LLM" else "#FF9800"
            dot.node(n["id"], f"{n['name']}\n({n['type']})", shape="box", style="filled", fillcolor=color, fontcolor="white")
        for e in st.session_state.edges:
            dot.edge(e["src"], e["tgt"], color="white", penwidth="2")
        st.graphviz_chart(dot)
    else:
        st.info(t["add_node"])

# === TAB 3: BIBLIOTECA ===
with tab3:
    st.subheader(t["library_scripts"])
    lib_dir = "library_scripts"
    os.makedirs(lib_dir, exist_ok=True)
    scripts = [f for f in os.listdir(lib_dir) if f.endswith(".py")]
    
    if not scripts:
        st.warning(t["empty_lib"])
    else:
        for s in scripts:
            st.success(f"📄 {s}")
            
    if st.button(t["generate_sample"]):
        with open(os.path.join(lib_dir, "sample_handler.py"), "w") as f:
            f.write('''
def execute(query):
    return f"🔌 Script de biblioteca procesó: {query}"
''')
        st.success("Script creado.")

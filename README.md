# 🍃 AutoGestor AI 5.0
**Self-Evolving Voice & Resource-Governed AI Platform**

[![Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![Pinokio Ready](https://img.shields.io/badge/Ready-Pinokio-orange)](https://pinokio.computer)

---

## 📖 Descripción
**AutoGestor AI 5.0** es una plataforma autónoma diseñada para ejecutarse localmente mediante **Pinokio**. Funciona como un "Gobernador" central que orestra agentes, genera plugins dinámicamente usando IA local (Ollama), monitoriza recursos en tiempo real (CPU, RAM, GPU, Temperatura) y permite el diseño visual de workflows. Todo con soporte multilenguaje, interacción por voz y persistencia de estado.

## ✨ Características Principales
- 🌍 **Multilenguaje:** Interfaz completa en Español, Inglés y Francés.
- 🎙️ **Interacción por Voz:** Síntesis de voz neural (Edge TTS) + entrada por teclado/micrófono.
- 🧠 **Plugins Auto-Generados:** Si falta un plugin, el Gobernador solicita a Ollama que genere el código Python en tiempo real y lo guarda en memoria.
- 📊 **Gobernador Eco-Inteligente:** Límites ajustables (0-100%) para CPU, RAM y GPU. Pausa automática si la temperatura supera el umbral (ej. 80°C) y reanuda cuando es seguro.
- 📁 **Biblioteca de Scripts:** Los plugins generados se guardan en `library_scripts/` para reutilización en futuros workflows.
- 🎨 **Diseñador Visual de Workflows:** Editor de nodos y aristas renderizado con Graphviz.
- 💾 **Persistencia:** Guarda el progreso exacto, nodos, conexiones y logs en `auto_state.json`.

## 🛠️ Prerrequisitos
1. **Pinokio** instalado en tu sistema.
2. **Python 3.10+** (se instala automáticamente con Pinokio).
3. **Ollama** corriendo localmente en `http://127.0.0.1:11434` *(Opcional, pero necesario para la auto-generación de plugins)*.
4. Tarjeta GPU NVIDIA (Opcional, para monitorización de `nvidia-ml-py`).
5. `graphviz` instalado en el sistema operativo.

## 📦 Instalación (Vía Pinokio)
1. Descarga o clona este repositorio en tu PC.
2. Abre **Pinokio** → Haz clic en **Install Script**.
3. Selecciona la carpeta `AutoGestor_AI_5`.
4. Pinokio leerá `install.json`, instalará `streamlit`, `psutil`, `edge-tts`, `graphviz` y lanzará la app.
5. La plataforma se abrirá automáticamente en `http://localhost:8501`.

## 📂 Estructura del Proyecto

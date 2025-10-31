# 🛰️ AI-Powered Network Diagnostics System

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/FastAPI-0.110+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![AI Model](https://img.shields.io/badge/NVIDIA-Nemotron-76B900?logo=nvidia&logoColor=white)](https://developer.nvidia.com/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Project-Active-success)](#)

---

> This project aims to enhance communication stability for remote workers.  
> It monitors and analyzes network issues using **AI-driven diagnostics**, then provides clear, step-by-step guidance to users without technical expertise.  
> The AI acts as a domain expert, handling complex technical analysis while enabling non-technical users to implement effective solutions easily.

---

### 👥 Creators  
**@cyberbryanzhang**, **@dev-tomnorris**, **@fourold**  
📧 *Questions?* Email: **cyber.bryanzhang@gmail.com**

---

## 🧭 Overview

This project demonstrates a **multi-agent AI system** that monitors and diagnoses network performance in real time using **NVIDIA Nemotron reasoning models**.

It consists of:
- **Network Data API (FastAPI)** → Simulates real-time network metrics.  
- **Monitoring Agent** → Observes network data and identifies anomalies.  
- **Diagnostic Agent** → Determines the most probable root cause using Nemotron reasoning.  

All agents communicate via **local HTTP endpoints** and share the same **NVIDIA NIM API key**.

```
+---------------------+       +--------------------+       +---------------------+
| Network Data API    | --->  | Monitoring Agent   | --->  | Diagnostic Agent    |
| (FastAPI, port 8000)|       | (Nemotron reasoning)|       | (Nemotron reasoning)|
+---------------------+       +--------------------+       +---------------------+
        ^                                                         |
        |                                                         v
        +-------------------< Shared .env (API key) >-------------+
```

---

## ⚙️ Requirements

### 🐍 Python Version  
- Python **3.10+** (✅ 3.13 works fine)

---

## 📦 Installation & Running

### Install Dependencies
```bash
pip install fastapi uvicorn openai python-dotenv requests
```

### Run API Endpoints for Demonstration and Agents
```bash
uvicorn network_data:app --reload --port 8000
python diagnostic-agent.py
```

### Run Monitoring Agent to Create Network Diagnosis
```bash
python nemotron-monitoring.py
```

---

## 🧩 Tech Keywords
**FastAPI**, **NVIDIA Nemotron**, **Multi-Agent System**, **Network Diagnostics**, **AI Reasoning**, **Python 3.10+**

---

<div align="center">

🧠 *AI Reasoning Engine* | 🧩 *Multi-Agent Architecture* | ☁️ *Network Stability for Remote Teams*  

Licensed under the [Apache 2.0 License](LICENSE)

</div>

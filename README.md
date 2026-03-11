# ⚡ Secure Local-Agentic Vision (SLAV) for P&ID Digitization

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.10-blue.svg?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/PyTorch-CUDA_11.8-ee4c2c.svg?logo=pytorch&logoColor=white" alt="PyTorch">
  <img src="https://img.shields.io/badge/Model-Florence--2--Large-0078D4.svg?logo=microsoft&logoColor=white" alt="Florence-2">
  <img src="https://img.shields.io/badge/Vector_DB-ChromaDB-FF6F00.svg?logo=database&logoColor=white" alt="ChromaDB">
  <img src="https://img.shields.io/badge/Status-Hackathon_Ready-success.svg" alt="Status">
</div>

<br>

> **An offline, GPU-accelerated Agentic AI pipeline to autonomously detect, classify, and extract engineering symbols from complex Piping and Instrumentation Diagrams (P&IDs) with 100% data privacy.**

---

## 📖 Overview
Digitizing P&IDs is a notoriously manual, time-consuming, and error-prone process. While existing cloud-based GenAI solutions exist, they pose massive **Intellectual Property (IP) and security risks** by sending sensitive enterprise schematics to third-party APIs. 

**Our Solution:** A completely offline, Edge-AI Agent. It utilizes **Microsoft's Florence-2** as the "Eyes" for zero-shot object detection, and a **ChromaDB Vector Database** as the "Brain" to verify detections against ISA-5.1 standards. The output is a highly accurate, structured Bill of Materials (Excel/XML) ready for Digital Twin integration.

## ✨ Key Features
* 🔒 **100% Data Privacy (Air-Gapped):** Runs entirely locally on an NVIDIA GPU. No API keys, no cloud calls, zero data leakage.
* 🚀 **High-Performance Inference:** Optimized with `torch.float16` and CUDA. Processes high-resolution document tiles in sub-seconds.
* 🧠 **Hybrid Agentic Workflow (Visual RAG):** Combines Generative Vision (Florence-2) with Semantic Vector Search (CLIP + ChromaDB) to eliminate AI hallucinations.
* 🎯 **One-Shot Self-Learning:** Teach the AI a new custom symbol simply by dropping a single PNG image into a folder. The Vector DB indexes it instantly—**no model retraining required.**
* 📊 **Enterprise-Ready Output:** Automatically stitches coordinates and generates standardized `XML` and `Excel (XLSX)` reports.

---

## 🏗️ System Architecture

Our pipeline decouples *Detection* from *Identification* to ensure high accuracy.

```mermaid
graph TD
    classDef input fill:#2b303a,stroke:#01579b,stroke-width:2px,color:#fff;
    classDef ai fill:#004d40,stroke:#2e7d32,stroke-width:2px,color:#fff;
    classDef output fill:#e65100,stroke:#ef6c00,stroke-width:2px,color:#fff;
    classDef db fill:#4a148c,stroke:#7b1fa2,stroke-width:2px,color:#fff,stroke-dasharray: 5 5;

    A(📄 Raw P&ID PDF) --> B[⚙️ Intelligent Tiling<br/>High-DPI Overlapping Grids]
    B --> C{👁️ The EYES<br/>Florence-2-Large on GPU}
    
    C -- Proposes Bounding Box --> D[✂️ Crop Detected Region]
    D --> E[(🧠 The BRAIN<br/>ChromaDB + CLIP Embeddings)]
    
    E -- Compares crop to ISA Standards --> F{Semantic Verification}
    
    F -- Distance < 65% --> G[✅ Label Confirmed & Refined]
    F -- Distance > 65% --> H[⚠️ Generic AI Label]
    
    G --> I[🔗 Coordinate Stitching]
    H --> I
    
    I --> J[📊 Export: XML & Excel BOM]

    %% Applying Styles
    class A,B input;
    class C,D,F,G,H ai;
    class I,J output;
    class E db;

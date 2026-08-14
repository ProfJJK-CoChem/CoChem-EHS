# 🧪 CoChem-EHS (Environmental Health & Safety Core)

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/release/python-3100/)
[![GitHub Actions Status](https://img.shields.io/badge/GitHub%20Actions-Serverless-2088FF.svg)](#)
[![Gemini API](https://img.shields.io/badge/Powered_by-Gemini_1.5_Pro-orange.svg)](#)
[![Compliance](https://img.shields.io/badge/Compliance-OSHA%20%7C%20EPA%20%7C%20TDEC-success.svg)](#)

**CoChem-EHS** is the serverless backend orchestration engine for the Cumberland University Sciences division. Designed to operate entirely within free-tier educational limits, this repository bridges Google Workspace apps with the Gemini 1.5 Pro multimodal LLM via GitHub Actions. It removes administrative friction from faculty workflows while mathematically ensuring strict federal and state safety compliance.

---

## 🏛️ System Architecture: The 4 Pillars

This repository contains the event-driven Python logic and GitHub Action workflows for the four core pillars of the Cumberland EHS v2.0 System:

### 1. Automated Intake ("Snap & Store") 📸
*   **Trigger:** Google Form Webhook / Scheduled Poll.
*   **Action:** Faculty upload a photo of a new chemical label. `intake_processor.py` uses Gemini Vision to extract the Chemical Name, CAS, Volume, and Vendor.
*   **Safety Lock:** The extracted CAS is cross-referenced deterministically against `flinn_logic_matrix.csv` to assign the proper physical Flinn storage shelf (e.g., *Organic #2*). 
*   **Output:** Appends data to the Master Inventory Google Sheet, fetches the digital SDS, and emails physical storage instructions to the submitter.

### 2. Frictionless Waste Management ("Smart Tag") 🗑️
*   **Trigger:** Google Form Webhook / Scheduled Poll.
*   **Action:** Faculty dictate waste additions via smartphone. `waste_processor.py` uses Gemini NLP to parse the chemical constituents and volumes. It then applies strict EPA RCRA mixture rules to generate hazard codes (D, F, P, U lists).
*   **Output:** `reportlab` dynamically generates a fully compliant PDF Waste Tag and emails it directly to the prep-room network printer.

### 3. SDS Compliance ("Closed-Loop Batch") 🗂️
*   **Trigger:** Cron Job (`0 8 * * 5` - Fridays at 8:00 AM).
*   **Action:** `sds_batch.py` fetches pending SDS PDFs, extracts only the English OSHA 16-section pages via `PyPDF2` (saving toner), and merges them into a single printable packet.
*   **Deployment:** Generates a dynamic QR-coded Cover Sheet. Student workers print the packet, place it in the physical Yellow Binders, and scan the QR code to digitally finalize the OSHA compliance loop.

### 4. Automated Auditing ("Proof-of-Presence") 🔎
*   **Trigger:** Cron Job (Start/End of Semesters) & Form Webhook.
*   **Action:** Faculty upload photos of critical safety infrastructure (e.g., flowing eyewash, open carboy). `audit_validator.py` checks the EXIF `DateTimeOriginal` via `Pillow` to prevent uploading old photos (stopping "pencil-whipping"), while Gemini Vision visually verifies the image contents. 
*   **Output:** Fraudulent audits are automatically rejected. Validated audits write a timestamped verification to the Admin Google Sheet.

---

## 📂 Repository Structure

```text
CoChem-EHS/
│
├── .devcontainer/                # GitHub Codespaces configuration
│   └── devcontainer.json
│
├── .github/
│   └── workflows/                # GitHub Actions CI/CD pipelines
│       ├── intake_webhook.yml
│       ├── waste_webhook.yml
│       ├── sds_friday_batch.yml
│       └── audit_validator.yml
│
├── src/                          # Core Python Logic
│   ├── intake_processor.py
│   ├── waste_processor.py
│   ├── sds_batch.py
│   ├── audit_validator.py
│   └── utils/
│       ├── gcp_auth.py           # Google Drive/Sheets/Gmail API wrappers
│       ├── gemini_client.py      # Gemini 1.5 Pro API wrappers
│       └── pdf_generator.py      # ReportLab layout templates
│
├── data/
│   └── flinn_logic_matrix.csv    # Static database mapping CAS to Flinn Shelves
│
├── tests/                        # Adversarial test payloads
│
├── requirements.txt              # Python dependencies
└── README.md
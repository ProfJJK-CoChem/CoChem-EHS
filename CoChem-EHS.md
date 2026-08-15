Here are the repository details and the complete README.md file to initialize your backend environment in GitHub.

### **Repository Name**

CoChem-EHS

### **Repository Description**

*Serverless Python backend for Cumberland University's Automated Environmental Health & Safety (EHS) system. Integrates Google Workspace, Gemini 1.5 Pro, and GitHub Actions for zero-friction chemical inventory, waste RCRA compliance, closed-loop SDS deployment, and verifiable lab auditing.*

### **README.md**

Markdown  
\# 🧪 CoChem-EHS (Environmental Health & Safety Core)

\[\!\[Python 3.10+\](https://img.shields.io/badge/python-3.10+-blue.svg)\](https://www.python.org/downloads/release/python-3100/)  
\[\!\[GitHub Actions Status\](https://img.shields.io/badge/GitHub%20Actions-Serverless-2088FF.svg)\](\#)  
\[\!\[Gemini API\](https://img.shields.io/badge/Powered\_by-Gemini\_1.5\_Pro-orange.svg)\](\#)  
\[\!\[Compliance\](https://img.shields.io/badge/Compliance-OSHA%20%7C%20EPA%20%7C%20TDEC-success.svg)\](\#)

**\*\*CoChem-EHS\*\*** is the serverless backend orchestration engine for the Cumberland University Sciences division. Designed to operate entirely within free-tier educational limits, this repository bridges Google Workspace apps with the Gemini 1.5 Pro multimodal LLM via GitHub Actions. It removes administrative friction from faculty workflows while mathematically ensuring strict federal and state safety compliance.

\---

\#\# 🏛️ System Architecture: The 4 Pillars

This repository contains the event-driven Python logic and GitHub Action workflows for the four core pillars of the Cumberland EHS v2.0 System:

\#\#\# 1\. Automated Intake ("Snap & Store") 📸  
\*   **\*\*Trigger:\*\*** Google Form Webhook / Scheduled Poll.  
\*   **\*\*Action:\*\*** Faculty upload a photo of a new chemical label. \`intake\_processor.py\` uses Gemini Vision to extract the Chemical Name, CAS, Volume, and Vendor.  
\*   **\*\*Safety Lock:\*\*** The extracted CAS is cross-referenced deterministically against \`flinn\_logic\_matrix.csv\` to assign the proper physical Flinn storage shelf (e.g., *\*Organic \#2\**).   
\*   **\*\*Output:\*\*** Appends data to the Master Inventory Google Sheet, fetches the digital SDS, and emails physical storage instructions to the submitter.

\#\#\# 2\. Frictionless Waste Management ("Smart Tag") 🗑️  
\*   **\*\*Trigger:\*\*** Google Form Webhook / Scheduled Poll.  
\*   **\*\*Action:\*\*** Faculty dictate waste additions via smartphone. \`waste\_processor.py\` uses Gemini NLP to parse the chemical constituents and volumes. It then applies strict EPA RCRA mixture rules to generate hazard codes (D, F, P, U lists).  
\*   **\*\*Output:\*\*** \`reportlab\` dynamically generates a fully compliant PDF Waste Tag and emails it directly to the prep-room network printer.

\#\#\# 3\. SDS Compliance ("Closed-Loop Batch") 🗂️  
\*   **\*\*Trigger:\*\*** Cron Job (\`0 8 \* \* 5\` \- Fridays at 8:00 AM).  
\*   **\*\*Action:\*\*** \`sds\_batch.py\` fetches pending SDS PDFs, extracts only the English OSHA 16-section pages via \`PyPDF2\` (saving toner), and merges them into a single printable packet.  
\*   **\*\*Deployment:\*\*** Generates a dynamic QR-coded Cover Sheet. Student workers print the packet, place it in the physical Yellow Binders, and scan the QR code to digitally finalize the OSHA compliance loop.

\#\#\# 4\. Automated Auditing ("Proof-of-Presence") 🔎  
\*   **\*\*Trigger:\*\*** Cron Job (Start/End of Semesters) & Form Webhook.  
\*   **\*\*Action:\*\*** Faculty upload photos of critical safety infrastructure (e.g., flowing eyewash, open carboy). \`audit\_validator.py\` checks the EXIF \`DateTimeOriginal\` via \`Pillow\` to prevent uploading old photos (stopping "pencil-whipping"), while Gemini Vision visually verifies the image contents.   
\*   **\*\*Output:\*\*** Fraudulent audits are automatically rejected. Validated audits write a timestamped verification to the Admin Google Sheet.

\---

\#\# 📂 Repository Structure

\`\`\`text  
CoChem-EHS/  
│  
├── .devcontainer/                \# GitHub Codespaces configuration  
│   └── devcontainer.json  
│  
├── .github/  
│   └── workflows/                \# GitHub Actions CI/CD pipelines  
│       ├── intake\_webhook.yml  
│       ├── waste\_webhook.yml  
│       ├── sds\_friday\_batch.yml  
│       └── audit\_validator.yml  
│  
├── src/                          \# Core Python Logic  
│   ├── intake\_processor.py  
│   ├── waste\_processor.py  
│   ├── sds\_batch.py  
│   ├── audit\_validator.py  
│   └── utils/  
│       ├── gcp\_auth.py           \# Google Drive/Sheets/Gmail API wrappers  
│       ├── gemini\_client.py      \# Gemini 1.5 Pro API wrappers  
│       └── pdf\_generator.py      \# ReportLab layout templates  
│  
├── data/  
│   └── flinn\_logic\_matrix.csv    \# Static database mapping CAS to Flinn Shelves  
│  
├── tests/                        \# Adversarial test payloads  
│  
├── requirements.txt              \# Python dependencies  
└── README.md

## **⚙️ Setup & Deployment Environment**

This repository is designed to be developed entirely within **GitHub Codespaces** and executed via **GitHub Actions**. No local servers are required.

### **1\. Environment Variables & Secrets**

To run this infrastructure, you must provision the following in your **GitHub Repository Secrets** (Settings \> Secrets and variables \> Actions):

* GEMINI\_API\_KEY: Your API key generated from Google AI Studio.  
* GCP\_CREDENTIALS: The raw JSON key for your Google Cloud Service Account (must have access to Sheets, Drive, and Gmail APIs).  
* PRINTER\_EMAIL: The HP ePrint (or equivalent) email address for the MH303 Prep-Room printer.  
* INVENTORY\_SHEET\_ID: The Google Sheet ID for the Master Inventory.  
* WASTE\_SHEET\_ID: The Google Sheet ID for the Waste Log.

### **2\. Local Development (Codespaces)**

> 1. Click the green **\<\> Code** button and select **Create codespace on main**.  
> 2. The .devcontainer will automatically install the necessary Python 3.10+ environment.  
> 3. Install dependencies manually if running locally outside of Codespaces:  
>    Bash  
>    pip install \-r requirements.txt

### **3\. Google Workspace Connectivity**

Ensure the Service Account email generated in GCP is explicitly shared as an "Editor" on the Master Inventory Google Sheet, the Waste Log Google Sheet, and the CU Sciences EHS Shared Google Drive.

## **🛡️ Security & Anti-Hallucination Protocol**

**DO NOT rely on Large Language Models (LLMs) for physical safety protocols.**  
In this repository, Gemini 1.5 Pro is strictly quarantined to optical character extraction (OCR) and natural language parsing (NLP). All physical safety routing—such as determining chemical incompatibilities or identifying proper Flinn storage shelves—is executed by standard Python logic querying the deterministic, human-verified data/flinn\_logic\_matrix.csv.  
**Offline Access:** Ensure the Google Drive desktop client on the prep-room computer is configured to keep the deployed SDS folder "Available Offline" to maintain OSHA 1910.1200 compliance during network outages.  
*Developed for Cumberland University Sciences.*
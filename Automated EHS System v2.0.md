# **🏛️ MASTER IMPLEMENTATION PLAN: Automated EHS System v2.0**

**Institution:** Cumberland University (Sciences: Chemistry, Biology, Physics)  
**Objective:** Deploy a frictionless, AI-verified, OSHA/EPA/TDEC-compliant EHS pipeline.  
**Technology Stack:** Google Workspace (Forms, Sheets, Drive, Gmail), GitHub (Codespaces, Actions), Gemini 1.5 Pro API, Python 3.10+.  
**Total Net Software Cost:** $0.00 (Utilizing existing educational infrastructure and free-tier compute).

## **PHASE 1: Infrastructure & Environment Setup (IT & DevOps)**

*The foundational architecture required before any backend code is written.*  
**1.1 Google Cloud & Workspace Configuration**

* **Service Account Creation:** IT must create a dedicated Google Workspace account (e.g., ehs-automation@cumberland.edu) to act as the master owner of all Forms, Sheets, and Drive folders. This prevents the system from breaking if a specific faculty member retires or leaves.  
* **API Enablement:** In the Google Cloud Console, enable the **Google Sheets API**, **Google Drive API**, and **Gmail API**. Generate a Service Account JSON credential key.  
* **Shared Drive Architecture:** Set up a Shared Drive (CU Sciences EHS) with the following directory tree:  
  * /Databases (Contains the Master Inventory and Waste Log Google Sheets)  
  * /SDS\_Archive/Pending (For newly fetched, unprinted SDS PDFs)  
  * /SDS\_Archive/Deployed (For confirmed, physically deployed SDS PDFs)

**1.2 GitHub Repository & AI Environment**

* **API Key:** Generate a **Gemini 1.5 Pro API Key** via Google AI Studio.  
* **Repo Setup:** Create a private repository in the Cumberland University GitHub Org (e.g., CU-EHS-Core).  
* **Codespace Configuration:** Configure a .devcontainer to install the required Python libraries: google-api-python-client, google-generativeai, reportlab (for PDF generation), PyPDF2 (for SDS truncation), Pillow (for EXIF extraction), and qrcode.  
* **Secrets Management:** Load the Gemini API Key and the Google Service Account JSON into **GitHub Repository Secrets** (GEMINI\_API\_KEY, GCP\_CREDENTIALS).

**1.3 The Deterministic Safety Database (Anti-Hallucination)**

* Upload a static CSV file to the GitHub repository root (flinn\_logic\_matrix.csv). This file must map chemical hazard classes to their corresponding physical shelf locations at Cumberland (e.g., Organic Flammable \-\> Flinn Organic \#2). This ensures Gemini is used for text extraction, but hard-coded logic dictates storage.

## **PHASE 2: Pillar-by-Pillar Engineering (Software Devs)**

*Development occurs in GitHub Codespaces. Deployment is managed via GitHub Actions triggered by webhooks (Google Apps Script on Form submit) or cron schedules.*

### **Pillar 1: Automated Intake ("Snap & Store")**

* **Frontend:** Create "CU Chemical Intake Form." Fields: Submitter Name, Room, and **File Upload** (Image of label).  
* **Python Logic (intake\_processor.py):**  
  1. Downloads the uploaded image from Google Drive.  
  2. Passes the image to the **Gemini 1.5 Pro Vision API** with a strict prompt: *"Extract the Chemical Name, CAS Number, Vendor, and Volume from this label. Output strictly as JSON."*  
  3. Cross-references the JSON output against flinn\_logic\_matrix.csv to determine the physical storage shelf.  
  4. Appends the parsed data to the Master Inventory Google Sheet.  
  5. Uses a web scraper or pubchempy to download the SDS PDF and saves it to the /SDS\_Archive/Pending folder.  
  6. Uses the Gmail API to email the submitter: *"Chemical logged. Place on physical shelf: \[Flinn Code\]."*

### **Pillar 2: Frictionless Waste Management ("Smart Tag")**

* **Frontend:** Create "CU Waste Addition Form." Fields: Submitter Name, Hood Number, and a **Paragraph Text Box** for smartphone dictation.  
* **Python Logic (waste\_processor.py):**  
  1. Passes the dictated text to Gemini. **Prompt:** *"Extract a list of chemicals and volumes. Apply EPA RCRA mixture rules. Output a JSON object containing the constituents and the applicable EPA Waste Codes (D, F, P, U)."*  
  2. Uses Python's reportlab library to generate a perfectly formatted 4x6 inch PDF Waste Tag containing the parsed data, date, and generator info.  
  3. Updates the Master Waste Log Google Sheet.  
  4. Emails the PDF directly to the prep-room network printer's unique email address (e.g., mh303-printer@hpeprint.com) for immediate physical output.

### **Pillar 3: SDS Compliance ("Closed-Loop Batch")**

* **The Batch Job:** Set a GitHub Actions cron job to run every Friday at 8:00 AM (0 8 \* \* 5).  
* **Python Logic (sds\_batch.py):**  
  1. Iterates through all PDFs in the /Pending folder.  
  2. Uses PyPDF2 to read each PDF, extracting *only* the English OSHA 16-section pages (discarding international translations to save toner).  
  3. Merges all truncated SDSs into a single PDF packet.  
  4. Uses reportlab and qrcode to generate a **Routing Cover Sheet** (e.g., *"Pgs 2-8 to MH303 Binder"*). The QR code is a pre-filled webhook URL.  
  5. Emails the collated packet to the prep-room printer.  
* **The Human Loop:** The student worker binds the pages and scans the QR code on the cover sheet. This webhook triggers a function to move the digital PDFs from "Pending" to "Deployed", securely closing the liability loop.

### **Pillar 4: Automated Auditing ("Proof-of-Presence")**

* **Frontend:** Modify the existing Cumberland Lab Audit Form to make "File Upload" mandatory for critical checks: 1\) Flowing Eyewash, 2\) Open Carboy, 3\) Powered-off Oven.  
* **The Trigger:** A cron job emails the form link to faculty in Week 1 and Week 15\.  
* **Python Logic (audit\_validator.py):**  
  1. *EXIF Check:* Uses Pillow to extract DateTimeOriginal from the uploaded JPEGs. If the photo is older than 48 hours, it fails.  
  2. *Visual Verification:* Sends the image to Gemini Vision API. **Prompt:** *"Does this image clearly show an eyewash station with water actively flowing out of the nozzles? Answer TRUE or FALSE."*  
  3. *Output:* If FALSE or EXIF fails, email the faculty member: *"Audit Rejected: Photo validation failed or is outdated. Please submit a live photo."* If TRUE, write a "VERIFIED" timestamp to the Admin Audit Sheet.

## **PHASE 3: Physical Operations & Hardware Deployment (Lab Manager)**

*Automation fails if the physical environment does not guide the user.*  
**3.1 Physical Command Centers**

* **Intake Station:** Set up a dedicated "Intake Mat" in the prep room. Permanently mount a laminated, high-contrast QR code linked to the Intake Form. Ensure the lighting is excellent for smartphone cameras.  
* **Waste Stations:** Print and laminate QR codes labeled "LOG WASTE HERE." Zip-tie these directly to the sashes of the designated waste hoods.  
* **Printer Gateway:** Ensure the prep-room printer has its "Email-to-Print" functionality activated. Stock hole-punches, zip-ties, and blank waste tags/tape directly next to the printer tray.

**3.2 Offline OSHA Compliance**

* Configure the prep room desktop and designated Lab Tablets to run the Google Drive Desktop app.  
* Navigate to the /SDS\_Archive/Deployed folder, right-click, and select **"Make available offline."** This legally satisfies the OSHA requirement that hazard communication must remain accessible during power or network outages.

## **PHASE 4: Quality Assurance & Adversarial Testing (Red Teaming)**

*Before university-wide rollout, the implementation team must attempt to break the system:*

> 1. **The "Sloppy Photo" Test (Pillar 1):** Deliberately take blurry photos of chemical labels, or photos with thumbs covering the CAS number. Verify Gemini gracefully triggers a "Human Review Required" fallback email to the Lab Manager instead of logging garbage data.  
> 2. **The "Cocktail" Test (Pillar 2):** Dictate highly complex, conflicting waste mixtures into the waste form (e.g., dictating the mixing of Nitric Acid with an organic solvent). Ensure the script flags this as an explosive incompatibility and alerts the Lab Manager immediately, rather than blindly printing a label.  
> 3. **The "Fake Audit" Test (Pillar 4):** Attempt to upload a screenshot of a photo, a downloaded image of an eyewash from Google Images, or a photo stripped of EXIF data. Verify the Python script automatically rejects the submission.

## **PHASE 5: Faculty Onboarding & Rollout (Department Leadership)**

**5.1 Faculty Training (The 5-Minute Pitch)**

* *Crucial Directive: Do not explain the AI, JSON, or GitHub backend to the faculty.*  
* Host a brief department meeting focused entirely on UX (User Experience).  
* **The Pitch:** *"We are eliminating EHS paperwork and friction. When a box arrives, scan the QR code and take a picture. When you dump waste, scan the hood QR code and speak into your phone. The system handles the SDS, calculates the EPA codes, and prints the physical labels for you."*

**5.2 Student Worker SOPs**

* Provide a simple, 1-page physical SOP in the prep room detailing how to execute the "Friday SDS Run" (Retrieve from printer $\\rightarrow$ Hole punch $\\rightarrow$ Place in respective room's Yellow Binder $\\rightarrow$ Scan the Cover Sheet QR Code). Ensure they understand that scanning the code is what finalizes the legal compliance check.
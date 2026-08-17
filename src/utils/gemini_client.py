import os
import json
import logging
from typing import Any
import google.generativeai as genai
from pydantic import BaseModel, ValidationError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LabelInfo(BaseModel):
    chemical_name: str
    cas_number: str
    vendor: str
    volume: str
    hazard_class: str

class Constituent(BaseModel):
    name: str
    volume: str

class WasteDictation(BaseModel):
    constituents: list[Constituent]
    epa_waste_codes: list[str]

def configure_gemini() -> None:
    """Configure the Gemini API client using the environment variable."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logger.error("[MISSING DATA] GEMINI_API_KEY environment variable is not set.")
        raise ValueError("GEMINI_API_KEY environment variable missing.")
    
    genai.configure(api_key=api_key)

def extract_label_info(image_path: str) -> LabelInfo:
    """Use Gemini Vision to extract chemical information from a label image."""
    configure_gemini()
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
    
    prompt = "Extract the Chemical Name, CAS Number, Vendor, and Volume from this label. Also determine the most appropriate hazard class (e.g., Organic Flammable, Organic Acid, Organic Misc, Inorganic Acid, Inorganic Base, Inorganic Misc, Oxidizer, Toxic). Output strictly as JSON with keys: chemical_name, cas_number, vendor, volume, hazard_class."
    
    try:
        image_file = genai.upload_file(image_path)
        response = model.generate_content([prompt, image_file])
        
        # Strip potential markdown formatting from the response
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
            
        data = json.loads(text.strip())
        return LabelInfo(**data)
    except (Exception, ValidationError) as e:
        logger.error(f"Failed to extract label info: {e}")
        raise

def parse_waste_dictation(dictation_text: str) -> WasteDictation:
    """Use Gemini NLP to parse waste dictation and apply EPA RCRA rules."""
    configure_gemini()
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
    
    prompt = f"Extract a list of chemicals and volumes from the following dictation: '{dictation_text}'. Apply EPA RCRA mixture rules. Output a JSON object containing a list of 'constituents' (each with 'name' and 'volume') and a list of applicable 'epa_waste_codes' (D, F, P, U)."
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
            
        data = json.loads(text.strip())
        return WasteDictation(**data)
    except (Exception, ValidationError) as e:
        logger.error(f"Failed to parse waste dictation: {e}")
        raise

def verify_audit_photo(image_path: str, prompt: str) -> bool:
    """Use Gemini Vision to verify if a photo matches the audit criteria."""
    configure_gemini()
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
    
    try:
        image_file = genai.upload_file(image_path)
        # We ask Gemini to output TRUE or FALSE
        response = model.generate_content([f"{prompt}. Answer exactly TRUE or FALSE.", image_file])
        return "TRUE" in response.text.upper()
    except Exception as e:
        logger.error(f"Failed to verify audit photo: {e}")
        raise

def check_compatibility_with_gemini(data: WasteDictation) -> bool:
    """Use Gemini to perform a Chemical Compatibility Pre-Check."""
    configure_gemini()
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
    
    constituents_str = ", ".join([f"{c.volume} of {c.name}" for c in data.constituents])
    prompt = (
        f"Perform a Chemical Compatibility Pre-Check for a waste mixture containing: {constituents_str}. "
        "Cross-reference this mixture against a known incompatibility matrix. "
        "Will this mixture result in an exothermic or gas-generating reaction, or is it an explosive incompatibility? "
        "Answer exactly TRUE if it is explosive/incompatible/exothermic/gas-generating, and FALSE if it is safe."
    )
    
    try:
        response = model.generate_content(prompt)
        return "TRUE" in response.text.upper()
    except Exception as e:
        logger.error(f"Failed to check compatibility: {e}")
        return True  # Fail safe

class HazardShelfPrediction(BaseModel):
    hazard_class: str
    flinn_shelf: str

def deduce_hazard_and_shelf(image_path: str) -> HazardShelfPrediction:
    """Use Gemini Vision for a zero-shot safety analysis to deduce the primary hazard class and dynamically assign the Flinn shelf."""
    configure_gemini()
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
    
    prompt = (
        "Perform a zero-shot safety analysis on the chemical structure or information shown in this image "
        "to deduce the primary hazard class and dynamically assign the appropriate Flinn shelf. "
        "Output strictly as JSON with keys: hazard_class, flinn_shelf."
    )
    
    try:
        image_file = genai.upload_file(image_path)
        response = model.generate_content([prompt, image_file])
        
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
            
        data = json.loads(text.strip())
        return HazardShelfPrediction(**data)
    except (Exception, ValidationError) as e:
        logger.error(f"Failed to deduce hazard and shelf: {e}")
        raise

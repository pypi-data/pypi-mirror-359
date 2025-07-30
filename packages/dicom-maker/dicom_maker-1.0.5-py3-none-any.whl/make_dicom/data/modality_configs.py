#!/usr/bin/env python3
"""
Modality configuration data for DICOM Generator
"""

# Modality configurations
MODALITY_CONFIGS = {
    "CT": {
        "body_parts": ["HEAD", "NECK", "CHEST", "ABDOMEN", "PELVIS", "SPINE", "EXTREMITY"],
        "slice_thickness": [1.0, 2.0, 2.5, 3.0, 5.0],
        "pixel_spacing": [0.5, 0.7, 1.0],
        "series_types": ["AXIAL", "CORONAL", "SAGITTAL"],
        "acquisition_protocols": ["STANDARD", "HIGH RESOLUTION", "LOW DOSE"]
    },
    "MR": {
        "body_parts": ["BRAIN", "CSPINE", "TSPINE", "LSPINE", "KNEE", "SHOULDER", "ABDOMEN"],
        "slice_thickness": [2.0, 3.0, 4.0, 5.0],
        "pixel_spacing": [0.7, 0.9, 1.2],
        "series_types": ["T1", "T2", "FLAIR", "DWI", "SWI"],
        "acquisition_protocols": ["GRADIENT ECHO", "SPIN ECHO", "INVERSION RECOVERY"]
    },
    "US": {
        "body_parts": ["ABDOMEN", "PELVIS", "BREAST", "THYROID", "TESTIS", "CAROTID"],
        "slice_thickness": [0.5, 1.0],
        "pixel_spacing": [0.2, 0.3],
        "series_types": ["B-MODE", "COLOR", "DOPPLER"],
        "acquisition_protocols": ["STANDARD", "HARMONIC", "COMPOUND"]
    },
    "CR": {
        "body_parts": ["CHEST", "HAND", "FOOT", "KNEE", "ELBOW", "SHOULDER"],
        "pixel_spacing": [0.1, 0.15, 0.2],
        "series_types": ["PA", "LATERAL", "OBLIQUE", "AP"],
        "acquisition_protocols": ["STANDARD", "WEIGHT BEARING", "STRESS VIEW"]
    }
}

# Protocols and studies
STUDY_DESCRIPTIONS = {
    "CT": {
        "HEAD": ["Head CT without contrast", "Head CT with contrast", "CT Angiogram Head"],
        "NECK": ["Neck CT without contrast", "Neck CT with contrast", "CT Soft Tissue Neck"],
        "CHEST": ["Chest CT without contrast", "CT Pulmonary Angiogram", "High Resolution Chest CT"],
        "ABDOMEN": ["Abdomen CT without contrast", "Abdomen CT with contrast", "CT Enterography"],
        "PELVIS": ["Pelvis CT without contrast", "Pelvis CT with contrast", "CT Urogram"],
        "SPINE": ["Cervical Spine CT", "Thoracic Spine CT", "Lumbar Spine CT"],
        "EXTREMITY": ["CT Lower Extremity", "CT Upper Extremity", "CT Joint Study"]
    },
    "MR": {
        "BRAIN": ["Brain MRI without contrast", "Brain MRI with contrast", "MR Angiogram Brain"],
        "CSPINE": ["Cervical Spine MRI", "Cervical Spine MRI with contrast", "MR Myelogram"],
        "TSPINE": ["Thoracic Spine MRI", "Thoracic Spine MRI with contrast", "MR Myelogram"],
        "LSPINE": ["Lumbar Spine MRI", "Lumbar Spine MRI with contrast", "MR Myelogram"],
        "KNEE": ["Knee MRI", "Knee MRI Arthrogram", "MR Cartilage Study"],
        "SHOULDER": ["Shoulder MRI", "Shoulder MR Arthrogram", "MR Rotator Cuff"],
        "ABDOMEN": ["Abdomen MRI without contrast", "Abdomen MRI with contrast", "MRCP"]
    },
    "US": {
        "ABDOMEN": ["Complete Abdomen US", "Limited Abdomen US", "RUQ US"],
        "PELVIS": ["Pelvic US", "Transvaginal US", "Transabdominal US"],
        "BREAST": ["Bilateral Breast US", "Right Breast US", "Left Breast US"],
        "THYROID": ["Thyroid US", "Parathyroid US", "Neck US"],
        "TESTIS": ["Scrotal US", "Testicular US", "Doppler Testis"],
        "CAROTID": ["Carotid Duplex", "Carotid Doppler", "Neck Vessel US"]
    },
    "CR": {
        "CHEST": ["Chest X-ray PA and Lateral", "Portable Chest X-ray", "Chest X-ray PA"],
        "HAND": ["Hand X-ray", "Wrist X-ray", "Hand and Wrist X-ray"],
        "FOOT": ["Foot X-ray", "Ankle X-ray", "Foot and Ankle X-ray"],
        "KNEE": ["Knee X-ray", "Weight-bearing Knee X-ray", "Knee X-ray Multiple Views"],
        "ELBOW": ["Elbow X-ray", "Elbow X-ray Multiple Views", "Elbow X-ray with Stress View"],
        "SHOULDER": ["Shoulder X-ray", "Shoulder X-ray Multiple Views", "Scapular Y View"]
    }
}
#!/usr/bin/env python3
"""
Study information generation for DICOM Generator
"""

import random
import datetime
from data.modality_configs import STUDY_DESCRIPTIONS
from utils.uid_generator import generate_uid


def generate_accession_number():
    """
    Generate a random accession number

    Returns:
        str: Unique accession number
    """
    return f"ACC{random.randint(1000000, 9999999)}"


def generate_study_description(modality, body_part):
    """
    Generate a study description based on modality and body part

    Args:
        modality (str): The imaging modality (CT, MR, etc.)
        body_part (str): The body part being examined

    Returns:
        str: Description of the study
    """
    if modality in STUDY_DESCRIPTIONS and body_part in STUDY_DESCRIPTIONS[modality]:
        return random.choice(STUDY_DESCRIPTIONS[modality][body_part])
    return f"{modality} {body_part}"


def generate_study_date(max_days_ago=730):
    """
    Generate a study date within the specified time range

    Args:
        max_days_ago (int): Maximum number of days in the past

    Returns:
        str: Formatted date string (YYYYMMDD)
    """
    study_days_ago = random.randint(0, max_days_ago)  # Up to max_days_ago days ago
    study_date_obj = datetime.datetime.now() - datetime.timedelta(days=study_days_ago)
    return study_date_obj.strftime('%Y%m%d')


def generate_study_info(modality, body_part):
    """
    Generate a complete set of random study information

    Args:
        modality (str): The imaging modality (CT, MR, etc.)
        body_part (str): The body part being examined

    Returns:
        dict: Dictionary containing study information
    """
    # Generate core study identifiers
    study_instance_uid = generate_uid()
    study_id = f"S{random.randint(1000, 9999)}"
    accession_number = generate_accession_number()
    study_date = generate_study_date()
    study_time = datetime.datetime.now().strftime('%H%M%S')

    # Generate study description based on modality and body part
    study_description = generate_study_description(modality, body_part)

    # Study status and additional study information
    study_statuses = ["SCHEDULED", "IN PROGRESS", "COMPLETED", "VERIFIED"]
    study_priorities = ["HIGH", "ROUTINE", "MEDIUM", "STAT"]
    reasons_for_study = ["Annual checkup", "Follow-up", "Diagnostic", "Screening",
                         "Trauma", "Pre-surgical", "Post-surgical", "Oncology workup"]

    # Additional clinical info
    contrast_agents = ["NONE", "ORAL", "IV", "BOTH"]
    patient_positions = ["HFS", "HFP", "FFS", "FFP", "SITTING", "STANDING"]

    # Generate scheduled procedure step ID
    scheduled_procedure_step_id = f"SPS{random.randint(10000, 99999)}"

    return {
        "StudyInstanceUID": study_instance_uid,
        "StudyID": study_id,
        "AccessionNumber": accession_number,
        "StudyDate": study_date,
        "StudyTime": study_time,
        "StudyDescription": study_description,
        "StudyStatusID": random.choice(study_statuses),
        "StudyPriorityID": random.choice(study_priorities),
        "ReasonForStudy": random.choice(reasons_for_study),
        "RequestedProcedureDescription": study_description,
        "RequestedContrastAgent": random.choice(contrast_agents),
        "ScheduledProcedureStepID": scheduled_procedure_step_id,
        "PerformedProcedureStepDescription": study_description,
        "PatientPosition": random.choice(patient_positions),
    }


def generate_series_info(study_instance_uid, modality, body_part, series_number, series_type=None):
    """
    Generate a complete set of random series information

    Args:
        study_instance_uid (str): The parent study UID
        modality (str): The imaging modality (CT, MR, etc.)
        body_part (str): The body part being examined
        series_number (int): The series number
        series_type (str, optional): Type of series (AXIAL, T1, etc.)

    Returns:
        dict: Dictionary containing series information
    """
    from data.modality_configs import MODALITY_CONFIGS

    # Generate series UID
    series_instance_uid = generate_uid()

    # If series type not provided, select one based on modality
    if series_type is None and modality in MODALITY_CONFIGS:
        if "series_types" in MODALITY_CONFIGS[modality]:
            series_type = random.choice(MODALITY_CONFIGS[modality]["series_types"])
        else:
            series_type = "STANDARD"

    # Generate description
    series_description = f"{series_type} {body_part}"

    # Get acquisition protocol based on modality
    acquisition_protocol = None
    if modality in MODALITY_CONFIGS:
        if "acquisition_protocols" in MODALITY_CONFIGS[modality]:
            acquisition_protocol = random.choice(MODALITY_CONFIGS[modality]["acquisition_protocols"])
        else:
            acquisition_protocol = "STANDARD"

    # Additional series specific information
    acquisition_types = ["SPIRAL", "SEQUENTIAL", "2D", "3D"]
    # Updated acquisition_contrasts to use floating point values instead of strings
    acquisition_contrasts = [0.0, 1.0, 0.5]  # UNENHANCED (0.0), CONTRAST (1.0), MIXED (0.5)

    return {
        "SeriesInstanceUID": series_instance_uid,
        "SeriesNumber": str(series_number),
        "SeriesDescription": series_description,
        "AcquisitionNumber": str(series_number),
        "SeriesDate": datetime.datetime.now().strftime('%Y%m%d'),
        "SeriesTime": datetime.datetime.now().strftime('%H%M%S'),
        "ProtocolName": acquisition_protocol,
        "AcquisitionType": random.choice(acquisition_types),
        "AcquisitionContrast": random.choice(acquisition_contrasts),
        "ORIGINAL\\PRIMARY\\AXIAL": f"ORIGINAL\\PRIMARY\\{series_type}" if series_type else "ORIGINAL\\PRIMARY\\AXIAL",
    }
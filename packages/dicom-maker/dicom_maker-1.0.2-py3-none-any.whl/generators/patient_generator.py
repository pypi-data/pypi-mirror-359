#!/usr/bin/env python3
"""
Patient information generation for DICOM Generator
"""

import random
import datetime
from config import (
    PATIENT_FIRST_NAMES,
    PATIENT_LAST_NAMES,
    INSTITUTION_ADDRESSES,
    BILATERAL_BODY_PARTS,
    LATERALITY
)


def generate_patient_name():
    """
    Generate a random patient name

    Returns:
        str: Name in the format 'LastName^FirstName'
    """
    first = random.choice(PATIENT_FIRST_NAMES)
    last = random.choice(PATIENT_LAST_NAMES)
    return f"{last}^{first}"


def generate_patient_id():
    """
    Generate a random patient ID

    Returns:
        str: Unique patient ID
    """
    return f"PID{random.randint(100000, 999999)}"


def generate_patient_demographics():
    """
    Generate a complete set of random patient demographics

    Returns:
        dict: Dictionary containing patient demographic information
    """
    # Generate basic identifiers
    patient_name = generate_patient_name()
    patient_id = generate_patient_id()
    patient_sex = random.choice(['M', 'F'])

    # Generate random birth date (18-90 years old)
    current_year = datetime.datetime.now().year
    birth_year = current_year - random.randint(18, 90)
    birth_month = random.randint(1, 12)
    birth_day = random.randint(1, 28)  # Simplified to avoid month length issues
    patient_birth_date = f"{birth_year}{birth_month:02d}{birth_day:02d}"

    # Age derived from birth date
    patient_age = f"{current_year - birth_year}Y"

    # Random patient physical stats
    if patient_sex == 'M':
        patient_height = random.uniform(160, 190)  # cm
        patient_weight = random.uniform(60, 100)  # kg
    else:
        patient_height = random.uniform(150, 180)  # cm
        patient_weight = random.uniform(45, 85)  # kg

    patient_address = random.choice(INSTITUTION_ADDRESSES)  # Reusing address list for patients
    patient_size = patient_height / 100  # Convert to meters for DICOM

    # Random ethnic group
    ethnic_groups = ["Caucasian", "African American", "Hispanic", "Asian", "Native American", "Other"]
    ethnic_group = random.choice(ethnic_groups)

    # Random occupation
    occupations = ["Engineer", "Teacher", "Doctor", "Lawyer", "Student", "Retired", "Nurse", "Technician",
                   "Manager", "Sales", "Construction", "Artist", "Writer", "Driver", "Unemployed"]
    occupation = random.choice(occupations)

    # Generate random patient history
    history_templates = [
        "Patient with no relevant history.",
        "Patient with minor relevant history.",
        "Patient with significant relevant history."
    ]

    return {
        "PatientName": patient_name,
        "PatientID": patient_id,
        "PatientSex": patient_sex,
        "PatientBirthDate": patient_birth_date,
        "PatientAge": patient_age,
        "PatientSize": str(patient_size),
        "PatientWeight": str(round(patient_weight, 1)),
        "PatientAddress": patient_address,
        "EthnicGroup": ethnic_group,
        "Occupation": occupation,
        "PatientOtherIDs": f"MRN{random.randint(100000, 999999)}",
        "AdditionalPatientHistory": random.choice(history_templates),
        "PatientComments": ""
    }


def get_laterality(body_part):
    """
    Determine if a body part should have laterality and return it if applicable

    Args:
        body_part (str): The body part being examined

    Returns:
        str or None: 'L', 'R', or None if laterality doesn't apply
    """
    if body_part in BILATERAL_BODY_PARTS:
        return random.choice(LATERALITY)
    return None
#!/usr/bin/env python3
"""
Institution and provider information generation for DICOM Generator
"""

import random
from config import (
    INSTITUTION_NAMES,
    INSTITUTION_ADDRESSES,
    PHYSICIAN_FIRST_NAMES,
    PHYSICIAN_LAST_NAMES,
    PHYSICIAN_SPECIALTIES
)


def generate_institution_name():
    """
    Generate a random institution name

    Returns:
        str: Institution name
    """
    return random.choice(INSTITUTION_NAMES)


def generate_institution_address():
    """
    Generate a random institution address

    Returns:
        str: Institution address
    """
    return random.choice(INSTITUTION_ADDRESSES)


def generate_physician_name():
    """
    Generate a random physician name

    Returns:
        str: Name in the format 'LastName^FirstName^Specialty^MD'
    """
    first = random.choice(PHYSICIAN_FIRST_NAMES)
    last = random.choice(PHYSICIAN_LAST_NAMES)
    specialty = random.choice(PHYSICIAN_SPECIALTIES)
    return f"{last}^{first}^{specialty}^MD"


def generate_institution_info():
    """
    Generate a complete set of random institution information

    Returns:
        dict: Dictionary containing institution information
    """
    institution_name = generate_institution_name()
    institution_address = generate_institution_address()
    department_name = "RADIOLOGY"

    # Station name (usually modality + number)
    # This will be updated later based on modality
    station_name = "STATION1"

    return {
        "InstitutionName": institution_name,
        "InstitutionAddress": institution_address,
        "InstitutionalDepartmentName": department_name,
        "StationName": station_name
    }


def generate_physician_info():
    """
    Generate a complete set of random physician information

    Returns:
        dict: Dictionary containing physician information
    """
    referring_physician = generate_physician_name()

    return {
        "ReferringPhysicianName": referring_physician,
        "RequestingPhysician": referring_physician,
        "PhysicianOfRecord": referring_physician,
        "PerformingPhysicianName": generate_physician_name(),  # Different physician
        "OperatorName": generate_physician_name().split('^')[0] + "^Tech",  # Technologist
    }
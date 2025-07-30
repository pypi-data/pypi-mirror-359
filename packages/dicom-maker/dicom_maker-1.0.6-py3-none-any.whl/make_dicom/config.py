#!/usr/bin/env python3
"""
Configuration constants for DICOM Generator
"""

# DICOM UID root (using a generic root for examples)
UID_ROOT = "1.2.826.0.1.3680043.9.7133"

# Patient names and IDs
PATIENT_FIRST_NAMES = ["John", "Jane", "Robert", "Mary", "William", "Sarah", "David", "Lisa",
                       "Michael", "Patricia", "James", "Jennifer", "Thomas", "Elizabeth", "Charles", "Linda"]
PATIENT_LAST_NAMES = ["Smith", "Jones", "Brown", "Johnson", "Williams", "Davis", "Miller", "Wilson",
                      "Anderson", "Taylor", "Thomas", "Jackson", "White", "Harris", "Martin", "Thompson"]

# Institution information
INSTITUTION_NAMES = ["Metro General Hospital", "City Medical Center", "University Hospital",
                     "Regional Medical Center", "Memorial Hospital", "General Hospital",
                     "County Hospital", "Community Medical Center", "Medical Associates",
                     "Radiology Partners"]

INSTITUTION_ADDRESSES = [
    "123 Main Street, New York, NY 10001",
    "456 Oak Avenue, Los Angeles, CA 90001",
    "789 Pine Road, Chicago, IL 60601",
    "321 Maple Drive, Houston, TX 77001",
    "654 Elm Boulevard, Philadelphia, PA 19101",
    "987 Cedar Lane, Phoenix, AZ 85001",
    "741 Birch Street, San Antonio, TX 78201",
    "852 Willow Avenue, San Diego, CA 92101",
    "963 Spruce Court, Dallas, TX 75201",
    "159 Redwood Plaza, San Jose, CA 95101"
]

# Physician information
PHYSICIAN_FIRST_NAMES = ["Alan", "Barbara", "Carl", "Donna", "Edward", "Frances", "George", "Helen",
                         "Ivan", "Julia", "Kevin", "Laura", "Mark", "Nancy", "Oscar", "Paula"]
PHYSICIAN_LAST_NAMES = ["Adams", "Baker", "Chen", "Diaz", "Edwards", "Fisher", "Garcia", "Hoffman",
                        "Ivanov", "Johnson", "Khan", "Lee", "Mitchell", "Nelson", "Ortiz", "Patel"]

PHYSICIAN_SPECIALTIES = ["Radiology", "Cardiology", "Neurology", "Orthopedics", "Internal Medicine",
                         "Family Medicine", "Emergency Medicine", "Oncology", "Gastroenterology", "Pediatrics"]

# Laterality mapping
BILATERAL_BODY_PARTS = ["KNEE", "SHOULDER", "HAND", "FOOT", "ELBOW", "BREAST", "EXTREMITY"]
LATERALITY = ["L", "R"]  # Left, Right
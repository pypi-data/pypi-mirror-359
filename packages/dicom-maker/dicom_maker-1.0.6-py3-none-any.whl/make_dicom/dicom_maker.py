#!/usr/bin/env python3
"""
Enhanced DICOM Generator

This script generates sample DICOM studies with consistent patient demographics and
comprehensive clinical metadata including institution information, referring physicians,
laterality, and other commonly used DICOM fields.

Requirements:
- Python 3.6+
- DCMTK toolkit installed and available in PATH

Usage:
python enhanced_dicom_generator.py --output-dir ./dicom-data --modality CT --body-part CHEST --num-studies 1 --num-series 3 --num-instances 5
"""

import argparse
import os
import subprocess
import uuid
import random
import datetime
import tempfile
from pathlib import Path

# DICOM UID root (using a generic root for examples)
UID_ROOT = "1.2.826.0.1.3680043.9.7133"

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

# Laterality mapping
BILATERAL_BODY_PARTS = ["KNEE", "SHOULDER", "HAND", "FOOT", "ELBOW", "BREAST", "EXTREMITY"]
LATERALITY = ["L", "R"]  # Left, Right


def generate_uid(prefix=UID_ROOT):
    """Generate a unique DICOM UID"""
    unique_part = str(uuid.uuid4().int)[:16]
    return f"{prefix}.{unique_part}"


def generate_patient_name():
    """Generate a random patient name"""
    first = random.choice(PATIENT_FIRST_NAMES)
    last = random.choice(PATIENT_LAST_NAMES)
    return f"{last}^{first}"


def generate_patient_id():
    """Generate a random patient ID"""
    return f"PID{random.randint(100000, 999999)}"


def generate_accession_number():
    """Generate a random accession number"""
    return f"ACC{random.randint(1000000, 9999999)}"


def generate_institution_name():
    """Generate a random institution name"""
    return random.choice(INSTITUTION_NAMES)


def generate_institution_address():
    """Generate a random institution address"""
    return random.choice(INSTITUTION_ADDRESSES)


def generate_physician_name():
    """Generate a random physician name"""
    first = random.choice(PHYSICIAN_FIRST_NAMES)
    last = random.choice(PHYSICIAN_LAST_NAMES)
    specialty = random.choice(PHYSICIAN_SPECIALTIES)
    return f"{last}^{first}^{specialty}^MD"


def generate_study_description(modality, body_part):
    """Generate a study description based on modality and body part"""
    if modality in STUDY_DESCRIPTIONS and body_part in STUDY_DESCRIPTIONS[modality]:
        return random.choice(STUDY_DESCRIPTIONS[modality][body_part])
    return f"{modality} {body_part}"


def get_laterality(body_part):
    """Determine if a body part should have laterality and return it if applicable"""
    if body_part in BILATERAL_BODY_PARTS:
        return random.choice(LATERALITY)
    return None


def create_dicom_template():
    """Create a template DICOM file with extended fields"""
    template = """# Dicom-File-Format

# Dicom-Meta-Information-Header
# Used TransferSyntax: Little Endian Explicit
(0002,0000) UL 184                                      # 4, 1 FileMetaInformationGroupLength
(0002,0001) OB 00\\01                                    # 2, 1 FileMetaInformationVersion
(0002,0002) UI =CTImageStorage                          # 26, 1 MediaStorageSOPClassUID
(0002,0003) UI [SOPInstanceUID]                         # 0, 1 MediaStorageSOPInstanceUID
(0002,0010) UI =LittleEndianExplicit                    # 20, 1 TransferSyntaxUID
(0002,0012) UI 1.2.276.0.7230010.3.0.3.6.4              # 28, 1 ImplementationClassUID
(0002,0013) SH DCMTK                                    # 6, 1 ImplementationVersionName

# Dataset
(0008,0005) CS ISO_IR 100                               # 10, 1 SpecificCharacterSet
(0008,0008) CS [ORIGINAL\\PRIMARY\\AXIAL]                # 0, 3 ImageType
(0008,0012) DA [ContentDate]                            # 0, 1 InstanceCreationDate
(0008,0013) TM [ContentTime]                            # 0, 1 InstanceCreationTime
(0008,0016) UI =CTImageStorage                          # 26, 1 SOPClassUID
(0008,0018) UI [SOPInstanceUID]                         # 0, 1 SOPInstanceUID
(0008,0020) DA [StudyDate]                              # 0, 1 StudyDate
(0008,0021) DA [SeriesDate]                             # 0, 1 SeriesDate
(0008,0022) DA [AcquisitionDate]                        # 0, 1 AcquisitionDate
(0008,0023) DA [ContentDate]                            # 0, 1 ContentDate
(0008,0030) TM [StudyTime]                              # 0, 1 StudyTime
(0008,0031) TM [SeriesTime]                             # 0, 1 SeriesTime
(0008,0032) TM [AcquisitionTime]                        # 0, 1 AcquisitionTime
(0008,0033) TM [ContentTime]                            # 0, 1 ContentTime
(0008,0050) SH [AccessionNumber]                        # 0, 1 AccessionNumber
(0008,0060) CS [Modality]                               # 0, 1 Modality
(0008,0064) CS [ConversionType]                         # 0, 1 ConversionType
(0008,0070) LO DICOM Generator                          # 16, 1 Manufacturer
(0008,0080) LO [InstitutionName]                        # 0, 1 InstitutionName
(0008,0081) ST [InstitutionAddress]                     # 0, 1 InstitutionAddress
(0008,0090) PN [ReferringPhysicianName]                 # 0, 1 ReferringPhysicianName
(0008,1010) SH [StationName]                            # 0, 1 StationName
(0008,1030) LO [StudyDescription]                       # 0, 1 StudyDescription
(0008,103e) LO [SeriesDescription]                      # 0, 1 SeriesDescription
(0008,1040) LO [InstitutionalDepartmentName]            # 0, 1 InstitutionalDepartmentName
(0008,1048) PN [PhysicianOfRecord]                      # 0, 1 PhysicianOfRecord
(0008,1050) PN [PerformingPhysicianName]                # 0, 1 PerformingPhysicianName
(0008,1070) PN [OperatorName]                           # 0, 1 OperatorName
(0008,1090) LO [ManufacturerModelName]                  # 0, 1 ManufacturerModelName
(0008,9215) SQ (Sequence with explicit length #=1)      # 68, 1 DerivationCodeSequence
  (fffe,e000) na (Item with explicit length #=2)          # 60, 1 Item
    (0008,0100) SH 121320                                   # 6, 1 CodeValue
    (0008,0104) LO Source image for image processing operation # 40, 1 CodeMeaning
  (fffe,e00d) na (ItemDelimitationItem)                   #   0, 0 ItemDelimitationItem
(fffe,e0dd) na (SequenceDelimitationItem)               #   0, 0 SequenceDelimitationItem

(0010,0010) PN [PatientName]                            # 0, 1 PatientName
(0010,0020) LO [PatientID]                              # 0, 1 PatientID
(0010,0030) DA [PatientBirthDate]                       # 0, 1 PatientBirthDate
(0010,0040) CS [PatientSex]                             # 0, 1 PatientSex
(0010,1000) LO [PatientOtherIDs]                        # 0, 1 OtherPatientIDs
(0010,1010) AS [PatientAge]                             # 0, 1 PatientAge
(0010,1020) DS [PatientSize]                            # 0, 1 PatientSize
(0010,1030) DS [PatientWeight]                          # 0, 1 PatientWeight
(0010,1040) LO [PatientAddress]                         # 0, 1 PatientAddress
(0010,2160) SH [EthnicGroup]                            # 0, 1 EthnicGroup
(0010,2180) SH [Occupation]                             # 0, 1 Occupation
(0010,21B0) LT [AdditionalPatientHistory]               # 0, 1 AdditionalPatientHistory
(0010,4000) LT [PatientComments]                        # 0, 1 PatientComments

(0018,0015) CS [BodyPartExamined]                       # 0, 1 BodyPartExamined
(0018,0050) DS [SliceThickness]                         # 0, 1 SliceThickness
(0018,0060) DS [KVP]                                    # 0, 1 KVP
(0018,1000) LO [DeviceSerialNumber]                     # 0, 1 DeviceSerialNumber
(0018,1020) LO [SoftwareVersions]                       # 0, 1 SoftwareVersions
(0018,1030) LO [ProtocolName]                           # 0, 1 ProtocolName
(0018,1100) DS [ReconstructionDiameter]                 # 0, 1 ReconstructionDiameter
(0018,1110) DS [DistanceSourceToDetector]               # 0, 1 DistanceSourceToDetector
(0018,1111) DS [DistanceSourceToPatient]                # 0, 1 DistanceSourceToPatient
(0018,1120) DS [GantryDetectorTilt]                     # 0, 1 GantryDetectorTilt
(0018,1130) DS [TableHeight]                            # 0, 1 TableHeight
(0018,1140) CS [RotationDirection]                      # 0, 1 RotationDirection
(0018,1150) IS [ExposureTime]                           # 0, 1 ExposureTime
(0018,1151) IS [XRayTubeCurrent]                        # 0, 1 XRayTubeCurrent
(0018,1152) IS [Exposure]                               # 0, 1 Exposure
(0018,1160) SH [FilterType]                             # 0, 1 FilterType
(0018,1170) IS [GeneratorPower]                         # 0, 1 GeneratorPower
(0018,1190) DS [FocalSpot]                              # 0, 1 FocalSpot
(0018,1210) SH [ConvolutionKernel]                      # 0, 1 ConvolutionKernel
(0018,5100) CS [PatientPosition]                        # 0, 1 PatientPosition
(0018,9302) CS [AcquisitionType]                        # 0, 1 AcquisitionType
(0018,9309) CS [AcquisitionContrast]                    # 0, 1 AcquisitionContrast

(0020,000d) UI [StudyInstanceUID]                       # 0, 1 StudyInstanceUID
(0020,000e) UI [SeriesInstanceUID]                      # 0, 1 SeriesInstanceUID
(0020,0010) SH [StudyID]                                # 0, 1 StudyID
(0020,0011) IS [SeriesNumber]                           # 0, 1 SeriesNumber
(0020,0012) IS [AcquisitionNumber]                      # 0, 1 AcquisitionNumber
(0020,0013) IS [InstanceNumber]                         # 0, 1 InstanceNumber
(0020,0032) DS [ImagePositionPatient]                   # 0, 3 ImagePositionPatient
(0020,0037) DS [ImageOrientationPatient]                # 0, 6 ImageOrientationPatient
(0020,0052) UI [FrameOfReferenceUID]                    # 0, 1 FrameOfReferenceUID
(0020,0060) CS [Laterality]                             # 0, 1 Laterality
(0020,1040) LO [PositionReferenceIndicator]             # 0, 1 PositionReferenceIndicator
(0020,1041) DS [SliceLocation]                          # 0, 1 SliceLocation

(0028,0002) US 1                                        # 2, 1 SamplesPerPixel
(0028,0004) CS MONOCHROME2                              # 12, 1 PhotometricInterpretation
(0028,0010) US 16                                       # 2, 1 Rows
(0028,0011) US 16                                       # 2, 1 Columns
(0028,0030) DS [PixelSpacing]                           # 0, 2 PixelSpacing
(0028,0100) US 16                                       # 2, 1 BitsAllocated
(0028,0101) US 16                                       # 2, 1 BitsStored
(0028,0102) US 15                                       # 2, 1 HighBit
(0028,0103) US 1                                        # 2, 1 PixelRepresentation
(0028,1050) DS 0                                        # 2, 1 WindowCenter
(0028,1051) DS 0                                        # 2, 1 WindowWidth

(0032,000a) CS [StudyStatusID]                          # 0, 1 StudyStatusID
(0032,000c) CS [StudyPriorityID]                        # 0, 1 StudyPriorityID
(0032,1030) LO [ReasonForStudy]                         # 0, 1 ReasonForStudy
(0032,1032) PN [RequestingPhysician]                    # 0, 1 RequestingPhysician
(0032,1060) LO [RequestedProcedureDescription]          # 0, 1 RequestedProcedureDescription
(0032,1070) LO [RequestedContrastAgent]                 # 0, 1 RequestedContrastAgent

(0040,0009) SH [ScheduledProcedureStepID]               # 0, 1 ScheduledProcedureStepID
(0040,0254) LO [PerformedProcedureStepDescription]      # 0, 1 PerformedProcedureStepDescription
(0040,0275) SQ (Sequence with explicit length #=1)      # 74, 1 RequestAttributesSequence
  (fffe,e000) na (Item with explicit length #=2)          # 66, 1 Item
    (0040,0007) LO [RequestedProcedureDescription]        # 0, 1 RequestedProcedureDescription
    (0040,0009) SH [ScheduledProcedureStepID]             # 0, 1 ScheduledProcedureStepID
  (fffe,e00d) na (ItemDelimitationItem)                   #   0, 0 ItemDelimitationItem
(fffe,e0dd) na (SequenceDelimitationItem)               #   0, 0 SequenceDelimitationItem

(7fe0,0010) OW 0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000\\0000 # 256, 1 PixelData
"""
    return template


def create_dicom_from_template(template_content, output_path, study_uid, series_uid, instance_uid,
                               instance_number, series_number, patient_id, patient_name, study_date,
                               modality, body_part, series_type, accession_number, study_id,
                               patient_birth_date, patient_sex, institution_name=None, institution_address=None,
                               referring_physician=None, laterality=None, acquisition_protocol=None):
    """Create a DICOM file from a template, replacing placeholders with actual values"""

    # Generate additional metadata if not provided
    if institution_name is None:
        institution_name = generate_institution_name()
    if institution_address is None:
        institution_address = generate_institution_address()
    if referring_physician is None:
        referring_physician = generate_physician_name()

    # Set a study description based on modality and body part
    study_description = generate_study_description(modality, body_part)

    # Generate additional patient metadata
    # Age derived from birth date
    birth_year = int(patient_birth_date[:4])
    current_year = datetime.datetime.now().year
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

    # Station name and device information
    station_name = f"{modality}{random.randint(1, 5)}"
    device_serial = f"SN{random.randint(100000, 999999)}"
    software_version = f"{random.randint(1, 9)}.{random.randint(0, 9)}.{random.randint(0, 9)}"

    # Study status and additional study information
    study_statuses = ["SCHEDULED", "IN PROGRESS", "COMPLETED", "VERIFIED"]
    study_priorities = ["HIGH", "ROUTINE", "MEDIUM", "STAT"]
    reasons_for_study = ["Annual checkup", "Follow-up", "Diagnostic", "Screening",
                         "Trauma", "Pre-surgical", "Post-surgical", "Oncology workup"]

    # Additional clinical info
    contrast_agents = ["NONE", "ORAL", "IV", "BOTH"]
    patient_positions = ["HFS", "HFP", "FFS", "FFP", "SITTING", "STANDING"]
    acquisition_types = ["SPIRAL", "SEQUENTIAL", "2D", "3D"]
    acquisition_contrasts = ["UNENHANCED", "CONTRAST", "MIXED"]

    # If acquisition protocol not provided, select one based on modality
    if acquisition_protocol is None and modality in MODALITY_CONFIGS:
        if "acquisition_protocols" in MODALITY_CONFIGS[modality]:
            acquisition_protocol = random.choice(MODALITY_CONFIGS[modality]["acquisition_protocols"])
        else:
            acquisition_protocol = "STANDARD"

    # Generate scheduled procedure step ID
    scheduled_procedure_step_id = f"SPS{random.randint(10000, 99999)}"

    # Prepare all replacements
    replacements = {
        "[StudyInstanceUID]": study_uid,
        "[SeriesInstanceUID]": series_uid,
        "[SOPInstanceUID]": instance_uid,
        "[StudyDate]": study_date,
        "[SeriesDate]": study_date,
        "[AcquisitionDate]": study_date,
        "[ContentDate]": study_date,
        "[StudyTime]": datetime.datetime.now().strftime('%H%M%S'),
        "[SeriesTime]": datetime.datetime.now().strftime('%H%M%S'),
        "[AcquisitionTime]": datetime.datetime.now().strftime('%H%M%S'),
        "[ContentTime]": datetime.datetime.now().strftime('%H%M%S'),
        "[AccessionNumber]": accession_number,
        "[Modality]": modality,
        "[StudyDescription]": study_description,
        "[SeriesDescription]": f"{series_type} {body_part}",
        "[PatientName]": patient_name,
        "[PatientID]": patient_id,
        "[PatientBirthDate]": patient_birth_date,
        "[PatientSex]": patient_sex,
        "[BodyPartExamined]": body_part,
        "[SeriesNumber]": str(series_number),
        "[InstanceNumber]": str(instance_number),
        "[StudyID]": study_id,
        "[AcquisitionNumber]": str(series_number),
        "[InstitutionName]": institution_name,
        "[InstitutionAddress]": institution_address,
        "[ReferringPhysicianName]": referring_physician,
        "[RequestingPhysician]": referring_physician,
        "[PhysicianOfRecord]": referring_physician,
        "[PerformingPhysicianName]": generate_physician_name(),  # Different physician
        "[OperatorName]": generate_physician_name().split('^')[0] + "^Tech",  # Technologist
        "[PatientOtherIDs]": f"MRN{random.randint(100000, 999999)}",
        "[PatientAge]": patient_age,
        "[PatientSize]": str(patient_size),
        "[PatientWeight]": str(round(patient_weight, 1)),
        "[PatientAddress]": patient_address,
        "[EthnicGroup]": ethnic_group,
        "[Occupation]": occupation,
        "[AdditionalPatientHistory]": f"Patient with {random.choice(['no', 'minor', 'significant'])} relevant history.",
        "[PatientComments]": "",
        "[StationName]": station_name,
        "[DeviceSerialNumber]": device_serial,
        "[SoftwareVersions]": software_version,
        "[ProtocolName]": acquisition_protocol if acquisition_protocol else "STANDARD",
        "[ConversionType]": "SYN",  # Synthetic
        "[ManufacturerModelName]": f"{modality} Scanner {random.randint(1000, 9999)}",
        "[StudyStatusID]": random.choice(study_statuses),
        "[StudyPriorityID]": random.choice(study_priorities),
        "[ReasonForStudy]": random.choice(reasons_for_study),
        "[RequestedProcedureDescription]": study_description,
        "[RequestedContrastAgent]": random.choice(contrast_agents),
        "[ScheduledProcedureStepID]": scheduled_procedure_step_id,
        "[PerformedProcedureStepDescription]": study_description,
        "[PatientPosition]": random.choice(patient_positions),
        "[AcquisitionType]": random.choice(acquisition_types),
        "[AcquisitionContrast]": random.choice(acquisition_contrasts),
        "[InstitutionalDepartmentName]": "RADIOLOGY",
    }

    # Add laterality if applicable
    if laterality:
        replacements["[Laterality]"] = laterality
    else:
        # Remove the laterality tag if not applicable
        template_content = template_content.replace(
            "(0020,0060) CS [Laterality]                             # 0, 1 Laterality\n", "")

    # Add modality-specific replacements
    config = MODALITY_CONFIGS[modality]
    slice_thickness = random.choice(config["slice_thickness"]) if "slice_thickness" in config else 1.0
    pixel_spacing = random.choice(config["pixel_spacing"]) if "pixel_spacing" in config else 1.0

    replacements.update({
        "[SliceThickness]": str(slice_thickness),
        "[PixelSpacing]": f"{pixel_spacing}\\{pixel_spacing}",
    })

    # Generate position values based on instance number for proper 3D positioning
    slice_z_position = float(instance_number - 1) * slice_thickness

    # Modality specific tags
    if modality == "CT":
        replacements.update({
            "[KVP]": "120",
            "[XRayTubeCurrent]": "400",
            "[ConvolutionKernel]": "STANDARD",
            "[ORIGINAL\\PRIMARY\\AXIAL]": "ORIGINAL\\PRIMARY\\AXIAL",
            "=CTImageStorage": "1.2.840.10008.5.1.4.1.1.2",
            "[ImagePositionPatient]": f"0\\0\\{slice_z_position}",  # Position varies by instance for 3D
            "[ImageOrientationPatient]": "1\\0\\0\\0\\1\\0",
            "[SliceLocation]": str(slice_z_position),
            "[ReconstructionDiameter]": str(random.uniform(100, 500)),
            "[DistanceSourceToDetector]": str(random.uniform(800, 1200)),
            "[DistanceSourceToPatient]": str(random.uniform(400, 800)),
            "[GantryDetectorTilt]": "0",
            "[TableHeight]": str(random.uniform(150, 250)),
            "[RotationDirection]": "CW",
            "[ExposureTime]": str(random.randint(500, 2000)),
            "[Exposure]": str(random.randint(50, 500)),
            "[FilterType]": "BODY",
            "[GeneratorPower]": str(random.randint(20, 60)),
            "[FocalSpot]": "1.2",
            "[FrameOfReferenceUID]": generate_uid(),
            "[PositionReferenceIndicator]": "",
        })
    elif modality == "MR":
        replacements.update({
            "=CTImageStorage": "1.2.840.10008.5.1.4.1.1.4",
            "[ORIGINAL\\PRIMARY\\AXIAL]": "ORIGINAL\\PRIMARY\\" + series_type,
            "[ImagePositionPatient]": f"0\\0\\{slice_z_position}",
            "[ImageOrientationPatient]": "1\\0\\0\\0\\1\\0",
            "[SliceLocation]": str(slice_z_position),
            "[FrameOfReferenceUID]": generate_uid(),
            "[PositionReferenceIndicator]": "",
        })
    elif modality == "US":
        replacements.update({
            "=CTImageStorage": "1.2.840.10008.5.1.4.1.1.6.1",
            "[ORIGINAL\\PRIMARY\\AXIAL]": "ORIGINAL\\PRIMARY\\" + series_type,
        })
    elif modality == "CR":
        replacements.update({
            "=CTImageStorage": "1.2.840.10008.5.1.4.1.1.1",
            "[ORIGINAL\\PRIMARY\\AXIAL]": "ORIGINAL\\PRIMARY\\" + series_type,
            "[FrameOfReferenceUID]": generate_uid(),
        })

    # Apply all replacements
    for placeholder, value in replacements.items():
        template_content = template_content.replace(placeholder, value)

    # Create the temporary dump file
    temp_dump_file = tempfile.mktemp(suffix='.dump')
    with open(temp_dump_file, 'w') as f:
        f.write(template_content)

    # Convert dump to DICOM
    try:
        subprocess.run(['dump2dcm', temp_dump_file, output_path], check=True)
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"Error creating DICOM file: {e}")
        return None
    finally:
        # Clean up the temporary dump file
        os.unlink(temp_dump_file)


def main():
    """Main function to parse command line arguments and generate DICOM data"""

    parser = argparse.ArgumentParser(description='Generate sample DICOM studies with consistent metadata')

    parser.add_argument('--output-dir', type=str, required=True,
                        help='Output directory for DICOM files')

    parser.add_argument('--modality', type=str, required=True, choices=MODALITY_CONFIGS.keys(),
                        help='DICOM modality (CT, MR, US, CR)')

    parser.add_argument('--body-part', type=str, required=True,
                        help='Body part examined')

    parser.add_argument('--num-studies', type=int, default=1,
                        help='Number of studies to generate')

    parser.add_argument('--num-series', type=int, default=1,
                        help='Number of series per study')

    parser.add_argument('--num-instances', type=int, default=1,
                        help='Number of instances per series')

    args = parser.parse_args()

    # Validate body part against modality
    if args.modality in MODALITY_CONFIGS and "body_parts" in MODALITY_CONFIGS[args.modality]:
        valid_body_parts = MODALITY_CONFIGS[args.modality]["body_parts"]
        if args.body_part not in valid_body_parts:
            print(f"Warning: {args.body_part} is not a standard body part for {args.modality}.")
            print(f"Valid body parts for {args.modality}: {', '.join(valid_body_parts)}")
            response = input("Continue anyway? (y/n): ")
            if response.lower() != 'y':
                return

    # Create main output directory
    os.makedirs(args.output_dir, exist_ok=True)

    # Generate each study
    for i in range(1, args.num_studies + 1):
        study_dir = os.path.join(args.output_dir, f"study_{i}")
        os.makedirs(study_dir, exist_ok=True)

        print(f"Generating study {i}/{args.num_studies}...")

        # Generate study-level information
        study_uid = generate_uid()
        study_id = f"S{random.randint(1000, 9999)}"
        accession_number = generate_accession_number()

        # Generate patient information
        patient_name = generate_patient_name()
        patient_id = generate_patient_id()
        patient_sex = random.choice(['M', 'F'])

        # Generate random birth date (18-90 years old)
        current_year = datetime.datetime.now().year
        birth_year = current_year - random.randint(18, 90)
        birth_month = random.randint(1, 12)
        birth_day = random.randint(1, 28)  # Simplified to avoid month length issues
        patient_birth_date = f"{birth_year}{birth_month:02d}{birth_day:02d}"

        # Generate study date (within last 2 years)
        study_days_ago = random.randint(0, 730)  # Up to 2 years ago
        study_date_obj = datetime.datetime.now() - datetime.timedelta(days=study_days_ago)
        study_date = study_date_obj.strftime('%Y%m%d')

        # Get template
        template = create_dicom_template()

        # Generate each series
        for series_number in range(1, args.num_series + 1):
            # Generate series UID
            series_uid = generate_uid()

            # Select series type based on modality
            if args.modality in MODALITY_CONFIGS and "series_types" in MODALITY_CONFIGS[args.modality]:
                series_type = random.choice(MODALITY_CONFIGS[args.modality]["series_types"])
            else:
                series_type = "STANDARD"

            # Generate series directory
            series_dir = os.path.join(study_dir, f"series_{series_number}")
            os.makedirs(series_dir, exist_ok=True)

            # Check if the body part should have laterality
            laterality = get_laterality(args.body_part)

            # Generate each instance
            for instance_number in range(1, args.num_instances + 1):
                # Generate instance UID
                instance_uid = generate_uid()

                # Create file path
                file_name = f"{args.modality}.{series_number}.{instance_number}.dcm"
                file_path = os.path.join(series_dir, file_name)

                # Create the DICOM file
                create_dicom_from_template(
                    template, file_path,
                    study_uid, series_uid, instance_uid,
                    instance_number, series_number,
                    patient_id, patient_name, study_date,
                    args.modality, args.body_part, series_type,
                    accession_number, study_id,
                    patient_birth_date, patient_sex
                )

        print(f"Generated study with UID: {study_uid}")

    print(f"Successfully generated {args.num_studies} studies in {args.output_dir}")


if __name__ == "__main__":
    main()
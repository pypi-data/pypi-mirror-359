#!/usr/bin/env python3
"""
DICOM file creation from templates for DICOM Generator
"""

import os
import tempfile
import subprocess
import random
from utils.uid_generator import generate_uid
from data.modality_configs import MODALITY_CONFIGS


def create_dicom_from_template(template_content, output_path, metadata):
    """
    Create a DICOM file from a template, replacing placeholders with actual values

    Args:
        template_content (str): The template DICOM content
        output_path (str): Path where the DICOM file will be saved
        metadata (dict): Dictionary of metadata values to replace in the template

    Returns:
        str or None: Path to the created DICOM file, or None if an error occurred
    """
    # Make a copy of the template content for modification
    modified_template = template_content

    # Process laterality separately as it might need to be removed
    if "Laterality" in metadata:
        laterality = metadata["Laterality"]
        if laterality:
            modified_template = modified_template.replace("[Laterality]", laterality)
        else:
            # Remove the laterality tag if not applicable
            modified_template = modified_template.replace(
                "(0020,0060) CS [Laterality]                             # 0, 1 Laterality\n", "")

    # Add modality-specific replacements
    modality = metadata.get("Modality")
    if modality:
        add_modality_specific_replacements(metadata, modality)

    # Apply all replacements
    for key, value in metadata.items():
        placeholder = f"[{key}]"
        if placeholder in modified_template and value is not None:
            modified_template = modified_template.replace(placeholder, str(value))

    # Create the temporary dump file
    temp_dump_file = tempfile.mktemp(suffix='.dump')
    with open(temp_dump_file, 'w') as f:
        f.write(modified_template)

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


def add_modality_specific_replacements(metadata, modality):
    """
    Add modality-specific fields to the metadata dictionary

    Args:
        metadata (dict): Dictionary of metadata to be updated
        modality (str): DICOM modality (CT, MR, etc.)
    """
    # Get slice thickness and pixel spacing
    config = MODALITY_CONFIGS.get(modality, {})

    slice_thickness = metadata.get("SliceThickness")
    if not slice_thickness and "slice_thickness" in config:
        metadata["SliceThickness"] = str(random.choice(config["slice_thickness"]))

    pixel_spacing = metadata.get("PixelSpacing")
    if not pixel_spacing and "pixel_spacing" in config:
        spacing = random.choice(config["pixel_spacing"])
        metadata["PixelSpacing"] = f"{spacing}\\{spacing}"

    # Process slice z position based on instance number
    instance_number = int(metadata.get("InstanceNumber", "1"))
    slice_thickness_value = float(metadata.get("SliceThickness", "1.0"))
    slice_z_position = float(instance_number - 1) * slice_thickness_value

    # Modality specific tags
    if modality == "CT":
        update_ct_metadata(metadata, slice_z_position)
    elif modality == "MR":
        update_mr_metadata(metadata, slice_z_position)
    elif modality == "US":
        update_us_metadata(metadata)
    elif modality == "CR":
        update_cr_metadata(metadata)


def update_ct_metadata(metadata, slice_z_position):
    """Update metadata for CT modality"""
    metadata.update({
        "=CTImageStorage": "1.2.840.10008.5.1.4.1.1.2",
        "KVP": "120",
        "XRayTubeCurrent": "400",
        "ConvolutionKernel": "STANDARD",
        "ImagePositionPatient": f"0\\0\\{slice_z_position}",
        "ImageOrientationPatient": "1\\0\\0\\0\\1\\0",
        "SliceLocation": str(slice_z_position),
        "ReconstructionDiameter": str(random.uniform(100, 500)),
        "DistanceSourceToDetector": str(random.uniform(800, 1200)),
        "DistanceSourceToPatient": str(random.uniform(400, 800)),
        "GantryDetectorTilt": "0",
        "TableHeight": str(random.uniform(150, 250)),
        "RotationDirection": "CW",
        "ExposureTime": str(random.randint(500, 2000)),
        "Exposure": str(random.randint(50, 500)),
        "FilterType": "BODY",
        "GeneratorPower": str(random.randint(20, 60)),
        "FocalSpot": "1.2",
        "FrameOfReferenceUID": generate_uid(),
        "PositionReferenceIndicator": "",
    })


def update_mr_metadata(metadata, slice_z_position):
    """Update metadata for MR modality"""
    metadata.update({
        "=CTImageStorage": "1.2.840.10008.5.1.4.1.1.4",
        "ImagePositionPatient": f"0\\0\\{slice_z_position}",
        "ImageOrientationPatient": "1\\0\\0\\0\\1\\0",
        "SliceLocation": str(slice_z_position),
        "FrameOfReferenceUID": generate_uid(),
        "PositionReferenceIndicator": "",
    })


def update_us_metadata(metadata):
    """Update metadata for US modality"""
    metadata.update({
        "=CTImageStorage": "1.2.840.10008.5.1.4.1.1.6.1",
    })


def update_cr_metadata(metadata):
    """Update metadata for CR modality"""
    metadata.update({
        "=CTImageStorage": "1.2.840.10008.5.1.4.1.1.1",
        "FrameOfReferenceUID": generate_uid(),
    })
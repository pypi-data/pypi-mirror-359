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
python main.py --output-dir ./dicom-data --modality CT --body-part CHEST --num-studies 1 --num-series 3 --num-instances 5
"""

import argparse
import os

# Import generator modules
from make_dicom.generators import (
    generate_patient_demographics,
    generate_institution_info,
    generate_physician_info,
    generate_study_info,
    generate_series_info,
    get_laterality,
    create_dicom_from_template
)
from make_dicom.utils import create_dicom_template, generate_uid


# Import data modules
from make_dicom.data.modality_configs import MODALITY_CONFIGS


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
    return generate_dicom_data(args)


def generate_dicom_data(args):
    """Generate DICOM data based on provided arguments"""
    # Validate body part against modality
    if args.modality in MODALITY_CONFIGS and "body_parts" in MODALITY_CONFIGS[args.modality]:
        valid_body_parts = MODALITY_CONFIGS[args.modality]["body_parts"]
        if args.body_part not in valid_body_parts:
            print(f"Warning: {args.body_part} is not a standard body part for {args.modality}.")
            print(f"Valid body parts for {args.modality}: {', '.join(valid_body_parts)}")
            response = input("Continue anyway? (y/n): ")
            if response.lower() != 'y':
                return False

    # Create main output directory
    os.makedirs(args.output_dir, exist_ok=True)

    # Generate each study
    for i in range(1, args.num_studies + 1):
        study_dir = os.path.join(args.output_dir, f"study_{i}")
        os.makedirs(study_dir, exist_ok=True)

        print(f"Generating study {i}/{args.num_studies}...")

        # Generate patient information
        patient_info = generate_patient_demographics()

        # Generate institution and physician information
        institution_info = generate_institution_info()
        physician_info = generate_physician_info()

        # Generate study-level information
        study_info = generate_study_info(args.modality, args.body_part)

        # Get template
        template = create_dicom_template()

        # Generate each series
        for series_number in range(1, args.num_series + 1):
            # Generate series information
            series_info = generate_series_info(
                study_info["StudyInstanceUID"],
                args.modality,
                args.body_part,
                series_number
            )

            # Get series type from series info
            series_type = series_info.get("SeriesDescription", "").split()[0]

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

                # Combine all metadata for DICOM creation
                metadata = {
                    # Core identifiers
                    "SOPInstanceUID": instance_uid,
                    "InstanceNumber": str(instance_number),
                    "Modality": args.modality,
                    "BodyPartExamined": args.body_part,
                    "Laterality": laterality,

                    # Content dates and times
                    "ContentDate": study_info["StudyDate"],
                    "ContentTime": study_info["StudyTime"],
                    "AcquisitionDate": study_info["StudyDate"],
                    "AcquisitionTime": study_info["StudyTime"],
                }

                # Update with all other information
                metadata.update(patient_info)
                metadata.update(institution_info)
                metadata.update(physician_info)
                metadata.update(study_info)
                metadata.update(series_info)

                # Create the DICOM file
                create_dicom_from_template(template, file_path, metadata)

        print(f"Generated study with UID: {study_info['StudyInstanceUID']}")

    print(f"Successfully generated {args.num_studies} studies in {args.output_dir}")
    return True


def cli_main():
    """Entry point for the command-line interface."""
    try:
        main()
        return 0
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
DICOM template utilities for DICOM Generator
"""


def create_dicom_template():
    """
    Create a template DICOM file with extended fields

    Returns:
        str: Template content with placeholders for DICOM fields
    """
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
(0018,9309) FD [AcquisitionContrast]                    # 0, 1 AcquisitionContrast

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
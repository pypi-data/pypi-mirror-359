#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os import PathLike
from pathlib import Path
from fhir.resources.R4B import bundle
from pydicom import dcmread
from pydicom import dataset
from tqdm import tqdm
import logging
from typing import Iterable, Union
import dicom2fhir.helpers as helpers
from dicom2fhir.helpers import get_or
from dicom2fhir.dicom2fhirbundle import Dicom2FHIRBundle
from dicom2fhir.dicom_json_proxy import DicomJsonProxy

StrPath = Union[str, PathLike]

def _parse_directory(dcmDir: StrPath, config: dict) -> Iterable[dataset.Dataset]:
    """
    Parse a directory of DICOM files including subdirectories and return instances as a Generator.

    :param dcmDir: Directory containing DICOM files.
    :return: Iterable[dataset.Dataset]
    """
    base = Path(dcmDir)
    if not base.is_dir():
        raise ValueError(f"Directory '{dcmDir}' not found")

    skip_invalid_files = get_or(config, "directory_parser.skip_invalid_files", True)

    def is_dicom_file(path: str) -> bool:
        try:
            with open(path, 'rb') as f:
                f.seek(128)
                return f.read(4) == b'DICM'
        except Exception:
            return False

    for fp in tqdm(base.rglob("*")):

        if not fp.is_file():
            continue
        if skip_invalid_files and not is_dicom_file(str(fp)):
            logging.warning(f"Skipping invalid DICOM file: {fp}")
            continue

        try:
            yield dcmread(str(fp), stop_before_pixels=True, force=True)
        except:
            logging.exception(f"An error occurred while processing DICOM file {fp}")
            raise

def _create_bundle(instances: Iterable[DicomJsonProxy], config: dict = {}) -> bundle.Bundle:

    dcm2fhir = Dicom2FHIRBundle(config=config)
    
    for ds in instances:
        if not isinstance(ds, DicomJsonProxy):
            raise TypeError("Expected a DicomJsonProxy object")
        dcm2fhir.add(ds)

    return dcm2fhir.create_bundle()

def process_dicom_2_fhir(dcms: StrPath | Iterable[dict], config: dict = {}) -> bundle.Bundle:
    """
    Process DICOM files or datasets into an ImagingStudy FHIR resource.
    
    :param dcms: Either a directory containing DICOM files or an iterable of DICOM datasets.
    :return: ImagingStudy resource.
    """

    def _wrap(instances: Iterable[dataset.Dataset]):
        for instance in instances:
            yield DicomJsonProxy(instance.to_json_dict())

    # use default id function for FHIR resource id generation
    if 'id_function' not in config:
        config['id_function'] = helpers.default_id_function()

    # parse directory of DICOM files
    if isinstance(dcms, StrPath):
        if not Path(dcms).is_dir():
            raise ValueError(f"Expected a directory, got: {dcms}")
        datasets = _parse_directory(dcms, config)
        dicom_json_proxies = _wrap(datasets)
        return _create_bundle(dicom_json_proxies, config)
    # use iterable of DICOM JSON Proxies
    else:
        # guard against non-iterable or non-dict types
        if not isinstance(dcms, Iterable):
            raise TypeError("Expected an iterable of dicts. Got: {}".format(type(dcms)))
        for d in dcms:
            if not isinstance(d, dict):
                raise TypeError("Expected a dict. Got: {}".format(type(d)))

        dicom_json_proxies = [DicomJsonProxy(d) for d in dcms]
        return _create_bundle(dicom_json_proxies, config)

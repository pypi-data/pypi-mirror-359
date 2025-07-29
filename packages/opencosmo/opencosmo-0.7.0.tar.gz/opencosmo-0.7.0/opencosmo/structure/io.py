from collections import defaultdict
from pathlib import Path
from typing import Iterable, Optional

import h5py

from opencosmo import dataset as d
from opencosmo import io
from opencosmo import structure as s
from opencosmo.header import OpenCosmoHeader, read_header
from opencosmo.structure.builder import build_dataset

LINK_ALIASES = {  # Left: Name in file, right: Name in collection
    "sodbighaloparticles_star_particles": "star_particles",
    "sodbighaloparticles_dm_particles": "dm_particles",
    "sodbighaloparticles_gravity_particles": "gravity_particles",
    "sodbighaloparticles_agn_particles": "agn_particles",
    "sodbighaloparticles_gas_particles": "gas_particles",
    "sod_profile": "halo_profiles",
    "galaxyproperties": "galaxy_properties",
    "galaxyparticles_star_particles": "star_particles",
}

ALLOWED_LINKS = {  # h5py.Files that can serve as a link holder and
    "halo_properties": ["halo_particles", "halo_profiles", "galaxy_properties"],
    "galaxy_properties": ["galaxy_particles"],
}


def verify_links(*headers: OpenCosmoHeader) -> tuple[str, list[str]]:
    """
    Verify that the links in the headers are valid. This means that the
    link holder has a corresponding link target and that the link target
    is of the correct type. It also verifies that the linked files are from
    the same simulation. Returns a dictionary where the keys are the
    link holder files and the values are lists of the corresponding link.

    Raises an error if the links are not valid, otherwise returns the links.
    """

    data_types = [header.file.data_type for header in headers]
    if len(set(data_types)) != len(data_types):
        raise ValueError("Data types in files must be unique to link correctly")

    properties_files = [dt for dt in data_types if dt in ALLOWED_LINKS]
    if not properties_files:
        raise ValueError("No valid link holder files found in headers")

    dtypes_to_headers = {header.file.data_type: header for header in headers}

    links = defaultdict(list)  # {file: [link_header, ...]}
    for file in properties_files:
        for link in ALLOWED_LINKS[file]:
            try:
                link_header = dtypes_to_headers[link]
                # Check that the headers come from the same simulation
                if link_header.simulation != dtypes_to_headers[file].simulation:
                    raise ValueError(f"Simulation mismatch between {file} and {link}")
                links[file].append(link)
            except KeyError:
                continue  # No link header found for this file

    has_links = [file in links for file in properties_files]
    # Properties files also need to have the same simulation
    if len(properties_files) > 1:
        # need exactly one true (for now)
        if sum(has_links) != 1:
            raise NotImplementedError("Chained links are not yet supported")
    for file in properties_files:
        if (
            dtypes_to_headers[file].simulation
            != dtypes_to_headers[properties_files[0]].simulation
        ):
            raise ValueError(
                f"Simulation mismatch between {file} and {properties_files[0]}"
            )
    properties_files = [
        file for file, has_link in zip(properties_files, has_links) if has_link
    ]
    property_file = properties_files[0]
    return property_file, links[property_file]


def open_linked_files(*files: Path):
    """
    Open a collection of files that are linked together, such as a
    properties file and a particle file.

    """
    if len(files) == 1 and isinstance(files[0], list):
        return open_linked_files(*files[0])

    file_handles = [h5py.File(file, "r") for file in files]
    headers = [read_header(file) for file in file_handles]
    properties_file, linked_files = verify_links(*headers)
    properties_index = next(
        index
        for index, header in enumerate(headers)
        if header.file.data_type == properties_file
    )
    properties_file = file_handles.pop(properties_index)
    properties_dataset = io.open(properties_file)
    if not isinstance(properties_dataset, d.Dataset):
        raise ValueError(
            "Properties file must contain a single dataset, but found more"
        )

    linked_files_by_type = {
        file["header"]["file"].attrs["data_type"]: file for file in file_handles
    }
    if len(linked_files_by_type) != len(linked_files):
        raise ValueError("Linked files must have unique data types")
    return get_linked_datasets(
        properties_dataset,
        linked_files_by_type,
        properties_file,
        headers[properties_index],
    )


def open_linked_file(
    file_handle: h5py.File,
    datasets_to_get: Optional[Iterable[str]] = None,
) -> s.StructureCollection:
    """
    Open a single file that contains both properties and linked datasets.
    """
    properties_name = list(
        filter(lambda name: "properties" in name, file_handle.keys())
    )

    header = read_header(file_handle)
    if len(properties_name) == 2:
        if (
            "galaxy_properties" in properties_name
            and "halo_properties" in properties_name
        ):
            properties_name = ["halo_properties"]
            # Custom handling for now
        else:
            raise ValueError(
                "Multiple properties datasets found, please specify which one to use"
            )

    elif len(properties_name) == 0:
        raise ValueError("No properties dataset found in file")

    properties_name = properties_name[0]
    names_to_ignore = [properties_name, "header"] + list(datasets_to_get or [])
    other_datasets = [
        name for name in file_handle.keys() if name not in names_to_ignore
    ]
    if not other_datasets:
        raise ValueError("No linked datasets found in file")
    linked_groups_by_type = {name: file_handle[name] for name in other_datasets}
    properties_dataset = io.open(file_handle[properties_name])
    if not isinstance(properties_dataset, d.Dataset):
        raise ValueError("Properties dataset must be a single dataset")

    return get_linked_datasets(
        properties_dataset, linked_groups_by_type, file_handle[properties_name], header
    )


def get_linked_datasets(
    properties_dataset: d.Dataset,
    linked_files_by_type: dict[str, h5py.File | h5py.Group],
    properties_file: h5py.File,
    header: OpenCosmoHeader,
) -> s.StructureCollection:
    datasets = {}
    for dtype, pointer in linked_files_by_type.items():
        if "data" not in pointer.keys():
            datasets.update({k: pointer[k] for k in pointer.keys() if k != "header"})
        else:
            datasets.update({dtype: pointer})

    link_handlers = get_link_handlers(properties_file, datasets, header)
    output = {}
    for key, handler in link_handlers.items():
        if key in LINK_ALIASES:
            output[LINK_ALIASES[key]] = handler
        else:
            output[key] = handler

    return s.StructureCollection(properties_dataset, header, output)


def get_link_handlers(
    link_file: h5py.File | h5py.Group,
    linked_files: dict[str, h5py.File | h5py.Group],
    header: OpenCosmoHeader,
) -> dict[str, s.LinkedDatasetHandler]:
    if "data_linked" not in link_file.keys():
        raise KeyError("No linked datasets found in the file.")
    links = link_file["data_linked"]

    unique_dtypes = {key.rsplit("_", 1)[0] for key in links.keys()}
    output_links = {}
    for dtype in unique_dtypes:
        if dtype not in linked_files and LINK_ALIASES.get(dtype) not in linked_files:
            continue  # Skip if the linked file is not provided

        key = LINK_ALIASES.get(dtype, dtype)
        if "data" not in linked_files[key].keys():
            raise KeyError(f"No data group found in linked file for dtype '{dtype}'")

        dataset = build_dataset(linked_files[key], header)
        try:
            start = links[f"{dtype}_start"]
            size = links[f"{dtype}_size"]

            output_links[key] = s.LinkedDatasetHandler(
                (start, size),
                dataset,
            )
        except KeyError:
            index = links[f"{dtype}_idx"]
            output_links[key] = s.LinkedDatasetHandler(index, dataset)
    return output_links

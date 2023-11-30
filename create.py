# from copy import deepcopy

from pathlib import Path

import pandas as pd
import sdmx
import sdmx.message as msg
import sdmx.model.v21 as model
from pycountry import countries

DOI = {
    "report": "10.7922/G2HM56SV",
    "data": "10.5281/zenodo.10148348",
    "data-v1": "10.5281/zenodo.10148349",
}

REMOTE_FILE = {
    "url": f"doi:{DOI['data-v1']}/supplementary_information_GFEI2023_TDC.xlsx",
    "known_hash": "sha256:dac6501c4249182c0dbb3e27ff9840d3115e6ec206cbe39cf07d4861f8cbfe20",
}

# Static structural information
SEGMENT = {
    "large car": "Large car",
    "large suv": "Large SUV",
    "lcv": "Light commercial vehicle",
    "medium car": "Medium car",
    "small car": "Small car",
    "small suv": "Small SUV",
    "unclassified": "unclassified",
}

POWERTRAIN = {
    "ev": "Battery electric vehicle",
    "hv": "Hybrid vehicle",
    "ice": "Internal combusion engine vehicle",
    "phev": "Plug-in hybrid vehicle",
    "fcv": "Fuel cell vehicle",
    "mhv": "Mild-hybrid vehicle",
    "unclassified": "unclassified",
}

MEASURE = {
    "SEC": (
        "specific_energy_cosumption_l_100km",  # [sic]
        "Specific energy consumption",
        "litre / 100 km",
    ),
    "WT": ("weight_kg", "Vehicle mass", "kg"),
    "FP": ("footprint_m2", "Vehicle footprint", "m²"),
    "REG": ("registrations", "Registrations", "1"),
}


def create_structures(file_path: Path) -> msg.StructureMessage:
    """Create data structures."""
    sm = msg.StructureMessage()

    # Create the maintainer agency
    _author = "Report author"
    a = model.Agency(
        id="GFEI_2023",
        name="GFEI 2023 benchmarking contributors",
        contact=[
            model.Contact(
                name="Pierpaolo Cazzola",
                email=["pcazzola@ucdavis.edu"],
                responsibility=_author,
            ),
            model.Contact(
                name="Leonardo Paoli",
                email=["paoli.leonardo@gmail.com"],
                responsibility=_author,
            ),
            model.Contact(
                name="Jacob Teter",
                email=["jacob.teter@gmail.com"],
                responsibility=_author,
            ),
            model.Contact(
                name="Paul Natsuo Kishimoto",
                email=["mail@paul.kishimoto.name"],
                responsibility="Data formatting only",
            ),
        ],
    )

    # Common arguments for creating maintainable artefacts
    ma_args = dict(
        version="1.0",
        maintainer=a,
        is_external_reference=False,
        is_final=True,
        annotations=[model.Annotation(id="doi", text=DOI["data"])],
    )

    # Create an agency scheme to store
    as_ = model.AgencyScheme(id="AGENCIES", **ma_args)
    as_.append(a)
    sm.add(as_)

    # Create the SEGMENT and POWERTRAIN code lists using static data
    for codelist_id, codes in ("SEGMENT", SEGMENT), ("POWERTRAIN", POWERTRAIN):
        # Create a code list
        cl = model.Codelist(id=codelist_id, **ma_args)

        # Add codes
        for id, name in codes.items():
            cl.append(model.Code(id=id, name=name))

        # Store in the message
        sm.add(cl)

    # Create the AREA code list
    cl = model.Codelist(
        id="AREA",
        description="Original data has only alpha-3 codes. "
        "Names retrieved from the ISO 3166-1 database via pycountry.",
        **ma_args,
    )

    # Determine unique values from the "data" sheet
    values = pd.read_excel(file_path, sheet_name="data")["CountryISO3"].unique()

    # Add codes
    for value in sorted(values):
        try:
            # Look up a record for this value
            country = countries.lookup(value)
            extra = None
        except LookupError:
            if value == "ROM":
                # Handle a known idiosyncrasy of the data
                country = countries.lookup("ROU")
                extra = "ISO 3166-1 alpha-3 : ROU"
            else:
                raise  # Something else; fail

        # Create a code
        cl.append(model.Code(id=value, name=country.name, description=extra))

    sm.add(cl)

    # Create a concept scheme containing the measures
    cs = model.ConceptScheme(id="MEASURE", **ma_args)
    for id, info in MEASURE.items():
        cs.append(model.Concept(id=id, name=info[1]))
    sm.add(cs)

    # Create the data structure definitions and data flows

    # Common dimensions
    dims = []
    for id in "AREA", "SEGMENT", "POWERTRAIN":
        dims.append(
            model.Dimension(
                id=id,
                # concept_identity=...,
                local_representation=model.Representation(enumerated=sm.codelist[id]),
            )
        )
    dims.append(model.Dimension(id="YEAR"))

    # Read description text from file
    desc = Path("description.txt").read_text()

    for id, info in MEASURE.items():
        # Data structure definition (DSD)
        dsd = model.DataStructureDefinition(id=id, **ma_args)
        # Use the common dimensions
        dsd.dimensions.extend(dims)
        # Record the primary measure
        dsd.measures.append(model.PrimaryMeasure(id=id, concept_identity=cs[id]))

        # Data flow structured by the DSD
        dfd = model.DataflowDefinition(
            id=id, **ma_args, structure=dsd, description=desc
        )

        # Store both
        sm.add(dsd)
        sm.add(dfd)

    return sm


def convert_data(file_path: Path, structures: msg.StructureMessage) -> msg.DataMessage:
    """Convert data to SDMX."""
    sm = structures  # Shorthand

    dm = msg.DataMessage()

    # - Read data from Excel file
    # - Convert column names to dimension names; set index
    df = (
        pd.read_excel(file_path, sheet_name="data")
        .rename(
            columns={
                "CountryISO3": "AREA",
                "segment": "SEGMENT",
                "powertrain": "POWERTRAIN",
                "year": "YEAR",
            }
        )
        .set_index(["AREA", "SEGMENT", "POWERTRAIN", "YEAR"])
    )

    # Convert data for each measure to data set
    for id, info in MEASURE.items():
        # Retrieve structure information
        dsd = sm.structure[id]
        column_name = info[0]

        def _make_obs(index, value):
            kv = {
                "AREA": sm.codelist["AREA"][index[0]],
                "SEGMENT": sm.codelist["SEGMENT"][index[1]],
                "POWERTRAIN": sm.codelist["POWERTRAIN"][index[2]],
                "YEAR": index[3],
            }
            return model.Observation(
                dimension=dsd.make_key(model.Key, kv),
                value=value,
                value_for=dsd.measures[0].concept_identity,
            )

        # Convert each row into an Observation
        obs = map(lambda item: _make_obs(*item), df[column_name].items())

        # Create a data set containing the observations
        ds = model.StructureSpecificDataSet(
            described_by=sm.dataflow[id], structured_by=dsd, obs=list(obs)
        )

        # Add to the data message
        dm.data.append(ds)

    return dm


def main():
    import zipfile
    from itertools import chain

    import pooch  # type: ignore [import-untyped]

    # Retrieve the file from Zenodo
    file_path = pooch.retrieve(**REMOTE_FILE)

    # Create SDMX structure information
    sm = create_structures(file_path)

    with open("structure.xml", "wb") as f:
        f.write(sdmx.to_xml(sm, pretty_print=True))

    # Convert data to SDMX
    dm = convert_data(file_path, sm)

    # Write data for each data set/flow in separate XML and CSV files
    for ds in dm.data:
        name = f"data-{ds.described_by.id}"

        _dm = msg.DataMessage(header=dm.header, data=[ds])
        with open(f"{name}.xml", "wb") as f:
            f.write(sdmx.to_xml(_dm, pretty_print=True))

        with open(f"{name}.csv", "w") as f:
            f.write(sdmx.to_csv(ds))

    # Compress the data
    cwd = Path.cwd()
    with zipfile.ZipFile("all.zip", mode="w", compression=zipfile.ZIP_LZMA) as zf:
        for p in chain(cwd.glob("*.xml"), cwd.glob(".csv")):
            zf.write(p)


if __name__ == "__main__":
    main()

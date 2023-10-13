# from copy import deepcopy

import pandas as pd
import sdmx
import sdmx.message as msg
import sdmx.model.v21 as model
from pycountry import countries

FILENAME = "supplementary_information_gfei2023_tdc.xlsx"

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


def create_structures() -> msg.StructureMessage:
    """Create data structures."""
    sm = msg.StructureMessage()

    # Create the maintainer agency
    a = model.Agency(
        id="GFEI_2023",
        name="GFEI 2023 benchmarking authors",
        contact=[
            model.Contact(name="Pierpaolo Cazzola"),
            model.Contact(name="Jacob Teter"),
            model.Contact(name="Leonardo Paoli", email=["paoli.leonardo@gmail.com"]),
            model.Contact(
                name="Paul Natsuo Kishimoto", email=["mail@paul.kishimoto.name"]
            ),
        ],
    )

    # Common arguments for creating maintainable artefacts
    ma_args = dict(
        version="1.0", maintainer=a, is_external_reference=False, is_final=True
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
        **ma_args
    )

    # Determine unique values from the "data" sheet
    values = pd.read_excel(FILENAME, sheet_name="data")["CountryISO3"].unique()

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

    for id, info in MEASURE.items():
        # Data structure definition (DSD)
        dsd = model.DataStructureDefinition(id=id, **ma_args)
        # Use the common dimensions
        dsd.dimensions.extend(dims)
        # Record the primary measure
        dsd.measures.append(model.PrimaryMeasure(id=id, concept_identity=cs[id]))

        # Data flow structured by the DSD
        dfd = model.DataflowDefinition(id=id, **ma_args, structure=dsd)

        # Store both
        sm.add(dsd)
        sm.add(dfd)

    return sm


def convert_data(structures) -> msg.DataMessage:
    """Convert data to SDMX."""
    dm = msg.DataMessage()

    df = pd.read_excel(FILENAME, sheet_name="data")

    # TODO convert to data sets in `dm`

    return dm


def main():
    sm = create_structures()

    with open("structure.xml", "wb") as f:
        f.write(sdmx.to_xml(sm, pretty_print=True))

    dm = convert_data(sm)

    with open("data.xml", "wb") as f:
        f.write(sdmx.to_xml(dm, pretty_print=True))


if __name__ == "__main__":
    main()

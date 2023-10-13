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


def create_structures() -> msg.StructureMessage:
    """Create data structures."""
    sm = msg.StructureMessage()

    # TODO Create the maintainer agency

    # Common arguments for creating code lists
    cl_args = dict(is_external_reference=False, is_final=True)

    # Create the SEGMENT and POWERTRAIN code lists using static data
    for codelist_id, codes in ("SEGMENT", SEGMENT), ("POWERTRAIN", POWERTRAIN):
        # Create a code list
        cl = model.Codelist(id=codelist_id, **cl_args)

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
        **cl_args
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

    # TODO Create the YEAR code list
    # TODO Create the concept scheme with the measures
    # TODO Create the data structure definition(s) and data frame(s)

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

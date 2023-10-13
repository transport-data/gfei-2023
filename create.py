import pandas as pd
import sdmx
import sdmx.message as msg
import sdmx.model.v21 as model

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
    # TODO Create the AREA code list

    # Create the SEGMENT and POWERTRAIN code lists using static data
    for codelist_id, codes in ("SEGMENT", SEGMENT), ("POWERTRAIN", POWERTRAIN):
        # Create a code list
        cl = model.Codelist(id=codelist_id, is_external_reference=False, is_final=True)

        # Add codes
        for id, name in codes.items():
            cl.append(model.Code(id=id, name=name))

        # Store in the message
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

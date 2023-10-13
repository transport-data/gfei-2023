import pandas as pd
import sdmx
import sdmx.message as msg

FILENAME = "supplementary_information_gfei2023_tdc.xlsx"

def create_structures() -> msg.StructureMessage:
    """Create data structures."""
    sm = msg.StructureMessage()

    # TODO Create the maintainer agency
    # TODO Create the AREA code list
    # TODO Create the SEGMENT code list
    # TODO Create the POWERTRAIN code list
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

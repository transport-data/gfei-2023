import sdmx
import sdmx.message as msg


def main():
    sm = msg.StructureMessage()

    with open("structure.xml", "wb") as f:
        f.write(sdmx.to_xml(sm, pretty_print=True))

    dm = msg.DataMessage()

    with open("data.xml", "wb") as f:
        f.write(sdmx.to_xml(dm, pretty_print=True))


if __name__ == "__main__":
    main()

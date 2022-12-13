import argparse


def main(argv=None):
    print(argv)
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="*")
    args = parser.parse_args(argv)

    print(args)

    return 0


# if __name__ == "__main__":
#     raise SystemExit(main())

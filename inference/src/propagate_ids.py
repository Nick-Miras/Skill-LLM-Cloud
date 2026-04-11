import argparse
from pathlib import Path

import pandas as pd


def propagate_ids_to_multiindex(
    input_csv: Path,
    output_csv: Path,
    id_column: str = "ID",
) -> None:
    """Forward-fill sparse IDs and write output with a MultiIndex.

    The ID value is propagated downward until the next non-empty ID appears.
    The output is written as CSV with a MultiIndex using [id_column, second_index_column].
    """
    df = pd.read_csv(input_csv)

    if id_column not in df.columns:
        raise ValueError(f"Column '{id_column}' was not found in {input_csv}")

    # Treat blank strings as missing so they can be forward-filled.
    df[id_column] = df[id_column].replace(r"^\s*$", pd.NA, regex=True)

    # Propagate each ID down to following rows until a new ID is present.
    df[id_column] = df[id_column].ffill()

    # Normalize IDs as nullable integers to avoid float representations (e.g., 1.0).
    numeric_ids = pd.to_numeric(df[id_column], errors="coerce")
    if numeric_ids.isna().any():
        raise ValueError(
            f"Column '{id_column}' contains non-numeric values after propagation."
        )
    df[id_column] = numeric_ids.astype("Int64")

    # Build a MultiIndex from propagated ID + the secondary key (e.g., UID).
    df = df.set_index([id_column])

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_csv)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Propagate sparse IDs to following rows and write a CSV with a MultiIndex."
        )
    )
    parser.add_argument(
        "--input-csv",
        type=Path,
        required=True,
        help="Path to the source CSV file.",
    )
    parser.add_argument(
        "--output-csv",
        type=Path,
        required=True,
        help="Path to write the transformed CSV file.",
    )
    parser.add_argument(
        "--id-column",
        type=str,
        default="ID",
        help="Name of the ID column to propagate (default: ID).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    propagate_ids_to_multiindex(
        input_csv=args.input_csv,
        output_csv=args.output_csv,
        id_column=args.id_column
    )


if __name__ == "__main__":
    main()

import polars as pl
import pandas as pd


def info_schema_parser(searchx, info_schema):
    """Pulls matching sequence of information schema from entire text corpus."""
    result_data = []

    print(
        f"Processing {len(info_schema)} schema entries against {len(searchx)} text entries..."
    )

    for idx, row in enumerate(info_schema.itertuples(index=False)):
        if idx % 10 == 0:  # Progress indicator - every 10 rows
            print(f"Processed {idx}/{len(info_schema)} schema entries...")

        table_catalog, table_schema, table_name, column_name = row

        # OPTIMIZATION 1: Check which fields are valid (handle each field independently)
        column_name_valid = not pd.isna(column_name) and str(column_name).strip()
        table_name_valid = not pd.isna(table_name) and str(table_name).strip()
        table_catalog_valid = not pd.isna(table_catalog) and str(table_catalog).strip()
        table_schema_valid = not pd.isna(table_schema) and str(table_schema).strip()

        # OPTIMIZATION 2: Skip entire row only if ALL fields are invalid
        if not any(
            [
                column_name_valid,
                table_name_valid,
                table_catalog_valid,
                table_schema_valid,
            ]
        ):
            continue

        # OPTIMIZATION 3: Pre-compute lowercase versions only for valid fields
        column_name_lower = str(column_name).lower() if column_name_valid else ""
        table_name_lower = str(table_name).lower() if table_name_valid else ""
        table_catalog_lower = str(table_catalog).lower() if table_catalog_valid else ""
        table_schema_lower = str(table_schema).lower() if table_schema_valid else ""

        # Loop through searchx (polars DataFrame) - keep original structure
        for search_row in searchx.iter_rows(named=True):
            unc = search_row["unc"]
            text = search_row["text"]
            ext = search_row["ext"]

            # OPTIMIZATION 4: Skip if text is null/empty
            if not text or pd.isna(text):
                continue

            # Convert text to string and lowercase
            line_str = str(text).lower()

            # Check column_name conditions (only if column_name is valid)
            if column_name_valid:
                flag_1 = 1 if f" {column_name_lower} " in f" {line_str} " else 0
                flag_2 = 1 if f"({column_name_lower})" in line_str else 0
                flag_3 = 1 if f".{column_name_lower}" in line_str else 0
            else:
                flag_1 = flag_2 = flag_3 = 0

            # Check table_catalog conditions (only if catalog is valid)
            if table_catalog_valid:
                flag_4 = 1 if f" {table_catalog_lower} " in f" {line_str} " else 0
                flag_5 = 1 if f"({table_catalog_lower})" in line_str else 0
                flag_6 = 1 if f".{table_catalog_lower}" in line_str else 0
            else:
                flag_4 = flag_5 = flag_6 = 0

            # Check table_schema conditions (only if schema is valid)
            if table_schema_valid:
                flag_7 = 1 if f" {table_schema_lower} " in f" {line_str} " else 0
                flag_8 = 1 if f"({table_schema_lower})" in line_str else 0
                flag_9 = 1 if f".{table_schema_lower}" in line_str else 0
            else:
                flag_7 = flag_8 = flag_9 = 0

            # Check table_name conditions (only if table_name is valid)
            if table_name_valid:
                flag_10 = 1 if f" {table_name_lower} " in f" {line_str} " else 0
                flag_11 = 1 if f"({table_name_lower})" in line_str else 0
                flag_12 = 1 if f".{table_name_lower}" in line_str else 0
            else:
                flag_10 = flag_11 = flag_12 = 0

            # Python conventions - table['column'] or table["column"] (only if both table_name and column_name are valid)
            if table_name_valid and column_name_valid:
                flag_13 = (
                    1 if f"{table_name_lower}['{column_name_lower}']" in line_str else 0
                )
                flag_14 = (
                    1 if f'{table_name_lower}["{column_name_lower}"]' in line_str else 0
                )
            else:
                flag_13 = flag_14 = 0

            # Python conventions for catalog (only if both catalog and column_name are valid)
            if table_catalog_valid and column_name_valid:
                flag_15 = (
                    1
                    if f"{table_catalog_lower}['{column_name_lower}']" in line_str
                    else 0
                )
                flag_16 = (
                    1
                    if f'{table_catalog_lower}["{column_name_lower}"]' in line_str
                    else 0
                )
            else:
                flag_15 = flag_16 = 0

            # Python conventions for schema (only if both schema and column_name are valid)
            if table_schema_valid and column_name_valid:
                flag_17 = (
                    1
                    if f"{table_schema_lower}['{column_name_lower}']" in line_str
                    else 0
                )
                flag_18 = (
                    1
                    if f'{table_schema_lower}["{column_name_lower}"]' in line_str
                    else 0
                )
            else:
                flag_17 = flag_18 = 0

            # Python dot notation (only if both table_name and column_name are valid)
            if table_name_valid and column_name_valid:
                flag_19 = (
                    1 if f"{table_name_lower}.{column_name_lower}" in line_str else 0
                )
            else:
                flag_19 = 0

            # Python dot notation for catalog (only if both catalog and column_name are valid)
            if table_catalog_valid and column_name_valid:
                flag_20 = (
                    1 if f"{table_catalog_lower}.{column_name_lower}" in line_str else 0
                )
            else:
                flag_20 = 0

            # Python dot notation for schema (only if both schema and column_name are valid)
            if table_schema_valid and column_name_valid:
                flag_21 = (
                    1 if f"{table_schema_lower}.{column_name_lower}" in line_str else 0
                )
            else:
                flag_21 = 0

            # R conventions - table$column (only if both table_name and column_name are valid)
            if table_name_valid and column_name_valid:
                flag_22 = (
                    1 if f"{table_name_lower}${column_name_lower}" in line_str else 0
                )
            else:
                flag_22 = 0

            # R conventions for catalog (only if both catalog and column_name are valid)
            if table_catalog_valid and column_name_valid:
                flag_23 = (
                    1 if f"{table_catalog_lower}${column_name_lower}" in line_str else 0
                )
            else:
                flag_23 = 0

            # R conventions for schema (only if both schema and column_name are valid)
            if table_schema_valid and column_name_valid:
                flag_24 = (
                    1 if f"{table_schema_lower}${column_name_lower}" in line_str else 0
                )
            else:
                flag_24 = 0

            # Only add to results if at least one condition is met
            if any(
                [
                    flag_1,
                    flag_2,
                    flag_3,
                    flag_4,
                    flag_5,
                    flag_6,
                    flag_7,
                    flag_8,
                    flag_9,
                    flag_10,
                    flag_11,
                    flag_12,
                    flag_13,
                    flag_14,
                    flag_15,
                    flag_16,
                    flag_17,
                    flag_18,
                    flag_19,
                    flag_20,
                    flag_21,
                    flag_22,
                    flag_23,
                    flag_24,
                ]
            ):
                result_data.append(
                    {
                        "unc": unc,
                        "ext": ext,
                        "table_catalog": table_catalog,
                        "table_schema": table_schema,
                        "table_name": table_name,
                        "column_name": column_name,
                        "line": text,
                        # Original column name flags
                        "flag_1_column_word_boundary": flag_1,
                        "flag_2_column_parentheses": flag_2,
                        "flag_3_column_dot_notation": flag_3,
                        # Original table catalog flags
                        "flag_4_catalog_word_boundary": flag_4,
                        "flag_5_catalog_parentheses": flag_5,
                        "flag_6_catalog_dot_notation": flag_6,
                        # Original table schema flags
                        "flag_7_schema_word_boundary": flag_7,
                        "flag_8_schema_parentheses": flag_8,
                        "flag_9_schema_dot_notation": flag_9,
                        # Original table name flags
                        "flag_10_table_word_boundary": flag_10,
                        "flag_11_table_parentheses": flag_11,
                        "flag_12_table_dot_notation": flag_12,
                        # Python bracket notation flags
                        "flag_13_python_table_single_quotes": flag_13,
                        "flag_14_python_table_double_quotes": flag_14,
                        "flag_15_python_catalog_single_quotes": flag_15,
                        "flag_16_python_catalog_double_quotes": flag_16,
                        "flag_17_python_schema_single_quotes": flag_17,
                        "flag_18_python_schema_double_quotes": flag_18,
                        # Python dot notation flags
                        "flag_19_python_table_dot": flag_19,
                        "flag_20_python_catalog_dot": flag_20,
                        "flag_21_python_schema_dot": flag_21,
                        # R dollar notation flags
                        "flag_22_r_table_dollar": flag_22,
                        "flag_23_r_catalog_dollar": flag_23,
                        "flag_24_r_schema_dollar": flag_24,
                    }
                )

    print(f"Found {len(result_data)} matches")

    ## Create Polars DataFrame from collected results
    result = pl.DataFrame(result_data)
    result.estimated_size("mb")

    ## Derive information schema HashTags
    result = result.with_columns(
        pl.concat_str(
            [
                pl.when(pl.col("table_catalog").is_not_null()).then(
                    pl.col("table_catalog")
                ),
                pl.when(pl.col("table_schema").is_not_null()).then(
                    pl.col("table_schema")
                ),
                pl.when(pl.col("table_name").is_not_null()).then(pl.col("table_name")),
                pl.when(pl.col("column_name").is_not_null()).then(
                    pl.col("column_name")
                ),
            ],
            separator=",",
            ignore_nulls=True,
        ).alias("HashTags")
    )

    return result

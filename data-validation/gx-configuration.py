import great_expectations as gx

context = gx.get_context()

# Create datasource
try:
    datasource = context.get_datasource("f3_backblast")
except ValueError:
    datasource = context.sources.add_sql(
        name="f3_backblast",
        connection_string="${COCKROACH_CONNECTION_STRING}",
        create_temp_table=False
    )

# Create assets
try:
    asset = datasource.get_asset("backblast_greenlevel")
except LookupError:
    asset = datasource.add_table_asset(
        name="backblast_greenlevel",
        table_name="backblast_greenlevel"
    )

try:
    asset = datasource.get_asset("backblast_churham")
except LookupError:
    asset = datasource.add_table_asset(
        name="backblast_churham",
        table_name="backblast_churham"
    )

try:
    asset = datasource.get_asset("backblast_peakcity")
except LookupError:
    asset = datasource.add_table_asset(
        name="backblast_peakcity",
        table_name="backblast_peakcity"
    )


try:
    asset = datasource.get_asset("ao_info_greenlevel")
except LookupError:
    asset = datasource.add_table_asset(
        name="ao_info_greenlevel",
        table_name="ao_info_greenlevel"
    )


try:
    asset = datasource.get_asset("ao_info_churham")
except LookupError:
    asset = datasource.add_table_asset(
        name="ao_info_churham",
        table_name="ao_info_churham"
    )


try:
    asset = datasource.get_asset("ao_info_peakcity")
except LookupError:
    asset = datasource.add_table_asset(
        name="ao_info_peakcity",
        table_name="ao_info_peakcity"
    )

try:
    asset = datasource.get_asset("pax_level_values_greenlevel")
except LookupError:
    asset = datasource.add_table_asset(
        name="pax_level_values_greenlevel",
        table_name="pax_level_values_greenlevel"
    )

try:
    asset = datasource.get_asset("pax_level_values_churham")
except LookupError:
    asset = datasource.add_table_asset(
        name="pax_level_values_churham",
        table_name="pax_level_values_churham"
    )

try:
    asset = datasource.get_asset("pax_level_values_peakcity")
except LookupError:
    asset = datasource.add_table_asset(
        name="pax_level_values_peakcity",
        table_name="pax_level_values_peakcity"
    )

# Create Suites
try:
    suite = context.get_expectation_suite("backblast")
except (ValueError, gx.exceptions.GreatExpectationsError):
    suite = context.add_expectation_suite("backblast")

try:
    suite = context.get_expectation_suite("pax_level_values")
except (ValueError, gx.exceptions.GreatExpectationsError):
    suite = context.add_expectation_suite("pax_level_values")

try:
    suite = context.get_expectation_suite("ao_info")
except (ValueError, gx.exceptions.GreatExpectationsError):
    suite = context.add_expectation_suite("ao_info")

# Create Checkpoints
context.add_or_update_checkpoint(
    name="backblast",
    validations=[
        {
            "expectation_suite_name": "backblast",
            "batch_request": {
                "datasource_name": "f3_backblast",
                "data_asset_name": "backblast_peakcity"
            }
        },
        {
            "expectation_suite_name": "backblast",
            "batch_request": {
                "datasource_name": "f3_backblast",
                "data_asset_name": "backblast_greenlevel"
            }
        },
        {
            "expectation_suite_name": "backblast",
            "batch_request": {
                "datasource_name": "f3_backblast",
                "data_asset_name": "backblast_churham"
            }
        }
    ]
)

context.add_or_update_checkpoint(
    name="ao_info",
    validations=[
        {
            "expectation_suite_name": "ao_info",
            "batch_request": {
                "datasource_name": "f3_backblast",
                "data_asset_name": "ao_info_peakcity"
            }
        },
        {
            "expectation_suite_name": "ao_info",
            "batch_request": {
                "datasource_name": "f3_backblast",
                "data_asset_name": "ao_info_greenlevel"
            }
        },
        {
            "expectation_suite_name": "ao_info",
            "batch_request": {
                "datasource_name": "f3_backblast",
                "data_asset_name": "ao_info_churham"
            }
        }
    ]
)

context.add_or_update_checkpoint(
    name="pax_level_values",
    validations=[
        {
            "expectation_suite_name": "pax_level_values",
            "batch_request": {
                "datasource_name": "f3_backblast",
                "data_asset_name": "pax_level_values_peakcity"
            }
        },
        {
            "expectation_suite_name": "pax_level_values",
            "batch_request": {
                "datasource_name": "f3_backblast",
                "data_asset_name": "pax_level_values_greenlevel"
            }
        },
        {
            "expectation_suite_name": "pax_level_values",
            "batch_request": {
                "datasource_name": "f3_backblast",
                "data_asset_name": "pax_level_values_churham"
            }
        }
    ]
)
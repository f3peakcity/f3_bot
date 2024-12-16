import great_expectations as gx

context = gx.get_context(
    mode="cloud",
)

# Create datasource
try:
    datasource = context.data_sources.get("f3_backblast")
except ValueError:
    datasource = context.data_sources.add_sql(
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
    batch_definition = asset.add_batch_definition_whole_table(
        "backblast_green_level"
    )

try:
    asset = datasource.get_asset("backblast_churham")
except LookupError:
    asset = datasource.add_table_asset(
        name="backblast_churham",
        table_name="backblast_churham"
    )
    batch_definition = asset.add_batch_definition_whole_table(
        "backblast_churham"
    )

try:
    asset = datasource.get_asset("backblast_peakcity")
except LookupError:
    asset = datasource.add_table_asset(
        name="backblast_peakcity",
        table_name="backblast_peakcity"
    )
    batch_definition = asset.add_batch_definition_whole_table(
        "backblast_peakcity"
    )


try:
    asset = datasource.get_asset("ao_info_greenlevel")
except LookupError:
    asset = datasource.add_table_asset(
        name="ao_info_greenlevel",
        table_name="ao_info_greenlevel"
    )
    batch_definition = asset.add_batch_definition_whole_table(
        "ao_info_greenlevel"
    )


try:
    asset = datasource.get_asset("ao_info_churham")
except LookupError:
    asset = datasource.add_table_asset(
        name="ao_info_churham",
        table_name="ao_info_churham"
    )
    batch_definition = asset.add_batch_definition_whole_table(
        "ao_info_churham"
    )


try:
    asset = datasource.get_asset("ao_info_peakcity")
except LookupError:
    asset = datasource.add_table_asset(
        name="ao_info_peakcity",
        table_name="ao_info_peakcity"
    )
    batch_definition = asset.add_batch_definition_whole_table(
        "ao_info_peakcity"
    )

try:
    asset = datasource.get_asset("pax_level_values_greenlevel")
except LookupError:
    asset = datasource.add_table_asset(
        name="pax_level_values_greenlevel",
        table_name="pax_level_values_greenlevel"
    )
    batch_definition = asset.add_batch_definition_whole_table(
        "pax_level_values_greenlevel"
    )

try:
    asset = datasource.get_asset("pax_level_values_churham")
except LookupError:
    asset = datasource.add_table_asset(
        name="pax_level_values_churham",
        table_name="pax_level_values_churham"
    )
    batch_definition = asset.add_batch_definition_whole_table(
        "pax_level_values_churham"
    )

try:
    asset = datasource.get_asset("pax_level_values_peakcity")
except LookupError:
    asset = datasource.add_table_asset(
        name="pax_level_values_peakcity",
        table_name="pax_level_values_peakcity"
    )
    batch_definition = asset.add_batch_definition_whole_table(
        "pax_level_values_peakcity"
    )

# Create Suites
try:
    suite = context.suites.get("backblast")
except (ValueError, gx.exceptions.GreatExpectationsError):
    suite = context.suites.add(gx.ExpectationSuite("backblast"))

try:
    suite = context.suites.get("pax_level_values")
except (ValueError, gx.exceptions.GreatExpectationsError):
    suite = context.suites.add(gx.ExpectationSuite("pax_level_values"))

try:
    suite = context.suites.get("ao_info")
except (ValueError, gx.exceptions.GreatExpectationsError):
    suite = context.suites.add(gx.ExpectationSuite("ao_info"))

# Create Checkpoints
try:
    checkpoint = context.checkpoints.get("pax_level_values")
except ValueError:
    context.checkpoints.add(gx.Checkpoint(
        name="backblast",
        validation_definitions=[
            gx.ValidationDefinition(
                name= "backblast_green_level",
                suite = context.suites.get("backblast"),
                data = datasource.get_asset("backblast_peakcity").get_batch_definition("backblast_peakcity")
            ),
            gx.ValidationDefinition(
                name="backblast_green_level",
                suite=context.suites.get("backblast"),
                data=datasource.get_asset("backblast_greenlevel").get_batch_definition("backblast_green_level")
            ),
            gx.ValidationDefinition(
                name="backblast_churham",
                suite=context.suites.get("backblast"),
                data=datasource.get_asset("backblast_churham").get_batch_definition("backblast_churham")
            )
        ]
    ))

try:
    checkpoint = context.checkpoints.get("pax_level_values")
except ValueError:
    context.checkpoints.add(gx.Checkpoint(
        name="ao_info",
        validation_definitions=[
            gx.ValidationDefinition(
                name="ao_info_peakcity",
                suite=context.suites.get("ao_info"),
                data=datasource.get_asset("ao_info_peakcity").get_batch_definition("ao_info_peakcity")
            ),
            gx.ValidationDefinition(
                name="ao_info_greenlevel",
                suite=context.suites.get("ao_info"),
                data=datasource.get_asset("ao_info_greenlevel").get_batch_definition("ao_info_greenlevel")
            ),
            gx.ValidationDefinition(
                name="ao_info_churham",
                suite=context.suites.get("ao_info"),
                data=datasource.get_asset("ao_info_churham").get_batch_definition("ao_info_churham")
            )
        ]
    ))

try:
    checkpoint = context.checkpoints.get("pax_level_values")
except ValueError:
    context.checkpoints.add(gx.Checkpoint(
        name="pax_level_values",
        validation_definitions=[
            gx.ValidationDefinition(
                name="pax_level_values_peakcity",
                suite=context.suites.get("pax_level_values"),
                data=datasource.get_asset("pax_level_values_peakcity").get_batch_definition("pax_level_values_peakcity")
            ),
            gx.ValidationDefinition(
                name="pax_level_values_greenlevel",
                suite=context.suites.get("pax_level_values"),
                data=datasource.get_asset("pax_level_values_greenlevel").get_batch_definition("pax_level_values_greenlevel")
            ),
            gx.ValidationDefinition(
                name="pax_level_values_churham",
                suite=context.suites.get("pax_level_values"),
                data=datasource.get_asset("pax_level_values_churham").get_batch_definition("pax_level_values_churham")
            )
        ]
    ))
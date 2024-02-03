import great_expectations as gx

if __name__ == "__main__":
    context = gx.get_context()
    print("Running checkpoint 'ao_info'...")
    context.run_checkpoint("ao_info")
    print("Running checkpoint 'backblast'...")
    context.run_checkpoint("backblast")
    print("Running checkpoint 'pax_level_values'...")
    context.run_checkpoint("pax_level_values")

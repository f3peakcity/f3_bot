import great_expectations as gx

if __name__ == "__main__":
    context = gx.get_context()
    print("Running checkpoint 'ao_info'...")
    checkpoint = context.checkpoints.get("ao_info")
    checkpoint.run()
    print("Running checkpoint 'backblast'...")
    context.checkpoints.get("backblast")
    checkpoint.run()
    print("Running checkpoint 'pax_level_values'...")
    checkpoint = context.checkpoints.get("pax_level_values")
    checkpoint.run()
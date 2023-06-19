import great_expectations as gx

if __name__ == "__main__":
    context = gx.get_context()
    print("Running checkpoint 'ao_info'...")
    context.run_checkpoint("ao_info")

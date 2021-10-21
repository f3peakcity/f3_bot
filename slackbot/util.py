def get_worked_phrase(summary):
    # If you want to have some fun with customizing the summary...
    # return "got pushed to their max"
    return "posted"


def build_message(backblast_data, logger):
    q_id = backblast_data.get("q_id")
    fng_ids = backblast_data.get("fng_ids")
    pax_ids = backblast_data.get("pax_ids")
    n_visiting_pax = backblast_data.get("n_visiting_pax")
    summary = backblast_data.get("summary")
    ao_id = backblast_data.get("ao_id")
    fngs_raw = backblast_data.get("fngs_raw")

    try:
        all_pax = {q_id} | set(fng_ids) | set(pax_ids)
        n_pax = len(all_pax)

        if n_visiting_pax > 0:
            n_pax += n_visiting_pax

        all_pax_no_q = all_pax - {q_id}
        all_pax_str = ", ".join([f"<@{pax}>" for pax in all_pax_no_q])
        all_pax_str += f" (<@{q_id}> Q)"
        worked_phrase = get_worked_phrase(summary)

        # ao_id: in message
        message = f"{n_pax} {worked_phrase}"
        if ao_id is not None and ao_id != "":
            message += f" at <#{ao_id}>"
        message += "."
        if summary is not None and summary != "":
            message += f"\n{summary}"
        message += f"\n{all_pax_str}"
        if len(fng_ids) > 0:
            fng_str = ", ".join([f"<@{pax}>" for pax in fng_ids])
            message += f"\nFNGs named today: {fng_str}"
        if len(fngs_raw) > 0:
            message += f"\nFNGs not yet in slack: {fngs_raw}"
        if n_visiting_pax > 0:
            message += f"\nJoined by {n_visiting_pax} from outside our region."

        return message
    except Exception as e:
        logger.error(f"Error building message: {e}")


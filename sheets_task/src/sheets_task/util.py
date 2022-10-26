from typing import List
from math import ceil

def get_worked_phrase(summary):
    # If you want to have some fun with customizing the summary...
    # return "got pushed to their max"
    return "posted"


def build_message(backblast_data, logger):
    q_id = backblast_data.get("q_id", "")
    fng_ids = backblast_data.get("fng_ids", [])
    pax_ids = backblast_data.get("pax_ids", [])
    n_visiting_pax = backblast_data.get("n_visiting_pax", 0)
    summary = backblast_data.get("summary", "")
    ao_id = backblast_data.get("ao_id", "")
    pax_no_slack = backblast_data.get("pax_no_slack", "")

    try:
        all_pax = {q_id} | set(fng_ids) | set(pax_ids)
        n_pax = len(all_pax)

        if n_visiting_pax > 0:
            n_pax += n_visiting_pax

        if pax_no_slack is not None and len(pax_no_slack) > 0:
            n_pax_no_slack = len(pax_no_slack.split(","))
            n_pax += n_pax_no_slack

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
        if pax_no_slack is not None and len(pax_no_slack) > 0:
            message += f"\nPax not yet in slack: {pax_no_slack}"
        if n_visiting_pax > 0:
            message += f"\nJoined by {n_visiting_pax} from outside our region."

        return message
    except Exception as e:
        logger.error(f"Error building message: {e}")

def get_message_blocks_from_message_text(message_text: str) -> List[str]:
    # slack imposes a 3000 character-per-block limit
    block_limit = 2900
    message_text_blocks = []
    if len(message_text) > block_limit:
        n_blocks = ceil(len(message_text) / block_limit)
        start = 0
        end = block_limit
        first = message_text[start:end] + "..."
        message_text_blocks.append(first)
        for i in range(1, n_blocks-1):
            start = i * block_limit
            end = (i+1) * block_limit
            message_text_blocks.append("..." + message_text[start:end] + "...")
        message_text_blocks.append("..." + message_text[end:])
    else:
        message_text_blocks.append(message_text)
    return message_text_blocks
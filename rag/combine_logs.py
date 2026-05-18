def combine_logs(logs: list[str]) -> str:
    return "\n".join(log.strip() for log in logs if log and log.strip())

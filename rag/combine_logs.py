def combine_logs(logs):
    return "\n".join(log.strip() for log in logs if log and log.strip())

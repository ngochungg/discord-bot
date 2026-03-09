def get_bar(percent):
    filled = int(percent / 10)
    return "█" * filled + "░" * (10 - filled)
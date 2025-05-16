async def send_long_sys_message(channel, content, prefix="```bash\n", suffix="```"):
    max_len = 2000 - len(prefix) - len(suffix)
    for i in range(0, len(content), max_len):
        part = content[i:i + max_len]
        await channel.send(f"{prefix}{part}{suffix}")

async def send_long_message(channel, content):
    max_len = 2000
    for i in range(0, len(content), max_len):
        part = content[i:i + max_len]
        await channel.send(f"{part}")
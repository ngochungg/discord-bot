from modules.on_pi_cmd import status, docker_ps, update

async def on_sys_cmd(message):
    if message.content.startswith("!status"):
        await status(message)
    if message.content.startswith("!docker_ps"):
        await docker_ps(message)
    if message.content.startswith("!update"):
        await update(message)
from modules.ai_cmd import summarize, translate, fix_grammar
from modules.music_cmd import play, stop, skip, show_queue
from modules.pi_cmd import status, docker_ps, update, minecraft_server, compose, homelab_ls


async def on_sys_cmd(message):
    if message.content.startswith("!status"):
        await status(message)
    elif message.content.startswith("!docker_ps"):
        await docker_ps(message)
    elif message.content.startswith("!update"):
        await update(message)
    elif message.content.startswith("!summarize"):
        # Lấy phần text sau "!summarize "
        message_text = message.content[len("!summarize"):].strip()
        await summarize(message, message_text=message_text)
    elif message.content.startswith("!translate"):
        # Lấy phần text sau "!translate "
        message_text = message.content[len("!translate"):].strip()
        await translate(message, message_text=message_text)
    elif message.content.startswith("!fix_grammar"):
        await fix_grammar(message)
    elif message.content.startswith("!play"):
        message_text = message.content[len("!play"):].strip()
        await play(message, message_text=message_text)
    elif message.content.startswith("!skip"):
        await skip(message)
    elif message.content.startswith("!queue"):
        await show_queue(message)
    elif message.content.startswith("!stop"):
        await stop(message)
    elif message.content.startswith("!minecraft_server"):
        await minecraft_server(message)
    elif message.content.startswith("!compose"):
        await compose(message)
    elif message.content.startswith("!homelab_ls"):
        await homelab_ls(message)

    elif message.content.startswith("!help"):
        help_text = """```
**List commands:**

!status - System status
!docker_ps - List docker is running
!update - Update bot system 
!summarize <text/url> - Summarize text or url
!translate <text> - Translate vi <-> en
!fix_grammar <text> - Fix English grammar 
!minecraft_server - Start a minecraft server
!help - Show this help
```"""
        await message.channel.send(help_text)
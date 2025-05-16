from modules.ai_cmd import summarize, translate, fix_grammar
from modules.pi_cmd import status, docker_ps, update

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
    elif message.content.startswith("!help"):
        help_text = """```
**List commands:**

!status - System status
!docker_ps - List docker is running
!update - Update bot system 
!summarize <text/url> - Summarize text or url
!translate <text> - Translate vi <-> en
!fix_grammar <text> - Fix English grammar 
!help - Show this help
```"""
        await message.channel.send(help_text)
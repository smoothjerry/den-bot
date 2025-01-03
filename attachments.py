import asyncio

import aiohttp
import discord

async def handle_attachments(message: discord.Message):
    # Check if the message contains attachments / yes
    if message.attachments:
        tasks = []
        for attachment in message.attachments:
            # Process only supported file types (images or videos)
            if attachment.content_type and "image" in attachment.content_type:
                tasks.append(process_attachment(attachment, message.channel))

        # Wait for all tasks to complete
        await asyncio.gather(*tasks)
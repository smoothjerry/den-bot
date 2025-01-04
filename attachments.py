import asyncio

import discord

def format_attachment_data(message: discord.Message):
    """
    Format image data from a discord message into image URL messages for OpenAI.
    Use array of image URLs.

    Returns empty list if there are no images.
    """
    # Check if the message contains attachments
    image_data = []
    if message.attachments:
        for attachment in message.attachments:
            # Process only supports image types
            if attachment.content_type and "image" in attachment.content_type:
                query_data = {
                    "type": "image_url",
                    "image_url": {
                        "url": attachment.url,
                    },
                }
        
        image_data.append(query_data)
    
    # prepend a general query that will instruct the model to interpret the images and
    # use that as part of its response.
    if image_data:
        general_image_query = {
            "type": "text",
            "text": "Analyze what is in this image or series of images and use this info in your response to the other user text prompts.",
        }
        image_data.insert(0, general_image_query)

    return image_data
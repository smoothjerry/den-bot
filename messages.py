"""
Helper utils for formatting and interacting with Discord messages.

For example: retrieving chain of message replies.
"""

import discord

CHAIN_LIMIT = 10 # limit of how many replies to fetch. controlling tokens to OpenAI.

async def fetch_reply_chain(message: discord.Message) -> list[discord.Message]:
    """
    Fetch a chain of replies starting from a given message.

    Args:
        message (discord.Message): The starting message.

    Returns:
        list[discord.Message]: A list of messages in the reply chain, from oldest to newest.
    """
    reply_chain = []
    
    # the first message will always be passed to ChatGPT anyway, so skip it by fetching
    # the next newest message in the replies (if it exists).
    current_message = None
    if message.reference and message.reference.message_id:
        current_message = await message.channel.fetch_message(
            message.reference.message_id
        )

    while current_message is not None and len(reply_chain) < CHAIN_LIMIT:
        reply_chain.append(current_message)

        # Fetch the referenced message (if this message is a reply)
        if current_message.reference and current_message.reference.message_id:
            current_message = await current_message.channel.fetch_message(
                current_message.reference.message_id
            )
        else:
            break

    # Reverse to get the order from oldest to newest
    return list(reversed(reply_chain))

def map_reply_chain_to_chatgpt_format(messages: list[discord.Message]) -> list[dict]:
    """
    Map a reply chain to the ChatGPT API format.

    Args:
        messages (List[discord.Message]): A list of Discord messages.

    Returns:
        List[dict]: Formatted messages for ChatGPT.
    """
    formatted_messages = []
    for message in messages:
        role = "user" if not message.author.bot else "assistant"
        formatted_messages.append({
            "role": role,
            "content": message.content
        })
    return formatted_messages

async def format_message_coversation(message: discord.Message) -> list[dict]:
    """
    Fetches a reply chain (if necessary) for message [message] and formats
    into ChatGPT API input.
    """
    reply_chain = await fetch_reply_chain(message)
    formatted_reply_chain = map_reply_chain_to_chatgpt_format(reply_chain)
    return formatted_reply_chain


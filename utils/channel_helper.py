import discord
from datetime import datetime

def get_progress_and_error(category):
    process_channel = discord.utils.get(category.channels, name=lambda n: n.startswith("process-"))
    error_channel = discord.utils.get(category.channels, name=lambda n: n.startswith("error-"))
    progress = int(process_channel.name.split("-")[1]) if process_channel else 0
    error = int(error_channel.name.split("-")[1]) if error_channel else 0
    return progress, error

def build_channel_overwrites(guild):
    overwrites = {guild.default_role: discord.PermissionOverwrite(read_messages=False)}
    player_role = discord.utils.get(guild.roles, name="0001")
    if player_role:
        overwrites[player_role] = discord.PermissionOverwrite(read_messages=True)
    return overwrites

async def create_game_channels(ctx, tz):
    guild = ctx.guild
    currentTime = datetime.now(tz).strftime("%H-%M-%S")
    category = discord.utils.get(guild.categories, name="0001")

    if category is None:
        category = await guild.create_category("0001")

    overwrites = build_channel_overwrites(guild)

    channels_to_create = [
        "started",
        "process-0",
        "error-0",
        f"s-{currentTime}"
    ]

    for ch_name in channels_to_create:
        await category.create_text_channel(name=ch_name, overwrites=overwrites)

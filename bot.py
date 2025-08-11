import os
import logging
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN is not set. Create a .env with DISCORD_TOKEN=... or set it in your environment.")

logging.basicConfig(level=logging.INFO)

# Use minimal intents; message_content not required for slash commands
intents = discord.Intents.default()

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        logging.info(f"Synced {len(synced)} application command(s)")
    except Exception:
        logging.exception("Failed to sync application commands")
    print(f"✅ Bot is online as {bot.user} (ID: {bot.user.id})")


def _can_actor_manage_role(actor: discord.Member, target_role: discord.Role) -> bool:
    if not actor.guild_permissions.manage_roles:
        return False
    # Actor must have strictly higher top role than the target role
    return actor.top_role > target_role


async def _can_bot_manage_role(guild: discord.Guild, target_role: discord.Role, client: discord.Client) -> bool:
    bot_member = guild.me
    if bot_member is None and client.user is not None:
        try:
            bot_member = await guild.fetch_member(client.user.id)
        except discord.HTTPException:
            return False
    if bot_member is None:
        return False
    if not bot_member.guild_permissions.manage_roles:
        return False
    return bot_member.top_role > target_role


def _is_unmanageable_role(role: discord.Role) -> bool:
    # Managed roles (e.g., integrations) cannot be assigned/removed by bots
    return role.is_default() or role.managed


@bot.tree.command(name="assignrole", description="Give a role to a user")
@app_commands.describe(user="Member to give the role to", role="Role to assign")
@app_commands.checks.has_permissions(manage_roles=True)
async def assignrole(
    interaction: discord.Interaction,
    user: discord.Member,
    role: discord.Role,
):
    if interaction.guild is None:
        await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
        return

    if _is_unmanageable_role(role):
        await interaction.response.send_message(
            "That role cannot be managed (it may be @everyone or a managed/integration role).",
            ephemeral=True,
        )
        return

    if not _can_actor_manage_role(interaction.user, role):
        await interaction.response.send_message(
            "You can't manage that role due to permissions or role hierarchy.", ephemeral=True
        )
        return

    if not await _can_bot_manage_role(interaction.guild, role, interaction.client):
        await interaction.response.send_message(
            "I can't manage that role. Ensure I have Manage Roles and my top role is above the target role.",
            ephemeral=True,
        )
        return

    try:
        await user.add_roles(role, reason=f"Assigned by {interaction.user} via /assignrole")
        await interaction.response.send_message(
            f"✅ {user.mention} has been given the role `{role.name}`.",
            ephemeral=False,
        )
    except discord.Forbidden:
        await interaction.response.send_message(
            "Action forbidden. Check permissions and role hierarchy.", ephemeral=True
        )
    except discord.HTTPException as e:
        await interaction.response.send_message(
            f"Failed to assign role: {e}", ephemeral=True
        )


@bot.tree.command(name="removerole", description="Remove a role from a user")
@app_commands.describe(user="Member to remove the role from", role="Role to remove")
@app_commands.checks.has_permissions(manage_roles=True)
async def removerole(
    interaction: discord.Interaction,
    user: discord.Member,
    role: discord.Role,
):
    if interaction.guild is None:
        await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
        return

    if _is_unmanageable_role(role):
        await interaction.response.send_message(
            "That role cannot be managed (it may be @everyone or a managed/integration role).",
            ephemeral=True,
        )
        return

    if not _can_actor_manage_role(interaction.user, role):
        await interaction.response.send_message(
            "You can't manage that role due to permissions or role hierarchy.", ephemeral=True
        )
        return

    if not await _can_bot_manage_role(interaction.guild, role, interaction.client):
        await interaction.response.send_message(
            "I can't manage that role. Ensure I have Manage Roles and my top role is above the target role.",
            ephemeral=True,
        )
        return

    try:
        await user.remove_roles(role, reason=f"Removed by {interaction.user} via /removerole")
        await interaction.response.send_message(
            f"🗑️ Removed `{role.name}` from {user.mention}.",
            ephemeral=False,
        )
    except discord.Forbidden:
        await interaction.response.send_message(
            "Action forbidden. Check permissions and role hierarchy.", ephemeral=True
        )
    except discord.HTTPException as e:
        await interaction.response.send_message(
            f"Failed to remove role: {e}", ephemeral=True
        )


if __name__ == "__main__":
    bot.run(TOKEN)
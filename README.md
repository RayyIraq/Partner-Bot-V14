# Discord Role Manager Bot (Slash Commands)

Secure Discord bot that assigns and removes roles using slash commands. No message content intent required.

## URGENT: Rotate your leaked token
If you previously embedded your token in code or shared it, reset it now:
- Discord Developer Portal → Your App → Bot → Reset Token
- Update your environment with the new token

## Prerequisites
- Python 3.9+
- A Discord application with a bot user
- Invite the bot with scopes: `bot` and `applications.commands`
- Grant the bot permission: `Manage Roles`

## Setup
1. Copy `.env.example` to `.env` and set your token:
   ```
   DISCORD_TOKEN=your-token-here
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the bot:
   ```bash
   python bot.py
   ```

## Commands
- `/assignrole user:@User role:@Role` — Assigns a role to a member
- `/removerole user:@User role:@Role` — Removes a role from a member

Both commands enforce:
- Caller must have `Manage Roles`
- Bot must have `Manage Roles`
- Role hierarchy checks (both caller and bot must have a higher top role than the target role)
- Managed roles (integrations/@everyone) are not assignable

## Intents
This bot uses only default intents and does not require the Message Content intent. Server Members intent is not required for these slash commands because Discord provides resolved member data with interactions.

## Troubleshooting
- If commands don't appear: wait up to a minute after startup or re-invite with `applications.commands` scope. The bot syncs commands on ready.
- If you see hierarchy errors: move the bot's top role above the role you want it to manage.
- If you see forbidden errors: ensure the bot has the `Manage Roles` permission in the server and channel.

#!/usr/bin/env python3
import os
import sys
import yaml
import asyncio
import logging

import discord
from discord.utils import setup_logging, oauth_url
from discord.ext import commands, tasks
from discord.ext.commands import CommandNotFound

from modules import shared

import plugins.sync
import plugins.watch

BOT_PREFIX = '' # please configure this line before deploying
if not BOT_PREFIX:
  raise ValueError("Expected non-empty BOT_PREFIX!")

intents = discord.Intents.all()
bot = commands.Bot(
  BOT_PREFIX,
  help_command=None,
  intents=intents,
)

@bot.listen('on_c/file_change')
async def bot_update_config(file):
  global bot
  if file != 'config.yml':
    return
  print("Updating file configuration.")
  shared.load_config(file)
  bot.owner_ids = shared.config.settings.ownerIDs
  bot.dispatch('c/config_update')

...

async def main():
  async with bot:
    try:
      await setup(bot)
    except KeyboardInterrupt:
      pass
    finally:
      await teardown(bot)

def setup_logger():
  handler = logging.StreamHandler(stream=sys.stderr)
  setup_logging(handler=handler)

async def setup(bot):
  setup_logger()

  print("Appending modules...")
  await bot.add_cog(plugins.watch.File(bot, ['config.yml']))
  await bot.add_cog(plugins.sync.Feature(bot))
  ...
  print("Logging in...")
  await bot.start(
    shared.config.cred.token,
    reconnect=True,
  )

async def teardown(bot):
  pass

@bot.event
async def on_command_error(ctx, error):
  print(type(error).__name__, str(error))
  if isinstance(error, CommandNotFound):
    return
  raise error

if __name__ == '__main__':
  print(
    "Invite:",
    oauth_url(
      shared.config.cred.id,
      permissions=discord.Permissions(0),
    )
  )

  asyncio.run(main())

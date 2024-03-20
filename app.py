#!/usr/bin/env python3
import os
import sys
import yaml
import asyncio
import logging
import argparse

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

async def setup_sync():
  async with bot:
    bot._connection.application_id = shared.config.cred.id
    await bot.http.static_login(shared.config.cred.token)
    await bot.tree.sync(guild=None)
    for serverID in bot.tree._guild_commands.keys():
      await bot.tree.sync(guild=serverID)

@bot.event
async def on_command_error(ctx, error):
  print(type(error).__name__, str(error))
  if isinstance(error, CommandNotFound):
    return
  raise error

def mode_normal():
  print(
    "Invite:",
    oauth_url(
      shared.config.cred.id,
      permissions=discord.Permissions(0),
    )
  )

  asyncio.run(main())

def mode_quick_sync():
  print('syncing commands...')
  asyncio.run(setup_sync())

def mode_selection():
  result   = argparse.Namespace(
    callback=mode_normal,
  )
  parser   = argparse.ArgumentParser()
  parser.add_argument(
    '--sync', action='store_const', const=mode_quick_sync, dest='callback',
    help='updates bot slash command and exit',
  )
  parser.parse_args(namespace=result)
  result.callback()

if __name__ == '__main__':
  mode_selection()

from inspect import iscoroutinefunction as callableasync
from modules import shared

async def is_owner(ctx):
  return ctx.author.id in shared.config.users

async def call_function(fun, *args, **kwargs):
  if callableasync(fun):
    await fun(*args, **kwargs)
  elif callable(fun):
    fun(*args, **kwargs)

is_manager = is_owner

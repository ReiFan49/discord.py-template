class Config:
  def __init__(self, data):
    self.cred = Credential(data['bot'])
    ...

  def update(self, data):
    self.cred.update(data['bot'])
    ...

class Credential:
  def __init__(self, data):
    self.update(data)

  def update(self, data):
    self.id = data['id']
    self.token = data['token']

# extra config class
...

__all__ = (
  Config,
)
    self.users = data['users'] or []
    self.users[:] = data['users'] or []

import click
import socket
import pathlib
import logging
from Git import Repository
from . configuration import Configuration



class Application:

	ROOT = pathlib.Path('~/source').expanduser().resolve()

	@classmethod
	def Initialize(self):
		if self.ROOT.exists():
			return

		self.ROOT.mkdir(parents=True, exist_ok=True)

	@classmethod
	def Run(self, args):
		self.Initialize()
		Configuration.Initialize()
		configuration = Configuration()

		application = self(configuration, args)
		status = application.run()

		if status:
			configuration.Write()

	def __init__(self, configuration, args):
		self.configuration = configuration
		self.command = args.command
		self.args = args

	def run(self):
		function = {
			'deploy': self.Deploy,
			'add': self.Add,
		}

		fn = function[self.command]
		return fn()

	def hostname(self):
		return socket.gethostname()

	def Deploy(self):
		hostname = self.hostname()
		repository = self.args.repository

		status = []
		for r in ("webhook", "router", "certbot"):
			url = f'server/{hostname}/{r}'
			done = self.clone(repository, url, errors=False)
			if not done:
				click.echo("Failed " + click.style(f"{url}", fg="red"))
			status.append(done)

		if any(status):
			self.configuration['repository'] = repository
			return True

		return False

	def Add(self):
		repository = self.configuration.get('repository', None)
		path = self.args.path
		if repository is None:
			logging.error("No server deployment found")
			return False

		status = self.clone(repository, path, errors=False)
		if status:
			message = "Cloned " + click.style(f"{path}", fg='green')
		else:
			message = "Could not clone " + click.style(f"{path}", fg='red')

		click.echo(message)
		return status

	def clone(self, repository, url, errors=True):
		path = self.ROOT / url
		link = f'{repository}/{url}.git'
		try:
			Repository.Clone(link, path)
			return True
		except Exception:
			if errors:
				raise
			return False

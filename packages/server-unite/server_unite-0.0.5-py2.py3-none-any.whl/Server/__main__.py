import argparse

from . application import Application



def parse_args():
	parser = argparse.ArgumentParser(prog="Server", description="Manage server deployment")
	subparsers = parser.add_subparsers(dest="command")

	deploy_parser = subparsers.add_parser("deploy", help="Deploy a new server")
	deploy_parser.add_argument('repository', help="Repository URL")

	add_parser = subparsers.add_parser("add", help="Add a repository")
	add_parser.add_argument('path', help="Relative path to repository")

	args = parser.parse_args()
	if args.command is None:
		parser.print_help()
		return

	return args



def main():
	args = parse_args()
	if args is None:
		return

	Application.Run(args)

if __name__ == '__main__':
	main()

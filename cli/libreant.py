import click
from webant.webant import main

from cli import libreant_cli_common


@click.command(help="launch libreant daemon")
@libreant_cli_common(additional_options=[
    '--port', '--address', '--fsdb-path', '--es-indexname', '--es-hosts',
    '--users-db', '--preset-paths', '--agherant-descriptions'])
def libreant(conf, **kwargs):
    try:
        main(conf)
    except Exception as e:
        if conf.get('DEBUG', False):
            raise
        else:
            click.secho(str(e), fg='yellow', err=True)

if __name__ == '__main__':
    libreant()

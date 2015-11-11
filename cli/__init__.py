import click
import logging
import json

from conf import config_utils
from conf.defaults import get_def_conf, get_help
from utils.loggers import initLoggers
from custom_types import StringList


def libreant_cli_common():
    decorators = [
        click.version_option(),
        click.option('-s', '--settings', type=click.Path(exists=True, readable=True), metavar="<path>", help='file from wich load settings'),
        click.option('-d', '--debug', is_flag=True, help=get_help('DEBUG')),
        click.option('-p', '--port', type=click.IntRange(min=1, max=65535), metavar="<port>", help=get_help('PORT')),
        click.option('--address', type=click.STRING, metavar="<address>", help=get_help('ADDRESS')),
        click.option('--fsdb-path', type=click.Path(), metavar="<path>", help=get_help('FSDB_PATH')),
        click.option('--es-indexname', type=click.STRING, metavar="<name>", help=get_help('ES_INDEXNAME')),
        click.option('--es-hosts', type=StringList(), metavar="<host>..", help=get_help('ES_HOSTS')),
        click.option('--users-db', type=click.Path(), metavar="<url>", help=get_help('USERS_DATABASE') ),
        click.option('--preset-paths', type=StringList(), metavar="<path>..", help=get_help('PRESET_PATHS')),
        click.option('--agherant-descriptions', type=StringList(), metavar="<url>..", help=get_help('AGHERANT_DESCRIPTIONS')),
        click.option('--dump-settings', is_flag=True, help='dump current settings and exit'),
        commonthings
    ]

    def deco(f):
        for dec in reversed(decorators):
            f = dec(f)
        return f
    return deco


def commonthings(f):
    def settamolto(**kwargs):  # settings, debug, port, address, fsdb_path, es_indexname, es_hosts, users_db, preset_paths, agherant_descriptions, dump_settings):
        initLoggers(logNames=['config_utils'])
        conf = config_utils.load_configs('LIBREANT_', defaults=get_def_conf(), path=kwargs['settings'])
        cliConf = {}
        if kwargs['debug']:
            cliConf['DEBUG'] = True
        if kwargs['port']:
            cliConf['PORT'] = kwargs['port']
        if kwargs['address']:
            cliConf['ADDRESS'] = kwargs['address']
        if kwargs['fsdb_path']:
            cliConf['FSDB_PATH'] = kwargs['fsdb_path']
        if kwargs['es_indexname']:
            cliConf['ES_INDEXNAME'] = kwargs['es_indexname']
        if kwargs['es_hosts']:
            cliConf['ES_HOSTS'] = kwargs['es_hosts']
        if kwargs['users_db']:
            cliConf['USERS_DATABASE'] = kwargs['users_db']
        if kwargs['preset_paths']:
            cliConf['PRESET_PATHS'] = kwargs['preset_paths']
        if kwargs['agherant_descriptions']:
            cliConf['AGHERANT_DESCRIPTIONS'] = kwargs['agherant_descriptions']
        conf.update(cliConf)

        if kwargs['dump_settings']:
            click.echo(json.dumps(conf, indent=3))
            exit(0)

        initLoggers(logging.DEBUG if conf.get('DEBUG', False) else logging.WARNING)
        f(conf=conf, **kwargs)
    return settamolto

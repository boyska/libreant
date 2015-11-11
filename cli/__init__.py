import click
import logging
import json

from conf import config_utils
from conf.defaults import get_def_conf, get_help
from utils.loggers import initLoggers
from custom_types import StringList


def libreant_cli_common(additional_options=[]):
    available = {
        '--port': click.option('-p', '--port', type=click.IntRange(min=1, max=65535), metavar="<port>", help=get_help('PORT')),
        '--address': click.option('--address', type=click.STRING, metavar="<address>", help=get_help('ADDRESS')),
        '--fsdb-path': click.option('--fsdb-path', type=click.Path(), metavar="<path>", help=get_help('FSDB_PATH')),
        '--es-indexname': click.option('--es-indexname', type=click.STRING, metavar="<name>", help=get_help('ES_INDEXNAME')),
        '--es-hosts': click.option('--es-hosts', type=StringList(), metavar="<host>..", help=get_help('ES_HOSTS')),
        '--users-db': click.option('--users-db', type=click.Path(), metavar="<url>", help=get_help('USERS_DATABASE') ),
        '--preset-paths': click.option('--preset-paths', type=StringList(), metavar="<path>..", help=get_help('PRESET_PATHS')),
        '--agherant-descriptions': click.option('--agherant-descriptions', type=StringList(), metavar="<url>..", help=get_help('AGHERANT_DESCRIPTIONS')),
    }
    decorators = [
        click.version_option(),
        click.option('-s', '--settings', type=click.Path(exists=True, readable=True), metavar="<path>", help='file from wich load settings'),
        click.option('-d', '--debug', is_flag=True, help=get_help('DEBUG')),
        click.option('--dump-settings', is_flag=True, help='dump current settings and exit'),
    ]
    for opt in additional_options:
        if opt not in available:
            raise ValueError('Unsupported option %s' % opt)
        decorators.append(available[opt])
    decorators.append(commonthings)

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
        if 'debug' in kwargs and kwargs['debug']:
            cliConf['DEBUG'] = True
        if 'port' in kwargs and kwargs['port']:
            cliConf['PORT'] = kwargs['port']
        if 'address' in kwargs and kwargs['address']:
            cliConf['ADDRESS'] = kwargs['address']
        if 'fsdb_path' in kwargs and kwargs['fsdb_path']:
            cliConf['FSDB_PATH'] = kwargs['fsdb_path']
        if 'es_indexname' in kwargs and kwargs['es_indexname']:
            cliConf['ES_INDEXNAME'] = kwargs['es_indexname']
        if 'es_hosts' in kwargs and kwargs['es_hosts']:
            cliConf['ES_HOSTS'] = kwargs['es_hosts']
        if 'users_db' in kwargs and kwargs['users_db']:
            cliConf['USERS_DATABASE'] = kwargs['users_db']
        if 'preset_paths' in kwargs and kwargs['preset_paths']:
            cliConf['PRESET_PATHS'] = kwargs['preset_paths']
        if 'agherant_descriptions' in kwargs and kwargs['agherant_descriptions']:
            cliConf['AGHERANT_DESCRIPTIONS'] = kwargs['agherant_descriptions']
        conf.update(cliConf)

        if kwargs['dump_settings']:
            click.echo(json.dumps(conf, indent=3))
            exit(0)

        initLoggers(logging.DEBUG if conf.get('DEBUG', False) else logging.WARNING)
        f(conf=conf, **kwargs)
    return settamolto

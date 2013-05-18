import mangler

config = {
        'log_level': 'DEBUG',
        'twanager.tracebacks': True,
        'server_store': ['tiddlywebplugins.sqlalchemy3', {
            'db_config': 'sqlite:///test.db'}],
        'system_plugins': ['tiddlywebwiki'],
        'collections.use_memory': True,
}

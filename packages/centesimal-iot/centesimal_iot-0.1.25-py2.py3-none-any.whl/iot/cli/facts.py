import re
import os
import yaml

from asyncio import run
from datetime import datetime

import click

from glom import glom

from pycelium.shell import Reactor, DefaultExecutor
from pycelium.pastor import Pastor
from pycelium.scanner import Settler

from pycelium.tools import parse_uri, build_uri
from pycelium.tools.cli.main import main, CONTEXT_SETTINGS
from pycelium.tools.cli.config import config, banner
from pycelium.tools.mixer import merge_yaml
from pycelium.tools.persistence import find_files


@main.group(context_settings=CONTEXT_SETTINGS)
@click.pass_obj
def facts(env):
    # banner("User", env.__dict__)
    pass


@facts.command()
@click.option("--uri", default="localhost")
@click.pass_obj
def get(env, uri):
    config.callback()
    ctx = parse_uri(uri)

    host = ctx['host']

    banner(f"Facts from '{host}'")

    reactor = Reactor()
    conn = DefaultExecutor(**ctx)
    reactor.attach(conn)

    stm = Settler()
    reactor.attach(stm)

    run(reactor.main())

    reactor.save("iot.yaml")

    foo = 1

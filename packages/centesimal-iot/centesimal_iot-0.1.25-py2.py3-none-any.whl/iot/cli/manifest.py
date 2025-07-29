import re
import os

import yaml

# import ruamel.yaml as yaml

from datetime import datetime
from glom import glom, assign

import click

from pycelium.tools import parse_uri, build_uri
from pycelium.tools.cli.main import main, CONTEXT_SETTINGS
from pycelium.tools.cli.config import config, banner

from pycelium.tools.mixer import merge_yaml
from pycelium.tools.persistence import find_files
from pycelium.tools.templating import decode_dict_new_lines

from pycelium.shell import search, bspec


@main.group(context_settings=CONTEXT_SETTINGS)
@click.pass_obj
def manifest(env):
    # banner("User", env.__dict__)
    pass


@manifest.command()
# @click.argument('filename', default='sample.gan')
@click.option("--email", default=None)
@click.option("--cost", default=30)
@click.pass_obj
def new(env, email, cost=0):
    config.callback()

    found = find_files(
        **env.__dict__,
    )
    banner("Found", found)

    banner(f"Loading users from {len(found)} projects")
    # root = consolidate(found, output=click.echo)

    ## update loaded resource with 'master' db
    # resources = glom(root.ROOT, 'resource')
    # mgr = ResourceManager(env)
    # mgr.update(resources)
    # mgr.save(resources)

    foo = 1


@manifest.command()
@click.option("--host", default="localhost")
@click.pass_obj
def list(env, host):
    config.callback()

    import iot

    ctx = {
        "host": host,
    }

    folders = [
        os.path.dirname(iot.__file__),
        ".",
    ]
    # folders = list(iot.__path__) + ["."]
    sort_pattern = [
        "((?P<parent>[^/]+)/)?(?P<basename>[^/]+)$",
    ]
    includes = [".*specs.*.yaml"]

    found = find_files(
        folders,
        includes=includes,
        sort_by="keys",
        sort_pattern=sort_pattern,
        **ctx,
    )
    banner("Found", found)

    foo = 1


@manifest.command()
@click.option("--uri", default="localhost")
@click.pass_obj
def merge(env, uri):
    config.callback()
    ctx = parse_uri(uri)
    # ctx = {
    # "uri": uri,
    # }

    import iot

    folders = [
        os.path.dirname(iot.__file__),
        ".",
    ]
    sort_pattern = [
        "((?P<parent>[^/]+)/)?(?P<basename>[^/]+)$",
    ]
    includes = [".*specs.*.yaml"]

    result = merge_yaml(
        folders, includes=includes, sort_pattern=sort_pattern, **ctx
    )
    # output = yaml.dump(result)
    # print(output)

    yaml.dump(result, open("iot.yaml", "w"))

    # check
    decode_dict_new_lines(result)

    # blueprint = {
    #'.*(content|text)': r".*\\n.*",
    # }

    # modify = search(result, blueprint, flat=True)
    # for key, value in modify.items():
    # value = value.replace("\\n", "\n")
    # spec = bspec(key)
    # assign(result, spec, value)

    # foo = 1

    kk = yaml.load(open("iot.yaml"), Loader=yaml.Loader)
    raw = result["venoen243"]["var"]["fs"]["/etc/wireguard/wg0.conf"][
        "content"
    ]
    # raw = raw.replace("\\n", "\n")

    print("." * 80)
    print(raw)

    foo = 1


@manifest.command()
@click.option("--uri", default="localhost")
@click.pass_obj
def test(env, uri):
    config.callback()
    ctx = parse_uri(uri)
    # ctx = {
    # "uri": uri,
    # }

    result = yaml.load(open("iot.yaml"), Loader=yaml.Loader)

    # check

    blueprint = {
        ".*(content|text)": r".*\\n.*",
    }

    modify = search(result, blueprint, flat=True)
    for key, value in modify.items():
        banner(key)
        print(value)

    # now decode
    decode_dict_new_lines(result)

    banner("YAML")
    output = yaml.dump(result)  # , default_style="|")
    print(output)

    foo = 1

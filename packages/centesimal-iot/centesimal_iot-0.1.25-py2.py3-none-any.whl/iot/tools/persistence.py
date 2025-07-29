assert False

import os
import re
import yaml
import pickle
import lzma as xz

from datetime import datetime

from glom import glom


# ------------------------------------------------
# DB dumpers
# ------------------------------------------------


# def save(data):
# if isinstance(data, Zingleton):
# data = data._instances_()

## TODO: xz
# output = yaml.dump(
# data,
# Dumper=yaml.Dumper,
# default_flow_style=False,
# )
# with open('/tmp/output.yaml', 'w') as f:
# f.write(output)
# with xz.open('/tmp/output.yaml.xz', 'wb') as f:
# f.write(output.encode('utf-8'))

# output = pickle.dumps(
# data,
# protocol=-1,
# )
# with open('/tmp/output.pickle', 'wb') as f:
# f.write(output)
# with xz.open('/tmp/output.pickle.xz', 'wb') as f:
# f.write(output)


def load():
    # data = yaml.load(
    # open('/tmp/output.yaml', 'rb'),
    # Loader=yaml.Loader,
    # )
    data = pickle.load(
        xz.open('/tmp/output.pickle.xz', 'rb'),
    )
    # provide _uid fiels for most collections
    for kind in 'project', 'task', 'resource':
        collection = glom(data, f"{kind}", default=None)
        if collection:
            for uid, item in collection.items():
                item._uid = uid
    return data


# ------------------------------------------------
#  Persistence
# ------------------------------------------------
class iPersistent:
    def __init__(self, **kw):
        foo = 1

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state):
        self.__dict__.update(state)


class iLoader:
    @classmethod
    def load(cls, folders, includes=[], excludes=[]):
        for path in find_files(
            folders, includes=includes, excludes=excludes
        ):
            data = yaml.load(open(path, 'r'), Loader=yaml.Loader)
            yield path, data


# ------------------------------------------------
# locate files
# ------------------------------------------------


def find_files(
    folders,
    includes=[],
    excludes=[],
    sort_by='value',
    sort_reverse=False,
    **kw,
):
    found = {}
    if isinstance(folders, str):
        folders = [folders]
    if isinstance(includes, str):
        includes = [includes]
    if isinstance(excludes, str):
        excludes = [excludes]

    for top in folders:
        top = os.path.expandvars(top)
        top = os.path.expanduser(top)
        top = os.path.abspath(top)
        for root, folders, files in os.walk(top):
            for file in files:
                path = os.path.join(root, file)

                ok = False
                for pattern in includes:
                    if re.search(pattern, path, flags=re.I | re.DOTALL):
                        ok = True
                        break
                if ok:
                    for pattern in excludes:
                        if re.search(pattern, path, flags=re.I | re.DOTALL):
                            ok = False
                            break
                if ok:
                    ts = os.stat(path, follow_symlinks=True).st_mtime
                    ts = datetime.utcfromtimestamp(ts).strftime(
                        '%Y-%m-%d %H:%M:%S'
                    )
                    found[path] = ts

    # banner("Found", found, 'st_mtime')
    idx, rev = (
        (0, False) if sort_by.lower().startswith('keys') else (1, True)
    )
    found = dict(
        sorted(
            found.items(),
            key=lambda item: item[idx],
            reverse=rev,
        )
    )
    return found

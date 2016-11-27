import toml
import sys

config = open("config.toml", 'r')
config2 = config.read()
config.close()
try:
    config = toml.loads(config2)
except toml.TomlDecodeError:
    print("Invalidly formatted TOML config, quiting")
    sys.exit(4)
del config2

get = config.get

find * |& grep __pycache__ | rm -rfv $(cat -)
rm db.*
rm error.html
rm config.toml
echo "mode='i2p'" > config.toml

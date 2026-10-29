#!/bin/sh
# Install commands for the current user; never change shell startup files.
set -eu

if [ "${1:-}" = --help ]; then
    cat <<'EOF'
Usage: ./install.sh
Copies the helpers to ~/bin/tifr and links commands into ~/.local/bin.
Override with TIFR_INSTALL_DIR and TIFR_COMMAND_DIR (absolute paths).
Run again after updating the checkout to install the new version.
EOF
    exit 0
fi
if [ "$#" -ne 0 ]; then
    echo 'Usage: ./install.sh [--help]' >&2
    exit 2
fi

source_dir=$(CDPATH= cd -- "$(dirname -- "$(readlink -f -- "$0")")" && pwd)
install_dir=${TIFR_INSTALL_DIR:-"$HOME/bin/tifr"}
command_dir=${TIFR_COMMAND_DIR:-"$HOME/.local/bin"}
for directory in "$install_dir" "$command_dir"; do
    case "$directory" in
        /*) ;;
        *) echo 'Installation directories must be absolute paths.' >&2; exit 2 ;;
    esac
done
if [ "$install_dir" = "$command_dir" ]; then
    echo 'Use separate helper and command directories.' >&2
    exit 2
fi

# Check all command names before copying anything. Existing links from a previous
# installation can be updated; unrelated commands are left alone.
for command in tifrvpn tifr-otp tifr-import-totp; do
    target=$command
    [ "$command" != tifr-otp ] || target=tifr-otp.py
    destination=$command_dir/$command
    if [ -e "$destination" ] || [ -L "$destination" ]; then
        if [ ! -L "$destination" ] || [ "$(readlink -- "$destination")" != "$install_dir/$target" ]; then
            echo "Command already exists: $destination. Choose another TIFR_COMMAND_DIR." >&2
            exit 1
        fi
    fi
done

mkdir -p -- "$install_dir" "$command_dir"
for file in tifrvpn tifr-vpn-auth.py tifr-otp.py tifr-import-totp tifr-import-totp.py; do
    if [ "$(readlink -f -- "$source_dir/$file")" != "$(readlink -f -- "$install_dir/$file")" ]; then
        install -m 755 -- "$source_dir/$file" "$install_dir/$file"
    fi
done
ln -sfn -- "$install_dir/tifrvpn" "$command_dir/tifrvpn"
ln -sfn -- "$install_dir/tifr-otp.py" "$command_dir/tifr-otp"
ln -sfn -- "$install_dir/tifr-import-totp" "$command_dir/tifr-import-totp"
printf 'Installed helpers: %s\nCommands: %s\n' "$install_dir" "$command_dir"
printf 'Ensure the command directory is on PATH, then follow README.md to set up credentials.\n'

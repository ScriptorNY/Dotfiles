#!/bin/zsh

USERNAME="bigfoot"

install_yay() {
	local cwd=$PWD

	git clone https://aur.archlinux.org/yay.git /tmp/yay
	cd /tmp/yay
	makepkg -si
	rm -rf /tmp/yay

	cd "$cwd"
}

configure_mirrors() {
	yay -Sy --cleanafter --nodiffmenu --noconfirm reflector

	sudo reflector --latest 20 --country France --protocol https --sort rate --save /etc/pacman.d/mirrorlist
}

source_zshrc() {
	su - $USERNAME -c "mkdir -p ~/.antigen"
	su - $USERNAME -c "curl -L git.io/antigen > ~/.antigen/antigen.zsh"
	su - $USERNAME -c "source ~/.zshrc"
}

install() {
	local script_path=$0:A
	local idx=0
	local package=$(cat "$script_path"/../dependencies.json | jq -r '.dependencies['"$idx"']')

	install_yay
	configure_mirrors
	source_zshrc

	while [[ ! "$package" = "null" ]]; do
		yay -Sy --cleanafter --nodiffmenu --noconfirm "$package"

		((idx++))
		package=$(cat "$script_path"/../dependencies.json | jq -r '.dependencies['"$idx"']')
	done
}

unfunction install_yay
unfunction configure_mirrors
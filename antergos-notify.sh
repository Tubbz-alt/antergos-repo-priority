#!/bin/bash
# -*- coding: utf-8 -*-
#
#  antergos-notify.sh
#
#  Copyright © 2016 Antergos
#
#  antergos-notify is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  antergos-notify is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with antergos-notify; if not, see <http://www.gnu.org/licenses/>.

export TEXTDOMAIN="ANTERGOS_NOTIFY"
export GETTEXT='gettext "ANTERGOS_NOTIFY"'

# Translatable Strings

# Notification Body Part 1
_part1=$(${GETTEXT} 'The antergos repo priority has been updated. You should review the change in')

# Notification Body Part 2
_part2=$(${GETTEXT} "/etc/pacman.conf.pacnew and then update your pacman.conf accordingly.\"")

_msg="${_part1} ${_part2}"

# Notification Subject
_subject=$(${GETTEXT} '"ATTENTION: Antergos System Message"')


maybe_display_desktop_alert() {
	if [[ -e '/usr/bin/pacman-boot' ]]; then
		return
	fi

	_icon='/usr/share/antergos/logo-square32.png'
	_command="/usr/bin/notify-send -u critical -a Antergos -i ${_icon} ${_subject} ${_msg}"
	_addr='DBUS_SESSION_BUS_ADDRESS'
	
	_processes=($(ps aux | grep '[d]bus-daemon --session' | awk '{print $2}' | xargs))
	_users=($(ps aux | grep '[d]bus-daemon --session' | awk '{print $1}' | xargs))

	for _i in $(seq 1 ${#_processes[@]}); do
		_pid="${_processes[(_i - 1)]}"
		_user="${_users[(_i - 1)]}"
		_dbus="$(grep -z ${_addr} /proc/$_pid/environ | sed -e s/${_addr}=//)"

		[[ -z "${_dbus}" ]] && continue

		echo "${_command}" > /dev/null
		echo "${_user}" > /dev/null

		DBUS_SESSION_BUS_ADDRESS="${_dbus}" DISPLAY=":0" su "${_user}" -c "${_command}"
	done
}

maybe_display_desktop_alert

exit 0

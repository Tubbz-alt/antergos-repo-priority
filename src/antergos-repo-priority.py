#!/bin/python
# -*- coding: utf-8 -*-
#
# antergos-repo-priority.py
#
# Copyright © 2016 Antergos
#
# antergos-repo-priority.py is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# antergos-repo-priority.py is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with antergos-repo-priority.py; if not, see <http://www.gnu.org/licenses/>.

import re
import os
import sys
import subprocess
import gettext
import locale
from termcolor import colored, cprint

APP_NAME = 'ANTERGOS_NOTIFY'
LOCALE_DIR = '/usr/share/locale'


def setup_gettext():
    gettext.textdomain(APP_NAME)
    gettext.bindtextdomain(APP_NAME, LOCALE_DIR)

    try:
        locale_code, encoding = locale.getdefaultlocale()
        lang = gettext.translation(APP_NAME, LOCALE_DIR, [locale_code], None, True)
        lang.install()
    except Exception:
        print('Translations setup failed. Using source strings (English).')


class AntergosRepoPriority:

    pmconf = '/etc/pacman.conf'
    pmconf_new = '/etc/pacman.conf.pacnew'
    pmconf_contents = []

    def get_pacman_config_contents(self) -> list:
        if not self.pmconf_contents:
            with open(self.pmconf, 'r') as pacman_config:
                self.pmconf_contents.extend(pacman_config.readlines())

        return self.pmconf_contents

    def has_antergos_repo(self) -> bool:
        return '[antergos]' in self.get_pacman_config_contents()

    def has_antergos_repo_before_arch_repos(self) -> bool:
        seen_antergos = False

        for line in self.get_pacman_config_contents():
            if re.search(r'^\s*\[antergos\]', line):
                seen_antergos = True
                break
            if re.search(r'^\s*\[core\]', line):
                break

        return seen_antergos

    def get_antergos_repo_lines(self) -> list:
        lines = []
        entered_antergos = False

        for line in self.get_pacman_config_contents():
            if entered_antergos and re.match(r'^[\s#]*\[\w', line):
                break
            elif entered_antergos:
                lines.append(line)
                continue
            elif re.match(r'^\s*\[antergos\]', line):
                lines.append(line)
                entered_antergos = True

        return lines

    def maybe_rename_existing_pacnew(self) -> None:
        if os.path.exists(self.pmconf_new):
            os.rename(self.pmconf_new, f'{self.pmconf_new}.old')

    def change_antergos_repo_priority(self) -> None:
        antergos_repo_lines = self.get_antergos_repo_lines()
        new_contents = []
        done = False

        for line in self.get_pacman_config_contents():
            if not done and re.match(r'^\s*\[core\]', line):
                new_contents.extend(antergos_repo_lines)
                new_contents.append(r'\n')
                done = True

            if line not in antergos_repo_lines:
                new_contents.append(line)

        with open(self.pmconf_new, 'w') as new_pacman_config:
            new_pacman_config.write(''.join(new_contents))

    def print_notice_to_stdout(self) -> None:
        prefix = colored('*', color='red', attrs=['bold', 'blink'])
        subject = _('"ATTENTION: Antergos System Message"')
        # I cant remember why the quotes are needed in the above call to gettext :-/
        subject = subject.replace('"', '')
        part1 = _('The antergos repo priority has been updated.')
        part2 = _('You should review the change in /etc/pacman.conf.pacnew')
        part3 = _('and then update your pacman.conf accordingly.')
        part4 = _('For more information see:')

        cprint(
            f'    =======>>> {subject} <<<=======    ',
            color='white',
            on_color='on_red',
            attrs=['bold', 'blink']
        )
        print('')
        print(f'{prefix} {part1}')
        print(f'{prefix} {part2}')
        print(f'{prefix} {part3}')
        print('')
        print(f'{prefix} {part4}')
        print(f'{prefix} https://antergos.com/wiki/antergos-repo-priority')
        print('')
        cprint(
            '                                                                 ',
            color='white',
            on_color='on_red',
            attrs=['bold', 'blink']
        )


if __name__ == '__main__':
    setup_gettext()

    repo_priority = AntergosRepoPriority()
    doing_install = os.environ.get('CNCHI_RUNNING', False)
    is_graphical_session = os.environ.get('DISPLAY', False)

    if not repo_priority.has_antergos_repo():
        sys.exit(0)

    if not repo_priority.has_antergos_repo_before_arch_repos():
        print('Changing antergos repo priority in pacman.conf.pacnew...')

        repo_priority.maybe_rename_existing_pacnew()
        repo_priority.change_antergos_repo_priority()
        repo_priority.print_notice_to_stdout()

        with open(repo_priority.pmconf) as old_conf, open(repo_priority.pmconf_new) as new_conf:
            if old_conf.read() == new_conf.read():
                sys.exit(0)

        if is_graphical_session and not doing_install:
            # Display desktop notification.
            try:
                subprocess.check_call(['/usr/bin/antergos-notify.sh'])
            except subprocess.CalledProcessError:
                pass

    sys.exit(0)

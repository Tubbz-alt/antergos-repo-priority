#!/bin/python
# -*- coding: utf-8 -*-
#
#  antergos-repo-priority.py
#
#  Copyright © 2016 Antergos
#
#  antergos-repo-priority.py is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  antergos-repo-priority.py is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with antergos-repo-priority.py; if not, see <http://www.gnu.org/licenses/>.

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

    def get_pacman_config_contents(self):
        if not self.pmconf_contents:
            with open(self.pmconf, 'r') as pacman_config:
                self.pmconf_contents.extend(pacman_config.readlines())

        return self.pmconf_contents

    def has_antergos_repo()
        return '[antergos]' in self.get_pacman_config_contents()

    def antergos_repo_before_arch_repos(self):
        seen_antergos = False
        
        for line in self.get_pacman_config_contents():
            if re.search(r'^\[antergos\]', line):
                seen_antergos = True
            if re.search(r'^\[core\]', line):
                break

        return seen_antergos

    def get_antergos_repo_lines(self):
        lines = []
        entered_antergos = False

        for line in self.get_pacman_config_contents():
            if entered_antergos and re.match(r'^(\[\w)|(#\[\w)', line):
                break
            elif entered_antergos:
                lines.append(line)
                continue
            elif re.match(r'^\[antergos\]', line):
                lines.append(line)
                entered_antergos = True

        return lines

    def maybe_rename_existing_pacnew(self):
        if os.path.exists(self.pmconf_new):
            os.rename(self.pmconf_new, '{}.old'.format(self.pmconf_new))

    def change_antergos_repo_priority(self):
        antergos_repo_lines = self.get_antergos_repo_lines()
        new_contents = []

        for line in self.get_pacman_config_contents():
            if re.match(r'^\[core\]', line):
                new_contents.extend(antergos_repo_lines)
                new_contents.append('')

            if line not in antergos_repo_lines:
                new_contents.append(line)
             
        with open(self.pmconf_new, 'w') as new_pacman_config:
            new_pacman_config.write(''.join(new_contents))

    def print_notice_to_stdout(self):
        prefix = colored('*', color='red', attrs=['bold', 'blink'])
        subject = _('"ATTENTION: Antergos System Message"')
        part1 = _('The antergos repo priority has been updated.')
        part2 = _('You should review the change in /etc/pacman.conf.pacnew')
        part3 = _('and then update your pacman.conf accordingly.')
        part4 = _('For more information see:')

        cprint(
            '    =======>>> {} <<<=======    '.format(subject.replace('"', '')),
            color='white',
            on_color='on_red',
            attrs=['bold', 'blink']
        )
        print('')
        print('{0} {1}'.format(prefix, part1))
        print('{0} {1}'.format(prefix, part2))
        print('{0} {1}'.format(prefix, part3))
        print('')
        print('{0} {1}'.format(prefix, part4))
        print('{} https://antergos.com/wiki/antergos-repo-priority'.format(prefix))
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

    if not repo_priority.has_antergos_repo():
        sys.exit(0)

    if not repo_priority.antergos_repo_before_arch_repos():
        print('Changing antergos repo priority in pacman.conf.pacnew...')
        repo_priority.maybe_rename_existing_pacnew()
        repo_priority.change_antergos_repo_priority()
        repo_priority.print_notice_to_stdout()

        if len(sys.argv) > 1 and 'True' == sys.argv[1] and not doing_install:
            # We were called by pacman INSTALL scriptlet.
            sys.exit(1)
        elif not doing_install:
            # We were called by ALPM hook. Display desktop notification.
            try:
                subprocess.check_call(['/usr/bin/antergos-notify.sh'])
            except subprocess.CalledProcessError:
                pass

    sys.exit(0)

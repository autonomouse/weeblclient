#!/usr/bin/env python

import pdb
import pycurl
import os
import re
import shutil
import subprocess
import sys

from glob import glob
from optparse import OptionParser

from arsenal.application import LaunchpadApplication
from lpltk.attachments import *
from lpltk.bug import Bug

class BugPatcher(LaunchpadApplication):
    flagnames = ('DEBUG',)

    modifiers = ()

    def run(self):
        bug = Bug(self.launchpad.service.launchpad, self.launchpad.bugid)

        targets = []
        for bugtask in bug.lpbug.bug_tasks:
            target = re.findall(r'^.*/(.*?)$', bugtask.target.self_link)[0]
            targets.append(target)

        for target in set(targets):
            answer = raw_input('Patch %s [Y/n]: ' % target)
            if answer and answer[0].lower() != 'y':
                continue
            self.patch_target_for_bug(target, bug)

    def patch_target_for_bug(self, target, bug):
        print 'Patching %s for bug: "%s"' % (target, bug.title)

        print 'Downloading source package'
        command = ['apt-get', '-y', 'source', target]
        child = self.create_child(command)
        child.wait()
        if child.returncode != 0:
            return False

        print 'Installing build dependencies'
        command = ['sudo', 'apt-get', '-y', 'build-dep', target]
        child = self.create_child(command)
        child.wait()
        if child.returncode != 0:
            return False

        sourcedir = None
        for entry in glob('%s/%s*' % (self.tmpdir, target)):
            if os.path.isdir(entry):
                sourcedir = entry
        if not sourcedir:
            return False

        command = ['what-patch',]
        child = self.create_child(command, cwd=sourcedir, pipe=True)
        child.wait()
        out, err = child.communicate()
        patchsys = out.strip()
        print 'Patch system detected:', patchsys

        handler = getattr(self, 'handle_%s' % patchsys, None)
        if not handler:
            return False

        attachments = Attachments(bug)
        attachments.add_filter(filter_is_patch, True)
        attachments.download_in_dir(self.tmpdir)

        for attachment in attachments:
            answer = raw_input('Apply %s [Y/n]: ' % attachment.title)
            if answer and answer[0].lower() != 'y':
                continue
            succeeded = handler(sourcedir, attachment)
            if not succeeded:
                print 'Could not apply %s' % attachment.title
                return False

    def move_patch_to_debian(self, sourcedir, attachment):
        oldpath = os.path.join(self.tmpdir, attachment.title)
        newpath = os.path.join(sourcedir,
                               'debian/patches/%s' % attachment.title)
        shutil.move(oldpath, newpath)

    def try_dpkg_buildpackage(self, sourcedir):
        command = ['dpkg-buildpackage', '-uc', '-b']
        child = self.create_child(command, sourcedir)
        child.wait()
        if child.returncode != 0:
            print 'Error(s) occurred while building package'
            return False

        print 'Package(s) built'
        for oldpath in glob('%s/*.deb' % self.tmpdir):
            deb = os.path.basename(oldpath)
            newpath = os.path.join(os.getcwd(), deb)
            shutil.move(oldpath, newpath)
            print 'Created', newpath

        return True

    def try_patch_levels(self, diff, dir, levels):
        for level in range(levels):
            print 'Trying patch level', level, '...',
            command = ['patch', '-t', '-p%d' % level, '-i', diff]
            child = self.create_child(command, dir, pipe=True)
            child.wait()
            if child.returncode == 0:
                print 'Succeeded'
                return True
            else:
                print 'Failed'

        return False

    def handle_quilt_with_patch(self, sourcedir, attachment):
        diff = os.path.join(self.tmpdir, attachment.title)

        if self.try_patch_levels(diff, sourcedir, 2):
            return self.try_dpkg_buildpackage(sourcedir)
        else:
            return False

    def handle_quilt_with_quilt(self, sourcedir, attachment):
        self.move_patch_to_debian(sourcedir, attachment)

        series = os.path.join(sourcedir, 'debian/patches/series')
        with open(series, 'a+b') as fd:
            fd.writelines([attachment.title, ''])

        return self.try_dpkg_buildpackage(sourcedir)

    def handle_quilt(self, sourcedir, attachment):
        remotefd = attachment.data.open()
        data = remotefd.read()
        remotefd.close()

        pattern = r'^--- .*/debian/patches'
        regexp = re.compile(pattern, re.MULTILINE)
        result = regexp.search(data)

        if result:
            return self.handle_quilt_with_patch(sourcedir, attachment)
        else:
            return self.handle_quilt_with_quilt(sourcedir, attachment)

    def handle_cdbs(self, sourcedir, attachment):
        self.move_patch_to_debian(sourcedir, attachment)
        return self.try_dpkg_buildpackage(sourcedir)

    def create_child(self, command, cwd="", pipe=False):
        if cwd == "":
            cwd = self.tmpdir

        connect = pipe and subprocess.PIPE or None

        child = subprocess.Popen(command,
                                 stdin=connect,
                                 stdout=connect,
                                 stderr=connect,
                                 shell=False,
                                 cwd=cwd)
        return child

if __name__ == "__main__":
    usage = '''
    %prog [OPTIONS] LP_URL
    '''
    parser = OptionParser(usage=usage)
    parser.add_option('-d', '--debug',
        action='store_true', dest='DEBUG',
        default=False,
        help='Enable debugging output')
    (options, args) = parser.parse_args()

    if len(args) < 1:
        parser.print_help()
        sys.exit(1)

    flags = 0
    for flagname in BugPatcher.flagnames:
        flags |= getattr(options, flagname) and \
                 getattr(BugPatcher, flagname)

    modifiers = {}

    app = BugPatcher('arsenal-bug-patcher',
        lpurl=args[0],
        flags=flags,
        modifiers=modifiers)
    app.launch()


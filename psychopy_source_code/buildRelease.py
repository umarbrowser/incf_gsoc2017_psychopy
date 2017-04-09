#!python

"""This script is used to:
    - update the version numbers
    - update the psychopyVersions repo:
        - copy over the code
        - commit, tag and push(?)

    It should be run from the root of the main git repository, which should be
    next to a clone of the psychopy/versions git repository
"""

import os, sys, shutil, subprocess
from os.path import join
from createInitFile import createInitFile

MAIN = os.path.abspath(os.path.split(__file__)[0])
VERSIONS = join(MAIN,'..','versions')

def getSHA(cwd='.'):
    if cwd=='.':
        cwd = os.getcwd()
    #get the SHA of the git HEAD
    SHA_string = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'], cwd=cwd).split()[0]
    #convert to hex from a string and return it
    print 'SHA:', SHA_string, 'for repo:',cwd
    return SHA_string

def buildRelease(versionStr, noCommit=False, interactive=True):
    #
    createInitFile(dist='sdist', version=versionStr, sha=getSHA())
    dest = join(VERSIONS,"psychopy")
    shutil.rmtree(dest)
    ignores = shutil.ignore_patterns("demos", "docs", "tests", "pylink",
                                     "*.pyo", "*.pyc", "*.orig", "*.bak",
                                     ".DS_Store", ".coverage")
    shutil.copytree("psychopy", dest, symlinks=False, ignore=ignores)

    #todo: would be nice to check here that we didn't accidentally add anything large (check new folder size)
    Mb = float(subprocess.check_output(["du", "-bsc", dest]).split()[0])/10**6
    print "size for '%s' will be: %.2f Mb" %(versionStr, Mb)
    if noCommit:
        return False

    if interactive:
        ok = raw_input("OK to continue? [n]y :")
        if ok != "y":
            return False

    lastSHA = getSHA(cwd=VERSIONS)
    print 'updating: git add --all'
    output = subprocess.check_output(["git", "add", "--all"], cwd=VERSIONS)
    if interactive:
        ok = subprocess.call(["cola"], cwd=VERSIONS)
        if lastSHA==getSHA():
            #we didn't commit the changes so quit
            print("no git commit was made: exiting")
            return False
    else:
        print "committing: git commit -m 'release version %s'" %versionStr
        subprocess.call(["git", "commit", "-m", "'release version %s'" %versionStr], cwd=VERSIONS)

    print "tagging: git tag -m 'release %s'" %versionStr
    ok = subprocess.call(["git", "tag", versionStr, "-m", "'release %s'" %versionStr], cwd=VERSIONS)

    print "'versions' tags are now:", subprocess.check_output(["git","tag"], cwd=VERSIONS).split()
    ok = subprocess.call(["git", "push", "%s" %versionStr], cwd=VERSIONS)
    if ok:
        print "Successfully pushed tag %s upstream" %versionStr
    else:
        print "Failed to push tag %s upstream" %versionStr

    #revert thte __init__ file to non-ditribution state
    print 'reverting the main master branch: git reset --hard HEAD'
    print subprocess.check_output(["git","reset", "--hard", "HEAD"], cwd=MAIN)
    return True #success

if __name__=="__main__":
    if "--noCommit" in sys.argv:
        noCommit = True
    else:
        noCommit = False
    #todo: update versions first
    versionStr = raw_input("version:")
    buildRelease(versionStr, noCommit=noCommit, interactive=True)

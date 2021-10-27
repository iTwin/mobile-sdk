#!/usr/bin/env python
import argparse
import fileinput
import re
import subprocess
import sys
import os

def getExecutingDirectory():
    return os.path.dirname(os.path.realpath(__file__))

def replaceAll(fileName, replacements):
    for line in fileinput.input(fileName, inplace=1):
        for (searchExp, replaceExp) in replacements:
            line = re.sub(searchExp, replaceExp, line)
        sys.stdout.write(line)

def modifyPackageJson(args, dir):
    fileName = os.path.join(dir, 'package.json')
    if os.path.exists(fileName):
        print "Processing: " + fileName
        replaceAll(fileName, [
            ('("version": )"[\.0-9]+', '\\1"' + args.newVersion),
            ('("@bentley/[a-z-0-9]*"): "2\.19\.[0-9]+', '\\1: "' + args.newBentley),
            ('("@itwin/mobile-sdk-core"): "[\.0-9]+', '\\1: "' + args.newVersion),
            ('("@itwin/mobile-ui-react"): "[\.0-9]+', '\\1: "' + args.newVersion),
        ])
        # if not args.skipInstall:
        #     result = subprocess.check_output(['npm', 'install', '--no-progress', '--loglevel=error', '--audit=false', '--fund=false'], cwd=dir)

def modifyPackageSwift(args, fileName):
    print "Processing: " + os.path.realpath(fileName)
    replaceAll(fileName, [('(mobile-ios-package", .exact\()"[\.0-9]+', '\\1"' + args.newIos)])

def modifyPodspec(args, fileName):
    print "Processing: " + os.path.realpath(fileName)
    replacements = [('(spec.version.*= )"[\.0-9]+', '\\1"' + args.newVersion)]
    replacements.append(('(spec.dependency +"itwin-mobile-ios-package", +"~>) [\.0-9]+', '\\1 ' + args.newIos))
    replaceAll(fileName, replacements)

def modifyPackageResolved(args, fileName):
    print "Processing: " + os.path.realpath(fileName)
    package = None
    for line in fileinput.input(fileName, inplace=1):
        match = re.search('"package": "(.*)"', line)
        if match and len(match.groups()) == 1:
            package = match.group(1)
        if package == 'itwin-mobile-ios':
            line = re.sub('("version": )".*"', '\\1"' + args.newIos + '"', line)
            if (args.newIosCommitId):
                line = re.sub('("revision": )".*"', '\\1"' + args.newIosCommitId + '"', line)
        elif package == 'itwin-mobile-sdk':
            line = re.sub('("version": )".*"', '\\1"' + args.newVersion + '"', line)
            if (args.newCommitId):
                line = re.sub('("revision": )".*"', '\\1"' + args.newCommitId + '"', line)
        sys.stdout.write(line)

def changeCommand(args, dirs):
    dir = executingDir
    parentDir = os.path.realpath(os.path.join(dir, '..'))
    modifyPackageSwift(args, os.path.join(dir, 'Package.swift'))
    modifyPackageSwift(args, os.path.join(dir, 'Package@swift-5.5.swift'))
    modifyPackageResolved(args, os.path.join(dir, 'Package.resolved'))
    modifyPodspec(args, os.path.join(dir, 'itwin-mobile-sdk.podspec'))
    modifyPackageJson(args, os.path.join(parentDir, 'mobile-sdk-core'))
    modifyPackageJson(args, os.path.join(parentDir, 'mobile-ui-react'))
    modifyPackageJson(args, os.path.join(parentDir, 'mobile-sdk-samples/ios/MobileStarter/react-app'))

def commitDir(args, dir):
    print "Committing in dir: " + dir
    rc = subprocess.call(['git', 'diff', '--quiet'], cwd=dir)
    if rc:
        subprocess.check_call(['git', 'add', '.'], cwd=dir)
        subprocess.check_call(['git', 'commit', '-m', 'Update version to ' + args.newVersion], cwd=dir)
    else:
        print "Nothing to commit."

def modifySamplesPackageResolved(args, dir):
    if not hasattr(args, 'newCommitId'):
        args.newCommitId = getLastCommitId(executingDir, args.newVersion)
    modifyPackageResolved(args, os.path.join(dir, 'iOS/SwiftUIStarter/SwiftUIStarter.xcodeproj/project.xcworkspace/xcshareddata/swiftpm/Package.resolved'))
    modifyPackageResolved(args, os.path.join(dir, 'iOS/SwiftUIStarter/LocalSDK_SwiftUIStarter.xcodeproj/project.xcworkspace/xcshareddata/swiftpm/Package.resolved'))
    modifyPackageResolved(args, os.path.join(dir, 'iOS/MobileStarter/LocalSDK_MobileStarter.xcodeproj/project.xcworkspace/xcshareddata/swiftpm/Package.resolved'))
    modifyPackageResolved(args, os.path.join(dir, 'iOS/MobileStarter/MobileStarter.xcodeproj/project.xcworkspace/xcshareddata/swiftpm/Package.resolved'))

def commitCommand(args, dirs):
    if not args.newVersion:
        args.newVersion = getNextRelease()

    print "Committing version: " + args.newVersion
    if args.newVersion:
        for dir in dirs:
            # The Package.resolved files in the sample projects need to be updated with the latest info. 
            # This assumes we've already committed in the mobile-sdk dir so we'll have  a commit id that we can write to the files.
            if dir.endswith('mobile-sdk-samples'):
                modifySamplesPackageResolved(args, dir)
            commitDir(args, dir)

def pushDir(args, dir):
    dir = os.path.realpath(dir)
    print "Pushing in dir: " + dir;
    subprocess.check_call(['git', 'push'], cwd=dir)

def pushCommand(args, dirs):
    for dir in dirs:
        pushDir(args, dir)

def releaseDir(args, dir):
    dir = os.path.realpath(dir)
    print "Releasing in dir: " + dir
    title = args.title if hasattr(args, 'title') else 'v' + args.newVersion
    subprocess.check_call(['gh', 'release', 'create', '-t', title, args.newVersion], cwd=dir)
    subprocess.check_call(['git', 'pull'], cwd=dir)

def releaseUpload(args, dir, fileName):
    dir = os.path.realpath(dir)
    print "Uploading in dir: {} file: {}".format(dir, fileName)
    subprocess.check_call(['gh', 'release', 'upload', args.newVersion, fileName], cwd=dir)

def releaseCommand(args, dirs):
    if not args.newVersion:
        args.newVersion = getNextRelease()
    print "Releasing version: " + args.newVersion

    if args.newVersion:
        for dir in dirs:
            releaseDir(args, dir)
        releaseUpload(args, '.', 'itwin-mobile-sdk.podspec')

def getLastRelease():
    result = subprocess.check_output(['git', 'tag'], cwd=executingDir)
    tags = result.splitlines()
    if isinstance(tags, list):
        return tags[len(tags)-1]

def getNextRelease():
    lastRelease = getLastRelease()
    if lastRelease:
        parts = lastRelease.split('.')
        if len(parts) == 3:
            parts[2] = str(int(parts[2]) + 1)
            newRelease = '.'.join(parts)
            return newRelease

def getLatestBentleyVersion():
    return subprocess.check_output(['npm', 'show', '@bentley/imodeljs-backend', 'version']).strip()

def getLatestNativeVersion():
    deps = subprocess.check_output(['npm', 'show', '@bentley/imodeljs-backend', 'dependencies'])
    match = re.search("'@bentley/imodeljs-native': '([0-9\.]+)'", deps)
    if match and len(match.groups()) == 1:
        return match.group(1)

def getFirstEntryOfLastLine(results):
    if results:
        lines = results.splitlines()
        last = lines[len(lines)-1]
        entries = last.split()
        return entries[0]

def getLastCommitId(dir, tagFilter):
    results = subprocess.check_output(['git', 'show-ref', '--tags', tagFilter], cwd=dir)
    return getFirstEntryOfLastLine(results)

def getLastRemoteCommitId(repo, tagFilter):
    results = subprocess.check_output(['git', 'ls-remote', '--tags', repo, tagFilter])
    return getFirstEntryOfLastLine(results)

def getVersions(args):
    foundAll = False
    newRelease = args.newVersion if hasattr(args, 'newVersion') else getNextRelease()

    if newRelease:
        print "New release: " + newRelease
        imodeljsVersion = getLatestBentleyVersion()
        print "@bentley version: " + imodeljsVersion
        addOnVersion = getLatestNativeVersion()
        if addOnVersion:
            foundAll = True
            print "mobile-ios-package version: " + addOnVersion
            addOnCommitId = getLastRemoteCommitId('https://github.com/iTwin/mobile-ios-package.git', addOnVersion)
            print "mobile-ios-package revision: " + addOnCommitId

    if foundAll:
        args.newVersion = newRelease
        args.newBentley = imodeljsVersion
        args.newIos = addOnVersion
        args.newIosCommitId = addOnCommitId
    return foundAll

def bumpCommand(args, dirs):
    foundAll = getVersions(args)
    if foundAll:
        changeCommand(args, dirs)
    else:
        print "Unable to determine all versions."

def doCommand(args, dirs):
    if args.strings:
        allArgs = ' '.join(args.strings)
        args = allArgs.split()
        for dir in dirs:
            subprocess.call(args, cwd=dir)

def allCommand(args, dirs):
    bumpCommand(args, dirs)
    commitCommand(args, dirs)
    pushCommand(args, dirs)
    releaseCommand(args, dirs)

def samplesCommand(args, dirs):
    foundAll = getVersions(args)
    if foundAll:
        modifySamplesPackageResolved(args, os.path.realpath(executingDir + '/' + '../mobile-sdk-samples'))

if __name__ == '__main__':
    executingDir = getExecutingDirectory()
    dirs = []
    for dir in ['.', '../mobile-sdk-core', '../mobile-ui-react', '../mobile-sdk-samples']:
        dirs.append(os.path.realpath(executingDir + '/' + dir))

    parser = argparse.ArgumentParser(description='Script for helping with creating a new Mobile SDK version.')
    sub_parsers = parser.add_subparsers(title='Commands', metavar='')
    
    parser_bump = sub_parsers.add_parser('bump', help='Create new point release')
    parser_bump.set_defaults(func=bumpCommand)
    parser_bump.add_argument('-n', '--new', dest='newVersion', help='New release version')
    # parser_bump.add_argument('-si', '--skipInstall', dest='skipInstall', help='Skip npm install', action='store_true')

    parser_change = sub_parsers.add_parser('change', help='Change version (alternative to bump, specify versions)')
    parser_change.set_defaults(func=changeCommand)
    parser_change.add_argument('-n', '--new', dest='newVersion', help='New release version', required=True)
    parser_change.add_argument('-nb', '--newBentley', dest='newBentley', help='New @bentley package version', required=True)
    parser_change.add_argument('-ni', '--newIos', dest='newIos', help='New itwin-mobile-ios-package version', required=True)

    parser_commit = sub_parsers.add_parser('commit', help='Commit changes')
    parser_commit.set_defaults(func=commitCommand)
    parser_commit.add_argument('-n', '--new', dest='newVersion', help='New release version')

    parser_push = sub_parsers.add_parser('push', help='Push changes')
    parser_push.set_defaults(func=pushCommand)

    parser_release = sub_parsers.add_parser('release', help='Create releases')
    parser_release.set_defaults(func=releaseCommand)
    parser_release.add_argument('-n', '--new', dest='newVersion', help='New release version')
    parser_release.add_argument('-t', '--title', dest='title', help='Release title')

    parser_all = sub_parsers.add_parser('all', help='Create a new point release and do everything (bump, commit, push, release)')    
    parser_all.set_defaults(func=allCommand)

    parser_do = sub_parsers.add_parser('do', help='Run a command in each dir')    
    parser_do.set_defaults(func=doCommand)
    parser_do.add_argument('strings', metavar='arg', nargs='+')

    parser_samples = sub_parsers.add_parser('samples', help='Modify samples')    
    parser_samples.set_defaults(func=samplesCommand)
    parser_samples.add_argument('-n', '--new', dest='newVersion', help='New release version')

    args = parser.parse_args()
    args.func(args, dirs)
    
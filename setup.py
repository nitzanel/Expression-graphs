def main(argv):
    filename = 'requirements.txt'
    import pip
    retcode = 0
    with open(filename, 'r') as f:
        for line in f:
            pipcode = pip.main(['install', line.strip()])
            retcode = retcode or pipcode
    return retcode

def extract_database():
    import zipfile
    print "extracting database..."
    zfile = zipfile.ZipFile('database/db.zip')
    zfile.extractall('database')
    print "database extracted."
    print "\n************************"
    print "to start using the website, use website.py"
    print "*************************"


if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
    extract_database()

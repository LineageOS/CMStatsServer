import sys

from sqlalchemy import create_engine
from ConfigParser import ConfigParser

from cmstats.utils.string import parse_modversion
from cmstats.model import DBSession, init_database


def init(configPath):
    config = ConfigParser()
    config.readfp(open(configPath))
    init_database(create_engine(config.get('database', 'uri')))

def fixversions():
    if len(sys.argv) != 3:
        print "Usage: cmstats.fixversions [config] [query]"
        sys.exit(1)

    configPath = sys.argv[1]
    query = sys.argv[2]

    init(configPath)

    session = DBSession()
    result = session.query("id", "version", "version_raw").from_statement("SELECT id, version, version_raw FROM devices WHERE version_raw LIKE :query").params(query=query).all()
    count = 0
    print "Found %s matching versions" % len(result)

    for id, version, version_raw in result:
        count += 1
        version_new = parse_modversion(version_raw)

        if version_new != version_raw and version_new is not None:
            session.execute("UPDATE devices SET version=:version, kang=0 WHERE id=:id", {'id': id, 'version': version_new})

        if count % 1000 == 0:
            print "Processed %s versions, %s remaining" % (count, (len(result) - count))
            session.commit()

    session.commit()

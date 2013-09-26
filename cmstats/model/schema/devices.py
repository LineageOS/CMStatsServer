from cmstats import cache
from cmstats.model import Base, DBSession
from cmstats.utils.string import parse_modversion, clean_unicode, clean_unicode
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql.expression import func
import datetime
import logging


class Device(Base):
    __tablename__ = "devices"

    id = Column('id', Integer, primary_key=True)
    hash = Column('hash', String(32), unique=True)
    name = Column('name', String(50), index=True)
    version = Column('version', String(255), index=True)
    version_raw = Column('version_raw', String(255))
    country = Column('country', String(50), index=True)
    carrier_id = Column('carrier_id', String(50), index=True)
    kang = Column('kang', Boolean, index=True)
    date_added = Column('date_added', DateTime)
    date_updated = Column('date_updated', DateTime)

    @classmethod
    def count_kang(cls):
        cache_key = "count_kang"
        def get_from_database():
            q = None
            try:
                session = DBSession()
                q = session.query(func.count(cls.id)).filter(cls.kang == True).one()[0]
                session.close()
            except:
                session.rollback()
                session.close()
            return q

        result = cache.get(cache_key)
        if result is None:
            result = cache.set(cache_key, get_from_database())

        return result

    @classmethod
    def count_nonkang(cls):
        cache_key = "count_nonkang"
        def get_from_database():
            q = None
            try:
                session = DBSession()
                q = session.query(func.count(cls.id)).filter(cls.kang == False).one()[0]
                session.close()
            except:
                session.rollback()
                session.close()
            return q

        result = cache.get(cache_key)
        if result is None:
            result = cache.set(cache_key, get_from_database())

        return result

    @classmethod
    def device_count(cls):
        cache_key = "device_count"
        def get_from_database():
            q = None
            try:
                session = DBSession()
    
                q = session.query(func.count(cls.name), cls.name) \
                    .group_by(cls.name).all()
    
                q = sorted(q, key=lambda x: x[0], reverse=True)
                session.close()
            except:
                session.rollback()
                session.close()
    
            return q

        result = cache.get(cache_key)
        if result is None:
            result = cache.set(cache_key, get_from_database())

        return result

    @classmethod
    def version_count(cls):
        cache_key = "version_count"
        def get_from_database():
            q = None
            try:
                session = DBSession()
    
                q = session.query(func.count(cls.version), cls.version) \
                    .filter(cls.kang == False) \
                    .group_by(cls.version).all()
    
                q = sorted(q, key=lambda x: x[0], reverse=True)
                session.close()
            except:
                session.rollback()
                session.close()
    
            return q

        result = cache.get(cache_key)
        if result is None:
            result = cache.set(cache_key, get_from_database())

        return result

    @classmethod
    def country_count(cls):
        cache_key = "country_count"
        def get_from_database():
            q = None
            try:
                session = DBSession()
                q = session.query(cls.country, func.count('*').label('count')).group_by(cls.country).all()
                session.close()
            except:
                session.rollback()
            return q

        result = cache.get(cache_key)
        if result is None:
            result = cache.set(cache_key, get_from_database())

        return result

    @classmethod
    def count_last_day(cls):
        cache_key = "count_last_day"
        def get_from_database():
            timestamp = datetime.datetime.now() - datetime.timedelta(hours=24)
            session = DBSession()
            q = None
            try:
                q = session.query(cls).filter(cls.date_added > timestamp).count()
                session.close()
            except:
                session.rollback()
                session.close()
            return q

        result = cache.get(cache_key)
        if result is None:
            result = cache.set(cache_key, get_from_database())

        return result

    @classmethod
    def add(cls, **kwargs):
        from cmstats import summary
        # Clean up the version.
        version = parse_modversion(kwargs['version'])

        # Grab a session
        session = DBSession()

        # Grab device record, if it already exists.
        try:
            obj = session.query(cls).filter(cls.hash == kwargs['hash']).one()
        except Exception, e:
            obj = cls()
            obj.date_added = func.now()

        # Flag this as a KANG if necessary.
        if version == None:
            version = kwargs['version']
            obj.kang = True
        else:
            obj.kang = False

        # Clean up any funky characters
        kwargs['name'] = clean_unicode(kwargs['name'])
        version = clean_unicode(version)

        if obj.hash is None:
            if summary.devices.get(kwargs['name']) is None:
                summary.devices[kwargs['name']] = 0

            summary.devices[kwargs['name']] += 1

            if version == None:
                summary.kang += 1
            else:
                summary.official += 1

                if summary.versions.get(version) is None:
                    summary.versions[version] = 0

                summary.versions[version] += 1

        summary.submits += 1

        logging.debug("Summary: kang=[%s], official=[%s], submits=[%s]" % (summary.kang, summary.official, summary.submits))

        # Populate the rest of the records.
        obj.hash = kwargs['hash']
        obj.name = kwargs['name']
        obj.version = version
        obj.version_raw = kwargs['version']
        obj.country = kwargs['country']
        obj.carrier_id = kwargs['carrier_id']
        obj.date_updated = func.now()

        logging.debug("Saving: %s" % obj)

        session.add(obj)
        try:
            session.commit()
        except Exception, e:
            summary.databaseExceptions += 1
            logging.error("Error commiting! %s" % e)
            session.rollback()
        session.close()

    def __str__(self):
        return "%(class)s(hash=%(hash)s, name=%(name)s, version=%(version)s, version_raw=%(version_raw)s, country=%(country)s)" % {
            'class': self.__class__.__name__,
            'hash': self.hash,
            'name': clean_unicode(self.name),
            'version': clean_unicode(self.version),
            'version_raw': clean_unicode(self.version_raw),
            'country': clean_unicode(self.country),
        }

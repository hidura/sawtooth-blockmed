#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

""" 
Creation: 13/2/20
Author: hidura
"""

from sqlalchemy import Column, MetaData, Table, BIGINT, Text

#The db definition is there just in case is the same structure.
from DataBase.Base import db

class User(db.Model):
    metadata = MetaData(db.engine)
    __tablename__ = "user_reg"

    __table_args__ = {"useexisting": True}
    id = Column('id', BIGINT, primary_key=True)
    idcard = Column("idcard", Text)
    passwd = Column("passwd", Text)
    user_type = Column("user_type", BIGINT)
    idcard_type = Column("idcard_type", BIGINT)
    email = Column("email", Text)
    first_name=Column("first_name", Text)
    last_name=Column("last_name", Text)

    User_tbl = Table(__tablename__, metadata, id, idcard, passwd, user_type, email, first_name, last_name,idcard_type)

    def __repr__(self):
        return "<User (id='%s',idcard='%s', passwd='%s',user_type='%s', email='%s',fist_name='%s',last_name='%s', idcard_type='%s')>" % \
               (self.id, self.idcard, self.passwd, self.user_type, self.email, self.first_name,self.last_name, self.idcard_type)

    metadata.create_all()

    def __Publish__(self):
        data = {}
        for column in self.__table__.columns.keys():
            value = self.__dict__[self.__table__.columns[column].name]
            if self.__table__.columns[column].type == "BIGINT":
                data[self.__table__.columns[column].name] = int(value)
            elif self.__table__.columns[column].type == "Integer":
                data[self.__table__.columns[column].name] = int(value)

            elif self.__table__.columns[column].type == "NUMERIC":
                data[self.__table__.columns[column].name] = float(value)
            elif self.__table__.columns[column].type == "Decimal":
                data[self.__table__.columns[column].name] = float(value)

            elif self.__table__.columns[column].type == "time":
                data[self.__table__.columns[column].name] = str(value.strftime('%H:%M:%S'))
            elif self.__table__.columns[column].type == "datetime":
                data[self.__table__.columns[column].name] = str(value.strftime('%a %d/%m/%Y'))
            else:
                data[self.__table__.columns[column].name] = str(value)
        return data

    @staticmethod
    def get_all():
        s = db.session.query(User)
        return s

    @staticmethod
    def insert(data):
        results = User(**data)
        db.session.add(results)
        db.session.commit()
        return results

    @staticmethod
    def bulk_insert(data):
        results = db.session.bulk_save_objects(data)
        db.session.commit()
        return results
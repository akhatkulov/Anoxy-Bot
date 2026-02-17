from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, BigInteger, func,VARCHAR
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError

import conf

engine = create_engine(conf.DB_URI)
Base = declarative_base()

class User(Base):
    __tablename__ = 'user_anoxy'
    id = Column(Integer, primary_key=True, autoincrement=True)
    cid = Column(BigInteger, unique=True)
    cid2 = Column(BigInteger, default=0)

class User_info(Base):
    __tablename__ = 'info_anoxy'
    id = Column(Integer,primary_key=True,autoincrement=True)
    cid = Column(BigInteger,unique=True)
    pic = Column(String,nullable=False)
    name = Column(VARCHAR(75))
    gender = Column(VARCHAR(75))
    age = Column(Integer)
    info = Column(String)
    contact = Column(String)

class Step(Base):
    __tablename__ = 'step_anoxy'
    id = Column(Integer, primary_key=True, autoincrement=True)
    cid = Column(BigInteger, unique=True)
    step = Column(String, default="0")
    arg = Column(BigInteger, default=0)

class Channels(Base):
    __tablename__ = 'channels_anoxy'
    id = Column(Integer, primary_key=True, autoincrement=True)
    link = Column(String, default="None", unique=True)

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

def get_all_user():
    try:
        x = session.query(User.cid).all()
        res = [i[0] for i in x]
        return res
    finally:
        session.close()

def user_count():
    try:
        x = session.query(func.count(User.id)).first()
        return x[0]
    finally:
        session.close()

def create_user(cid):
    try:
        user = User(cid=int(cid), cid2=0)
        step = Step(cid=int(cid), step="0", arg=0)
        info = User_info(cid=int(cid), pic="demo link")
        session.add(user)
        session.add(step)
        session.add(info)
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Error: {e}")
    finally:
        session.close()

def get_info(cid : int):
    try:
        x = session.query(User_info).filter_by(cid=cid).first()
        res = {"cid":cid, "age" : x.age ,"name": x.name, "info":x.info, "contact": x.contact,'pic':x.pic,"gender":x.gender}
        return res 
    finally:
        session.close()

def change_info(cid : int, type_info : str, value : str):
    x = session.query(User_info).filter_by(cid=cid).first()
    try:
        if type_info == "name":
            x.name = value
        elif type_info == "gender":
            x.gender = value
        elif type_info == "info":
            x.info = value
        elif type_info == "contact":
            x.contact = value
        elif type_info == "pic":
            x.pic = value
        elif type_info == "age":
            x.age = int(value)
        session.commit()
        return True
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Error: {e}")
        return False
    finally:
        session.close()

def check_user(cid : int):
    try:
        x = session.query(User_info).filter_by(cid=cid).first()
        name = x.name
        info = x.info 
        pic = x.pic
        contact = x.contact
        gender = x.gender
        if name == None or info == None or pic == None or contact == None or gender == None:
            return False
        else:
            return True
    except:
        return False
    finally:
        session.close()



def get_cid2(cid):
    try:
        x = session.query(User).filter_by(cid=cid).first()
        return x.cid2 if x else None
    finally:
        session.close()

def get_members():
    try:
        x = session.query(User).where(User.cid >= 0).all()
        return x
    finally:
        session.close()

def put_cid2(cid, cid2):
    try:
        x = session.query(User).filter_by(cid=cid).first()
        if x:
            x.cid2 = int(cid2)
            session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Error: {e}")
    finally:
        session.close()

def get_step(cid):
    try:
        x = session.query(Step).filter_by(cid=cid).first()
        return x.step if x else None
    finally:
        session.close()

def put_step(cid, step):
    try:
        x = session.query(Step).filter_by(cid=cid).first()
        if x:
            x.step = str(step)
            session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Error: {e}")
    finally:
        session.close()

def get_arg(cid):
    try:
        x = session.query(Step).filter_by(cid=cid).first()
        return x.arg if x else None
    finally:
        session.close()

def put_arg(cid, arg):
    try:
        x = session.query(Step).filter_by(cid=cid).first()
        if x:
            x.arg = arg
            session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Error: {e}")
    finally:
        session.close()

def put_channel(channel: str):
    try:
        x = Channels(link=channel)
        session.add(x)
        session.commit()
        return True
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Error: {e}")
        return False
    finally:
        session.close()

def get_channel():
    try:
        x = session.query(Channels).all()
        res = [i.link for i in x]
        return res
    finally:
        session.close()

def get_channel_with_id():
    try:
        x = session.query(Channels).all()
        res = ""
        for channel in x:
            res += f"\nID: {channel.id} \nLink: @{channel.link}"
        return res
    finally:
        session.close()

def delete_channel(ch_id):
    try:
        x = session.query(Channels).filter_by(id=int(ch_id)).first()
        if x:
            session.delete(x)
            session.commit()
            return True
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Error: {e}")
        return False
    finally:
        session.close()
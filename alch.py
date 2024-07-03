from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, BigInteger, func
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError

engine = create_engine("postgresql://postgres:1945@localhost/postgres")
Base = declarative_base()

class User(Base):
    __tablename__ = 'user_anoxy'
    id = Column(Integer, primary_key=True, autoincrement=True)
    cid = Column(BigInteger, unique=True)
    cid2 = Column(BigInteger, default=0)

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

def get_all_user():
    session = Session()
    try:
        x = session.query(User.cid).all()
        res = [i[0] for i in x]
        return res
    finally:
        session.close()

def user_count():
    session = Session()
    try:
        x = session.query(func.count(User.id)).first()
        return x[0]
    finally:
        session.close()

def create_user(cid):
    session = Session()
    try:
        user = User(cid=int(cid), cid2=0)
        step = Step(cid=int(cid), step="0", arg=0)
        session.add(user)
        session.add(step)
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Error: {e}")
    finally:
        session.close()

def get_cid2(cid):
    session = Session()
    try:
        x = session.query(User).filter_by(cid=cid).first()
        return x.cid2 if x else None
    finally:
        session.close()

def get_members():
    session = Session()
    try:
        x = session.query(User).where(User.cid >= 0).all()
        return x
    finally:
        session.close()

def put_cid2(cid, cid2):
    session = Session()
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
    session = Session()
    try:
        x = session.query(Step).filter_by(cid=cid).first()
        return x.step if x else None
    finally:
        session.close()

def put_step(cid, step):
    session = Session()
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
    session = Session()
    try:
        x = session.query(Step).filter_by(cid=cid).first()
        return x.arg if x else None
    finally:
        session.close()

def put_arg(cid, arg):
    session = Session()
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
    session = Session()
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
    session = Session()
    try:
        x = session.query(Channels).all()
        res = [i.link for i in x]
        return res
    finally:
        session.close()

def get_channel_with_id():
    session = Session()
    try:
        x = session.query(Channels).all()
        res = ""
        for channel in x:
            res += f"\nID: {channel.id} \nLink: @{channel.link}"
        return res
    finally:
        session.close()

def delete_channel(ch_id):
    session = Session()
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

print(get_channel_with_id())

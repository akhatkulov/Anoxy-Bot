from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String,BigInteger, func
from sqlalchemy.orm import sessionmaker, declarative_base

engine = create_engine("postgresql://postgres:1945@localhost/postgres")
Base = declarative_base()

class User(Base):
    __tablename__ = 'user_anoxy'
    id = Column(Integer, primary_key=True, autoincrement=True)
    cid = Column(BigInteger, unique=True)
    cid2 = Column(BigInteger, default=0)

class Step(Base):
    __tablename__ = 'step_anoxy'
    id = Column(Integer,primary_key=True, autoincrement=True)
    cid = Column(BigInteger, unique=True)
    step = Column(String, default="0")
    arg = Column(BigInteger,default=0)


class Channels(Base):
    __tablename__ = 'channels_anoxy'
    id = Column(Integer,primary_key=True,autoincrement=True)
    link = Column(String,default="None",unique=True)


Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

def get_all_user():
    x = session.query(User.cid).all()
    res = []
    for i in x:
        res.append(i[0])
        # print(i[0])
    return res

# print(get_all_user())
def user_count():
    x = session.query(func.count(User.id)).first()
    # print(x[0])
    return x[0]
user_count()

def create_user(cid):
    try:
        user = User(cid=int(cid), cid2=0)
        step = Step(cid=int(cid), step="0",arg=0)
        session.add(user)
        session.add(step)
        session.commit()
    except:
        session.rollback()
def get_cid2(cid):
    x = session.query(User).filter_by(cid=cid).first()
    # print(x.cid2)
    return x.cid2
def get_members():
    x = session.query(User).where(User.cid>=0).all()
    print(x)
    return x


# print(session.query(User).all())

def put_cid2(cid, cid2):
    x = session.query(User).filter_by(cid=cid).first()
    x.cid2 = int(cid2) 
    session.commit()


def get_step(cid):
    x = session.query(Step).filter_by(cid=cid).first()
    return x.step

def put_step(cid,step):
    x = session.query(Step).filter_by(cid=cid).first()
    x.step = str(step)
    session.commit()

def get_arg(cid):
    x = session.query(Step).filter_by(cid=cid).first()
    return x.arg

def put_arg(cid,arg):
    x = session.query(Step).filter_by(cid=cid).first()
    x.arg = arg
    session.commit()

def put_channel(channel: str):
    try:
        x = Channels(link=channel)
        session.add(x)
        session.commit()
        return True
    except:
        session.rollback()
        return False

def get_channel():
    x = session.query(Channels).all()
    res = []
    for i in x:
        res.append(i.link)
    return res

print(get_channel())
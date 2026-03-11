from sqlalchemy import text,select,and_
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from datetime import datetime,timedelta
from typing import List
from sqlalchemy.orm import sessionmaker
import asyncpg
import os
from dotenv import load_dotenv
from backend.database.main_models  import metadata_obj,login_table
import asyncio
import atexit
from sqlalchemy import func
#backend.database.


load_dotenv()


async_engine = create_async_engine(
    f"postgresql+asyncpg://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@localhost:5432/login_database_obj_ai",
    pool_size=20,           
    max_overflow=50,       
    pool_recycle=3600,     
    pool_pre_ping=True,    
    echo=False
)



AsyncSessionLocal = sessionmaker(
    async_engine, 
    class_=AsyncSession,
    expire_on_commit=False
)

async def drop_table():
    async with async_engine.begin() as conn:
        await conn.run_sync(metadata_obj.drop_all)

async def create_table():
    async with async_engine.begin() as conn:
        await conn.run_sync(metadata_obj.create_all)

        
async def is_user_exists(username:str) -> bool:
   async with AsyncSession(async_engine) as conn:
       stmt = select(login_table.c.username).where(login_table.c.username == username)
       res = await conn.execute(stmt)
       data = res.scalar_one_or_none()
       if data is not None:
           return True
       return False 
   
   
async def register(username:str,password:str) -> bool:
    if await is_user_exists(username):
        return False
    async with AsyncSession(async_engine) as conn:
        async with conn.begin():
            try:
                date_now = datetime.now().date()
                stmt = login_table.insert().values(
                    username = username,
                    hash_password = password,
                    sub = False,
                    date_free_sub = date_now
                )
                await conn.execute(stmt)
                return True
            except Exception as e:
                raise Exception(f"Error : {e}")

async def login(username:str,try_psw:str) -> bool:
    if not await is_user_exists(username):
        return False
    async with AsyncSession(async_engine) as conn:
        async with conn.begin():
            try:
                stmt = select(login_table.c.hash_password).where(login_table.c.username == username)
                res = await conn.execute(stmt)
                data = res.scalar_one_or_none()
                return str(data) == try_psw if data is not None else False
            except Exception as e:
                raise Exception(f"Error : {e}")

async def get_user_free_trial_end_date(username:str) -> str | bool:
    if not await is_user_exists(username):
        return False  
    async with AsyncSession(async_engine) as conn:
        try:
            stmt = select(login_table.c.date_free_sub).where(login_table.c.username == username)
            res = await conn.execute(stmt)
            data = res.scalar_one_or_none()
            return str(data) if data is not None else False 
        except Exception as e:
            raise Exception(f"Error : {e}")
                   
            
async def set_sub_to_something(username:str,action:bool) -> bool:# функция которая отписывает и подписывает
    if not await is_user_exists(username):
        return False
    async with AsyncSession(async_engine) as conn:
        async with conn.begin():
            try:
                stmt = login_table.update().where(login_table.c.username == username).values(
                    sub = action
                )
                await conn.execute(stmt)
                return True
            except Exception as e:
                raise Exception(f"Error : {e}")

async def is_user_subbed(username:str) -> bool | dict:
    if not await is_user_exists(username):
        return {
            "username":username,
            "Error": "Not found"
        }
    async with AsyncSession(async_engine) as conn:
        try:
            stmt = select(login_table.c.sub).where(login_table.c.username == username)
            res = await conn.execute(stmt)
            data = res.scalar_one_or_none()
            return data
        except Exception as e:
            raise Exception(f"Error : {e}")
        
async def get_user_data(username:str) -> dict:
    if not await is_user_exists(username):
        return {}
    async with AsyncSession(async_engine) as conn:
        try:
            stmt = select(login_table.c.date_free_sub).where(login_table.c.username == username)
            res = await conn.execute(stmt)
            data = res.scalar_one_or_none()
            return {
                "sub":username,
                "date":str(data)
            }
        except Exception as e:
            raise Exception(f"Error : {e}")

async def is_user_date_ended(username:str) -> bool:
    pass

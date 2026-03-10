from sqlalchemy import Table,MetaData,Column,String,Date,Boolean

metadata_obj = MetaData()

login_table = Table(
    "login_table_obj_ai",
    metadata_obj,
    Column("username",String,primary_key=True),
    Column("hash_password",String),
    Column("date_free_sub",Date),
    Column("sub",Boolean)
)
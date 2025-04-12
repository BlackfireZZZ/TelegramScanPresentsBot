from peewee import SqliteDatabase, Model, IntegerField, BooleanField


db = SqliteDatabase('src/database/database_file/database.db')


class User(Model):
    id = IntegerField(primary_key=True)
    mode = IntegerField(default=1) # 1 - dont use recursion, 2 - use recursion
    level = IntegerField(default=1) # recursion level
    is_parser = BooleanField(default=False)

    class Meta:
        database = db
        table_name = 'users'


with db:
    db.create_tables([User])


class Database:
    def new_user(user_id: int):
        if not User.select().where(User.id == user_id).exists():
            User.create(id=user_id)
    
    def admin_exists(user_id: int):
        return User.select().where(User.id == user_id).exists()

    def get_user_mode(user_id: int):
        return User.select().where(User.id == user_id).first().mode

    def get_user_level(user_id: int):
        return User.select().where(User.id == user_id).first().level
    
    def update_user_mode(user_id: int, mode: int):
        User.update(mode=mode).where(User.id == user_id).execute()

    def update_user_level(user_id: int, level: int):
        User.update(level=level).where(User.id == user_id).execute()

    def update_user_is_parser(user_id: int, is_parser: bool):
        User.update(is_parser=is_parser).where(User.id == user_id).execute()
    
    def get_user_is_parser(user_id: int):
        return User.select().where(User.id == user_id).first().is_parser


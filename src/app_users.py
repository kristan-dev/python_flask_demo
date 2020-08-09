from src.util.db import Database
import src.util.logger
import logging
import json

class Users:
  @staticmethod
  def get_all_users():
    Database.create_db_connection()
    logging.info("Connected to DB")
    pass

  @classmethod
  def sign_up(cls, user_data):
    Database.create_db_connection()
    logging.info("Connected to DB")
    try:
      insert_cursor = Database.database_connection.cursor()
      insert_sql = "INSERT INTO sample_schema.users VALUES(%s)"
      insert_cursor.execute(insert_sql, (user_data["email"], user_data["password"], user_data["username"], user_data["user_type"],))
      Database.commit_db_actions()
    except Exception as e:
      Database.rollback_db_actions()
      Database.close_db_connection()
      raise e

  @classmethod
  def log_in(cls):
    pass
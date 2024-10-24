#!/bin/bash

DB_PATH="user_data.db"

SQL_QUERY="SELECT * FROM survey_data ORDER BY answer ASC"

COUNT_QUERY="SELECT COUNT(username) FROM survey_data"

echo " "
echo "reading user count..."
echo " "

sqlite3 "$DB_PATH" "$COUNT_QUERY"

echo "of 337 users answered"
echo " "
echo "reading user data..."
echo " "

sqlite3 "$DB_PATH" "$SQL_QUERY"

echo





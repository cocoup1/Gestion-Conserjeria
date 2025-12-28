"""
core package.

Azure App Service (Code) does not provide system MySQL client libraries required by
mysqlclient (MySQLdb). Use PyMySQL (pure Python) as a drop-in replacement.
"""
import pymysql

pymysql.install_as_MySQLdb()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Simple Bot to reply to Telegram messages
# This program is dedicated to the public domain under the CC0 license.
"""
EzPro BOT, Model
"""

import bot_main


def get_status_id(name):
    sql = "SELECT id FROM ezpro_status WHERE name = '%s'" % name
    cursor = bot_main.db.query(sql)
    records = cursor.fetchall()
    bot_main.db.commit()

    if cursor.rowcount > 0:
        for row in records:
            return row[0]


def get_teknisi(id):
    sql = "SELECT * FROM ezpro_user WHERE id = '%s' " % id
    cursor = bot_main.db.query(sql)
    records = cursor.fetchall()
    bot_main.db.commit()

    if cursor.rowcount > 0:
        for row in records:
            return row[7]


def get_category_id(name):
    sql = "SELECT * FROM ezpro_categoryresult WHERE name = '%s' " % name
    cursor = bot_main.db.query(sql)
    records = cursor.fetchall()
    bot_main.db.commit()

    if cursor.rowcount > 0:
        for row in records:
            return row[0]


def get_wo_teknisi(user_id, status_id):
    sql = "SELECT * FROM ezpro_user A " \
          "LEFT JOIN ezpro_scbe B ON A.id = B.first_technician_id " \
          "LEFT JOIN ezpro_service C ON B.service_id = C.id " \
          "LEFT JOIN ezpro_sto D ON B.sto_id = D.id " \
          "LEFT JOIN ezpro_status E ON B.status_id = E.id " \
          "WHERE A.id = '%s' AND B.status_id = '%s'" % (user_id, status_id)
    cursor = bot_main.db.query(sql)
    return cursor


def get_scbe(user_id, status_id):
    sql = "SELECT * FROM ezpro_user A " \
          "LEFT JOIN ezpro_user_sto B ON A.id = B.customuser_id " \
          "LEFT JOIN ezpro_sto C ON B.sto_id = C.id " \
          "LEFT JOIN ezpro_scbe D ON C.id = D.sto_id " \
          "LEFT JOIN ezpro_service E ON D.service_id = E.id " \
          "LEFT JOIN ezpro_categoryresult F ON D.category_result_id = F.id " \
          "WHERE A.id = '%s' AND D.status_id = '%s'" % (user_id, status_id)
    cursor = bot_main.db.query(sql)
    return cursor


def get_order(user_id, status_id):
    sql = "SELECT * FROM ezpro_sto A " \
          "LEFT JOIN ezpro_scbe B ON A.id = B.sto_id " \
          "LEFT JOIN ezpro_service C ON B.service_id = C.id " \
          "LEFT JOIN ezpro_categoryresult D ON B.category_result_id = D.id " \
          "WHERE B.sales_id = '%s' AND B.status_id = '%s'" % (user_id, status_id)
    cursor = bot_main.db.query(sql)
    return cursor

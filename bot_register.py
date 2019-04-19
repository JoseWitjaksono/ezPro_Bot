#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Simple Bot to reply to Telegram messages
# This program is dedicated to the public domain under the CC0 license.
"""
EzPro BOT, Register Module
"""

from telegram import (ParseMode, ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)
import logging
import bot_main

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

REGISTER_TA, REGISTER_MITRA, REGISTER_TELKOM, REGISTER_SALES, \
    APPROVE_TA, APPROVE_MITRA, APPROVE_TELKOM, APPROVE_SALES, REGISTER = range(9)


def register(bot, update, user_data):
    user = update.message.from_user
    text = update.message.text
    user_data['unit'] = text

    logger.info("Unit of %s: %s", user.first_name, text)

    if update.message.text == "Teknisi TA":
        update.message.reply_text('Silahkan Input NIK Anda',
                                  reply_markup=ReplyKeyboardRemove())
        return REGISTER_TA

    elif update.message.text == "Teknisi Mitra":
        update.message.reply_text('Silahkan Input NIK Anda',
                                  reply_markup=ReplyKeyboardRemove())
        return REGISTER_MITRA

    elif update.message.text == "Telkom":
        update.message.reply_text('Silahkan Input NIK Anda',
                                  reply_markup=ReplyKeyboardRemove())
        return REGISTER_TELKOM

    elif update.message.text == "Sales":
        update.message.reply_text('Silahkan Input KContact Anda',
                                  reply_markup=ReplyKeyboardRemove())
        return REGISTER_SALES


def register_teknisi_ta(bot, update, user_data):
    reply_keyboard = [['Ya', 'Tidak']]
    db_data = {}
    user = update.message.from_user
    text = update.message.text

    logger.info("NIK TA of %s: %s", user.first_name, text)

    sql = "SELECT * FROM ezpro_user WHERE username = '%s'" % text
    cursor = bot_main.db.query(sql)
    records = cursor.fetchall()
    bot_main.db.commit()

    if cursor.rowcount > 0:
        user_data['nik'] = text
        for row in records:
            db_data['name'] = row[7]
            db_data['phone_number'] = row[9]
        update.message.reply_text(
            "Apakah data ini sesuai ?\n"
            "Nama : "
            "{}"
            "\nNomor Telepon : "
            "{}".format(db_data['name'], db_data['phone_number']),
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))
        return APPROVE_TA
    else:
        del user_data
        update.message.reply_text("NIK anda tidak ditemukan.\nSilahkan input NIK anda")
        return REGISTER_TA


def approve_teknisi_ta(bot, update, user_data):
    text = update.message.text
    if text == 'Ya':
        update.message.reply_text(
            "Terimakasih, akun anda akan segera kami aktivasi."
            "{}".format(bot_main.array_to_str(user_data)), parse_mode=ParseMode.HTML,)
        activate_user(user_data)
    else:
        update.message.reply_text("Silahkan ulangi registrasi dengan mengklik tombol /start")

    return ConversationHandler.END


def register_teknisi_mitra(bot, update, user_data):
    reply_keyboard = [['Ya', 'Tidak']]
    db_data = {}
    user = update.message.from_user
    text = update.message.text

    logger.info("NIK MITRA of %s: %s", user.first_name, text)

    sql = "SELECT * FROM ezpro_user WHERE username = '%s'" % text
    cursor = bot_main.db.query(sql)
    records = cursor.fetchall()
    bot_main.db.commit()

    if cursor.rowcount > 0:
        user_data['nik'] = text
        for row in records:
            db_data['name'] = row[7]
            db_data['phone_number'] = row[9]
        update.message.reply_text(
            "Apakah data ini sesuai ?\n"
            "Nama : "
            "{}"
            "\nNomor Telepon : "
            "{}".format(db_data['name'], db_data['phone_number']),
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))
        return APPROVE_MITRA
    else:
        del user_data
        update.message.reply_text("NIK anda tidak ditemukan.\nSilahkan input NIK anda")
        return REGISTER_MITRA


def approve_teknisi_mitra(bot, update, user_data):
    text = update.message.text
    if text == 'Ya':
        update.message.reply_text(
            "Terimakasih, akun anda akan segera kami aktivasi."
            "{}".format(bot_main.array_to_str(user_data)), parse_mode=ParseMode.HTML)
        activate_user(user_data)
    else:
        update.message.reply_text("Silahkan ulangi registrasi dengan mengklik tombol /start")

    return ConversationHandler.END


def register_telkom(bot, update, user_data):
    reply_keyboard = [['Ya', 'Tidak']]
    db_data = {}
    user = update.message.from_user
    text = update.message.text

    logger.info("NIK TA of %s: %s", user.first_name, text)

    sql = "SELECT * FROM ezpro_user WHERE username = '%s'" % text
    cursor = bot_main.db.query(sql)
    records = cursor.fetchall()
    bot_main.db.commit()

    if cursor.rowcount > 0:
        user_data['nik'] = text
        for row in records:
            db_data['name'] = row[7]
            db_data['phone_number'] = row[9]
        update.message.reply_text(
            "Apakah data ini sesuai ?\n"
            "Nama : "
            "{}"
            "\nNomor Telepon : "
            "{}".format(db_data['name'], db_data['phone_number']),
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))
        return APPROVE_TELKOM
    else:
        del user_data
        update.message.reply_text("NIK anda tidak ditemukan.\nSilahkan ulangi input NIK anda")
        return REGISTER_TELKOM


def approve_telkom(bot, update, user_data):
    text = update.message.text
    if text == 'Ya':
        update.message.reply_text(
            "Terimakasih, akun anda akan segera kami aktivasi."
            "{}".format(bot_main.array_to_str(user_data)), parse_mode=ParseMode.HTML)
        activate_user(user_data)
    else:
        update.message.reply_text("Silahkan ulangi registrasi dengan mengklik tombol /start")

    return ConversationHandler.END


def register_sales(bot, update, user_data):
    reply_keyboard = [['Ya', 'Tidak']]
    db_data = {}
    user = update.message.from_user
    text = update.message.text

    logger.info("KContact Sales of %s: %s", user.first_name, text)

    sql = "SELECT * FROM ezpro_user WHERE username = '%s'" % text
    cursor = bot_main.db.query(sql)
    records = cursor.fetchall()
    bot_main.db.commit()

    if cursor.rowcount > 0:
        user_data['nik'] = text
        for row in records:
            db_data['name'] = row[7]
            db_data['phone_number'] = row[9]
        update.message.reply_text(
            "Apakah data ini sesuai ?\n"
            "Nama : "
            "{}"
            "\nNomor Telepon : "
            "{}".format(db_data['name'], db_data['phone_number']),
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))
        return APPROVE_SALES
    else:
        del user_data
        update.message.reply_text("KCONTACT anda tidak ditemukan.\nSilahkan input KCONTACT anda")
        return REGISTER_SALES


def approve_sales(bot, update, user_data):
    text = update.message.text
    if text == 'Ya':
        update.message.reply_text(
            "Terimakasih, akun anda akan segera kami aktivasi."
            "{}".format(bot_main.array_to_str(user_data)),  parse_mode=ParseMode.HTML)
        activate_user(user_data)
    else:
        update.message.reply_text("Silahkan ulangi registrasi dengan mengklik tombol /start")
    return ConversationHandler.END


def activate_user(user_data):
    placeholders = "username = '%s'" % (user_data['nik'])
    columns = "chat_id = '%s', username_telegram = '%s'" % (user_data['chat_id'], user_data['username'])
    table = 'ezpro_user'
    sql = "UPDATE %s SET %s WHERE %s" % (table, columns, placeholders)
    bot_main.db.query(sql)
    bot_main.db.commit()
    print("Record Updated successfully ")


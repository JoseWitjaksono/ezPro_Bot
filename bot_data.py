#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Simple Bot to reply to Telegram messages
# This program is dedicated to the public domain under the CC0 license.
"""
EzPro BOT, Data Module
"""
from telegram.utils.helpers import escape_markdown
from telegram import ParseMode, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler, InlineQueryHandler, CallbackQueryHandler)
import logging
import requests
import json
import bot_main
import model
from datetime import datetime

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
date = datetime.now()
nowtime = date.replace(hour=00, minute=00, second=00)


def get_id(chat_id):
    sql = "SELECT * FROM ezpro_user WHERE chat_id = '%s' " % chat_id
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


def rest_get_myir(myir):
    url = 'http://api.indihome.co.id/api/track-view'
    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Authorization": "Basic bXlpbmRpaG9tZTpwN2Qya0xYNGI0TkY1OFZNODR2Vw=="}
    payload = 'guid=myindihome#2017&code=&data={"trackId":"%s"}' % myir

    return requests.post(url, data=payload, headers=headers)


def rest_track_myir(myir):
    url = 'http://api.indihome.co.id/api/get-milestone-order'
    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Authorization": "Basic bXlpbmRpaG9tZTpwN2Qya0xYNGI0TkY1OFZNODR2Vw=="}
    payload = 'guid=myindihome#2017&code=&data={"trackId":"%s"}' % myir

    return requests.post(url, data=payload, headers=headers)


def rest_get_sc(sc):
    url = "https://starclick.telkom.co.id/backend/public/api/tracking?_dc=1533002388191&ScNoss=true&Field=ORDER_ID&SearchText=" + sc
    # url = "http://localhost/json.php"
    return requests.get(url)


def cek_sc(bot, update):
    data = {}
    text = update.message.text
    if text == "⬅️ Kembali":
        return bot_main.start(bot, update, data)
    data_ = str(rest_get_sc(text).text)
    json_ = json.loads(data_)

    if len(json_['data']) == 0:
        update.message.reply_text('SC Tidak ditemukan',
                                  reply_markup=ReplyKeyboardMarkup([['⬅️ Kembali']], one_time_keyboard=True,
                                                                   resize_keyboard=True))
        return ConversationHandler.END
    else:
        real_data = json_['data'][0]
        track_id = real_data['KCONTACT'].split(';')[1]
        data_track = str(rest_track_myir(track_id).text)
        json_track = json.loads(data_track)
        track_data = json_track['data'][0]

        data['No. SC'] = real_data['ORDER_ID']
        data['Tanggal Order'] = real_data['ORDER_DATE']
        data['Status Order'] = real_data['STATUS_RESUME']
        data['Message 1'] = track_data['MESSAGE1']
        data['Message 2'] = track_data['MESSAGE2']
        data['Tanggal PS'] = real_data['ORDER_DATE_PS']
        data['NCLI'] = real_data['NCLI']
        data['Nama Customer'] = real_data['CUSTOMER_NAME']
        data['Alamat Instalasi'] = real_data['INS_ADDRESS']
        data['Track ID'] = real_data['KCONTACT'].split(';')[1]
        data['No Inet'] = "-" if real_data['SPEEDY'] is None else real_data['SPEEDY'].split('~')[1]
        data['No Pots'] = real_data['POTS']
        data['Nama Alpro'] = real_data['LOC_ID']
        data['Witel'] = real_data['WITEL']
        data['STO'] = real_data['XS2']
        update.message.reply_text(
            "🔍 <b>Cek SC</b>\n"
            "{}".format(bot_main.array_to_str(data)), parse_mode=ParseMode.HTML,
            reply_markup=ReplyKeyboardMarkup([['⬅️ Kembali']], one_time_keyboard=True, resize_keyboard=True))
        return ConversationHandler.END


def cek_myir(bot, update):
    data = {}
    text = update.message.text
    if text == "⬅️ Kembali":
        return bot_main.start(bot, update, data)
    data_ = str(rest_get_myir(text).text)
    json_ = json.loads(data_)

    if json_['code'] == 10:
        update.message.reply_text('Track ID Tidak ditemukan',
                                  reply_markup=ReplyKeyboardMarkup([['⬅️ Kembali']], one_time_keyboard=True,
                                                                   resize_keyboard=True))
        return ConversationHandler.END
    else:
        real_data = json_['data']
        data['Track ID'] = real_data['track_id']
        data['K-Contact'] = json_['data']['detail'][0]['x3']
        data['No. SC'] = real_data['scid']
        data['Tanggal Order'] = real_data['orderDate']
        data['Status'] = real_data['status_name']
        data['Nama Customer'] = real_data['user_name']
        data['Paket'] = real_data['name']
        data['Alamat Instalasi'] = json_['data']['address']['address']
        data['STO'] = json_['data']['data1']['sto']

        update.message.reply_text(
            "🔍 <b>Cek Track ID</b>\n"
            "{}".format(bot_main.array_to_str(data)), parse_mode=ParseMode.HTML,
            reply_markup=ReplyKeyboardMarkup([['⬅️ Kembali']], one_time_keyboard=True, resize_keyboard=True))
        return ConversationHandler.END


def cek_order(bot, update):
    db_data = {}
    push = {}
    date_check = 'A'
    text = update.message.text
    user = update.message.from_user
    user_id = get_id(user.id)
    if text == "⬅️ Kembali":
        return bot_main.start(bot, update, db_data)

    status_id = model.get_status_id(text)
    order_data = model.get_order(user_id, status_id)
    records = order_data.fetchall()
    if order_data.rowcount > 0:
        for row in records:
            db_data['TRACK_ID'] = row[5]
            db_data['ORDER_DATE'] = row[6]
            db_data['CUSTOMER_NAME'] = row[24]
            db_data['KCONTACT'] = row[8]
            db_data['ADDRESS_INSTALLATION'] = row[29]
            db_data['PACKAGE'] = row[30]
            db_data['CUSTOMER_PHONE'] = row[25]
            db_data['STO'] = row[3]
            db_data['DATE'] = row[11]
            date_check = 'B'
            if text == 'Not FU':
                date_check = 'C'
                update.message.reply_text(
                    "📋 <b>List Order</b>\n"
                    "{}".format(bot_main.array_to_str(db_data)),
                    parse_mode=ParseMode.HTML, reply_markup=ReplyKeyboardMarkup([['⬅️ Kembali']],
                                                                                one_time_keyboard=True,
                                                                                resize_keyboard=True))
            elif text == 'Kendala Pelanggan':
                    date_check = 'C'
                    push['TRACK_ID'] = row[5]
                    push['SC'] = row[31]
                    push['KENDALA'] = row[37]
                    push['DETIL KENDALA'] = row[9]
                    push['TECHNICIAN_NAME'] = get_teknisi(row[12])
                    push['CUSTOMER_NAME'] = row[24]
                    push['CUSTOMER_PHONE'] = row[25]
                    push['ADDRESS_INSTALLATION'] = row[29]
                    update.message.reply_text(
                        "📋 <b>List Order</b>\n"
                        "{}".format(bot_main.array_to_str(push)),
                        parse_mode=ParseMode.HTML, reply_markup=ReplyKeyboardMarkup([['⬅️ Kembali']],
                                                                                    one_time_keyboard=True,
                                                                                    resize_keyboard=True))
            elif text == 'Kendala Teknis':
                    date_check = 'C'
                    push['TRACK_ID'] = row[5]
                    push['SC'] = row[31]
                    push['KENDALA'] = row[37]
                    push['DETIL KENDALA'] = row[9]
                    push['TECHNICIAN_NAME'] = get_teknisi(row[12])
                    push['CUSTOMER_NAME'] = row[24]
                    push['CUSTOMER_PHONE'] = row[25]
                    push['ADDRESS_INSTALLATION'] = row[29]
                    update.message.reply_text(
                        "📋 <b>List Order</b>\n"
                        "{}".format(bot_main.array_to_str(push)),
                        parse_mode=ParseMode.HTML, reply_markup=ReplyKeyboardMarkup([['⬅️ Kembali']],
                                                                                    one_time_keyboard=True,
                                                                                    resize_keyboard=True))
            elif text == 'Assign Teknisi':
                date_check = 'C'
                push['TRACK_ID'] = row[5]
                push['SC'] = row[31]
                push['TECHNICIAN_NAME'] = get_teknisi(row[12])
                push['CUSTOMER_NAME'] = row[24]
                push['CUSTOMER_PHONE'] = row[25]
                push['ADDRESS_INSTALLATION'] = row[29]
                update.message.reply_text(
                    "📋 <b>List Order</b>\n"
                    "{}".format(bot_main.array_to_str(push)),
                    parse_mode=ParseMode.HTML, reply_markup=ReplyKeyboardMarkup([['⬅️ Kembali']],
                                                                                one_time_keyboard=True,
                                                                                resize_keyboard=True))
            elif text == 'Push PI':
                date_check = 'C'
                push['TRACK_ID'] = row[5]
                push['SC'] = row[31]
                push['TECHNICIAN_NAME'] = get_teknisi(row[12])
                push['CUSTOMER_NAME'] = row[24]
                push['CUSTOMER_PHONE'] = row[25]
                push['ADDRESS_INSTALLATION'] = row[29]
                update.message.reply_text(
                    "📋 <b>List Order</b>\n"
                    "{}".format(bot_main.array_to_str(push)),
                    parse_mode=ParseMode.HTML, reply_markup=ReplyKeyboardMarkup([['⬅️ Kembali']],
                                                                                one_time_keyboard=True,
                                                                                resize_keyboard=True))
            elif text == 'PI':
                    date_check = 'C'
                    push['TRACK_ID'] = row[5]
                    push['SC'] = row[31]
                    push['TECHNICIAN_NAME'] = get_teknisi(row[12])
                    push['CUSTOMER_NAME'] = row[24]
                    push['CUSTOMER_PHONE'] = row[25]
                    push['ADDRESS_INSTALLATION'] = row[29]
                    update.message.reply_text(
                        "📋 <b>List Order</b>\n"
                        "{}".format(bot_main.array_to_str(push)),
                        parse_mode=ParseMode.HTML, reply_markup=ReplyKeyboardMarkup([['⬅️ Kembali']],
                                                                                    one_time_keyboard=True,
                                                                                    resize_keyboard=True))
            else:
                update.message.reply_text("Data SCBE tidak ditemukan",
                                          reply_markup=ReplyKeyboardMarkup([['⬅️ Kembali']], one_time_keyboard=True,
                                                                           resize_keyboard=True))
                bot_main.db.commit()
                return ConversationHandler.END
        if date_check == 'B':
            update.message.reply_text("Data Order tidak ditemukan",
                                      reply_markup=ReplyKeyboardMarkup([['⬅️ Kembali']], one_time_keyboard=True,
                                                                       resize_keyboard=True))
            bot_main.db.commit()
            return ConversationHandler.END

        bot_main.db.commit()
        return bot_main.GET_MYIR_WO
    else:
        update.message.reply_text("Data Order tidak ditemukan",
                                  reply_markup=ReplyKeyboardMarkup([['⬅️ Kembali']], one_time_keyboard=True,
                                                                   resize_keyboard=True))
        bot_main.db.commit()
        return ConversationHandler.END


def cek_wo(bot, update):
    db_data = {}
    push = {}
    text = update.message.text
    user = update.message.from_user
    user_id = get_id(user.id)
    status_id = model.get_status_id(text)

    if text == "⬅️ Kembali":
        return bot_main.start(bot, update, db_data)
    wo_data = model.get_wo_teknisi(user_id, status_id)
    records = wo_data.fetchall()
    if wo_data.rowcount > 0:
        for row in records:
            db_data['TRACK_ID'] = row[18]
            db_data['ORDER_DATE'] = row[19]
            db_data['CUSTOMER_NAME'] = row[37]
            db_data['KCONTACT'] = row[21]
            db_data['ADDRESS_INSTALLATION'] = row[42]
            db_data['PACKAGE'] = row[43]
            db_data['CUSTOMER_PHONE'] = row[38]
            db_data['STO'] = row[52]
            if text == 'Assign Teknisi':
                keyboard = [[InlineKeyboardButton("UPDATE", callback_data=db_data['TRACK_ID'])]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                update.message.reply_text('📋 <b>List WO</b>\n'
                                          "{}".format(bot_main.array_to_str(db_data)),
                                          parse_mode=ParseMode.HTML,
                                          reply_markup=reply_markup)
            else:
                push['TRACK_ID'] = row[18]
                push['SC'] = row[44]
                push['STATUS'] = row[54]
                push['TECHNICIAN_NAME'] = get_teknisi(row[25])
                push['CUSTOMER_NAME'] = row[37]
                push['CUSTOMER_PHONE'] = row[38]
                push['ADDRESS_INSTALLATION'] = row[42]
                update.message.reply_text('📋 <b>List WO</b>\n'
                                          "{}".format(bot_main.array_to_str(push)),
                                          parse_mode=ParseMode.HTML,
                                          reply_markup=ReplyKeyboardMarkup([['⬅️ Kembali']], one_time_keyboard=True,
                                                                           resize_keyboard=True))
        if text == 'Assign Teknisi':
            update.message.reply_text("📋 *List WO*\n\n Silahkan Pilih WO yang akan di update",
                                      parse_mode=ParseMode.MARKDOWN,
                                      reply_markup=ReplyKeyboardMarkup([['⬅️ Kembali']], one_time_keyboard=True,
                                                                       resize_keyboard=True))
    else:
        update.message.reply_text("Data Work Order tidak ditemukan",
                                  reply_markup=ReplyKeyboardMarkup([['⬅️ Kembali']], one_time_keyboard=True,
                                                                   resize_keyboard=True))
        bot_main.db.commit()
        return ConversationHandler.END
    bot_main.db.commit()
    return bot_main.PUSH_MAIN


def cek_scbe(bot, update):
    db_data = {}
    push = {}
    date_check = 'A'
    text = update.message.text
    user = update.message.from_user
    user_id = get_id(user.id)
    if text == "⬅️ Kembali":
        return bot_main.start(bot, update, db_data)

    status_id = model.get_status_id(text)
    scbe_data = model.get_scbe(user_id, status_id)
    records = scbe_data.fetchall()
    if scbe_data.rowcount > 0:
        for row in records:
            db_data['TRACK_ID'] = row[25]
            db_data['ORDER_DATE'] = row[26]
            db_data['CUSTOMER_NAME'] = row[44]
            db_data['KCONTACT'] = row[28]
            db_data['ADDRESS_INSTALLATION'] = row[49]
            db_data['PACKAGE'] = row[50]
            db_data['CUSTOMER_PHONE'] = row[45]
            db_data['STO'] = row[23]
            db_data['DATE'] = row[31]
            date_check = 'B'
            if text == 'Not FU':
                date_check = 'C'
                keyboard = [[InlineKeyboardButton("ASSIGN WO", callback_data=db_data['TRACK_ID'])]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                update.message.reply_text(
                    "🌐 <b>SCBE</b>\n"
                    "{}".format(bot_main.array_to_str(db_data)),
                    parse_mode=ParseMode.HTML, reply_markup=reply_markup)
            elif text == 'Kendala Pelanggan':
                if nowtime < db_data['DATE']:
                    date_check = 'C'
                    push['TRACK_ID'] = row[25]
                    push['SC'] = row[51]
                    push['KENDALA'] = row[57]
                    push['DETIL KENDALA'] = row[29]
                    push['TECHNICIAN_NAME'] = get_teknisi(row[32])
                    push['CUSTOMER_NAME'] = row[44]
                    push['CUSTOMER_PHONE'] = row[45]
                    push['ADDRESS_INSTALLATION'] = row[49]
                    update.message.reply_text(
                        "🌐 <b>SCBE</b>\n"
                        "{}".format(bot_main.array_to_str(push)),
                        parse_mode=ParseMode.HTML, reply_markup=ReplyKeyboardMarkup([['⬅️ Kembali']],
                                                                                    one_time_keyboard=True,
                                                                                    resize_keyboard=True))
            elif text == 'Kendala Teknis':
                if nowtime < db_data['DATE']:
                    date_check = 'C'
                    push['TRACK_ID'] = row[25]
                    push['SC'] = row[51]
                    push['KENDALA'] = row[57]
                    push['DETIL KENDALA'] = row[29]
                    push['TECHNICIAN_NAME'] = get_teknisi(row[32])
                    push['CUSTOMER_NAME'] = row[44]
                    push['CUSTOMER_PHONE'] = row[45]
                    push['ADDRESS_INSTALLATION'] = row[49]
                    update.message.reply_text(
                        "🌐 <b>SCBE</b>\n"
                        "{}".format(bot_main.array_to_str(push)),
                        parse_mode=ParseMode.HTML, reply_markup=ReplyKeyboardMarkup([['⬅️ Kembali']],
                                                                                    one_time_keyboard=True,
                                                                                    resize_keyboard=True))
            elif text == 'Assign Teknisi':
                date_check = 'C'
                push['TRACK_ID'] = row[25]
                push['SC'] = row[51]
                push['TECHNICIAN_NAME'] = get_teknisi(row[32])
                push['CUSTOMER_NAME'] = row[44]
                push['CUSTOMER_PHONE'] = row[45]
                push['ADDRESS_INSTALLATION'] = row[49]
                update.message.reply_text(
                    "🌐 <b>SCBE</b>\n"
                    "{}".format(bot_main.array_to_str(push)),
                    parse_mode=ParseMode.HTML, reply_markup=ReplyKeyboardMarkup([['⬅️ Kembali']],
                                                                                one_time_keyboard=True,
                                                                                resize_keyboard=True))
            elif text == 'Push PI':
                date_check = 'C'
                push['TRACK_ID'] = row[25]
                push['SC'] = row[51]
                push['TECHNICIAN_NAME'] = get_teknisi(row[32])
                push['CUSTOMER_NAME'] = row[44]
                push['CUSTOMER_PHONE'] = row[45]
                push['ADDRESS_INSTALLATION'] = row[49]
                update.message.reply_text(
                    "🌐 <b>SCBE</b>\n"
                    "{}".format(bot_main.array_to_str(push)),
                    parse_mode=ParseMode.HTML, reply_markup=ReplyKeyboardMarkup([['⬅️ Kembali']],
                                                                                one_time_keyboard=True,
                                                                                resize_keyboard=True))
            elif text == 'PI':
                if nowtime < db_data['DATE']:
                    date_check = 'C'
                    push['TRACK_ID'] = row[25]
                    push['SC'] = row[51]
                    push['TECHNICIAN_NAME'] = get_teknisi(row[32])
                    push['CUSTOMER_NAME'] = row[44]
                    push['CUSTOMER_PHONE'] = row[45]
                    push['ADDRESS_INSTALLATION'] = row[49]
                    update.message.reply_text(
                        "🌐 <b>SCBE</b>\n"
                        "{}".format(bot_main.array_to_str(push)),
                        parse_mode=ParseMode.HTML, reply_markup=ReplyKeyboardMarkup([['⬅️ Kembali']],
                                                                                    one_time_keyboard=True,
                                                                                    resize_keyboard=True))
            else:
                update.message.reply_text("Data SCBE tidak ditemukan",
                                          reply_markup=ReplyKeyboardMarkup([['⬅️ Kembali']], one_time_keyboard=True,
                                                                           resize_keyboard=True))
                bot_main.db.commit()
                return ConversationHandler.END
        if text == 'Not FU':
            update.message.reply_text("🌐 *SCBE*\n\n Silahkan Pilih WO yang akan di assign",
                                      parse_mode=ParseMode.MARKDOWN,
                                      reply_markup=ReplyKeyboardMarkup([['⬅️ Kembali']], one_time_keyboard=True,
                                                                       resize_keyboard=True))
        elif date_check == 'B':
            update.message.reply_text("Data SCBE tidak ditemukan",
                                      reply_markup=ReplyKeyboardMarkup([['⬅️ Kembali']], one_time_keyboard=True,
                                                                       resize_keyboard=True))
            bot_main.db.commit()
            return ConversationHandler.END

        bot_main.db.commit()
        return bot_main.GET_MYIR_WO
    else:
        update.message.reply_text("Data SCBE tidak ditemukan",
                                  reply_markup=ReplyKeyboardMarkup([['⬅️ Kembali']], one_time_keyboard=True,
                                                                   resize_keyboard=True))
        bot_main.db.commit()
        return ConversationHandler.END


def get_myir_wo(bot, update, user_data):
    reply_keyboard = []
    query = update.callback_query
    user_data['assigned_myir'] = query.data
    tl_id = get_id(user_data['chat_id'])

    sql = "SELECT * FROM ezpro_user A " \
          "JOIN ezpro_user_sto B ON A.id = B.customuser_id " \
          "WHERE user_role_id = '3' AND B.sto_id IN ( " \
          "  SELECT sto_id FROM ezpro_user A " \
          "  JOIN ezpro_user_sto B ON A.id = B.customuser_id " \
          "  WHERE A.id = '%s' " \
          ")" % tl_id
    cursor = bot_main.db.query(sql)
    records = cursor.fetchall()
    records = [item[7] for item in records]
    bot_main.db.commit()
    if cursor.rowcount > 0:
        reply_keyboard = [records[i:i + 3] for i in range(0, len(records), 3)]
        reply_keyboard.append(['⬅️ Kembali'])
    bot.send_message(text="Pilih Teknisi yang akan di assign \n"
                          "Track ID : {}".format(user_data['assigned_myir']),
                     chat_id=query.message.chat_id, reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                                                     one_time_keyboard=True,
                                                                                     resize_keyboard=True))
    return bot_main.ASSIGN_WO


def assign_second_teknisi(bot, update, user_data):
    text = update.message.text

    sql = "SELECT * FROM ezpro_user WHERE username = '%s' " % text
    cursor = bot_main.db.query(sql)
    records = cursor.fetchall()
    bot_main.db.commit()

    if cursor.rowcount > 0:
        for row in records:
            user_data['first_technician_id'] = row[0]
            user_data['first_technician_name'] = row[7]
            user_data['first_technician_tele'] = row[8]

    sql = "SELECT * FROM ezpro_scbe WHERE track_id = '%s' " % user_data['assigned_myir']
    cursor = bot_main.db.query(sql)
    records = cursor.fetchall()
    bot_main.db.commit()

    if cursor.rowcount > 0:
        for row in records:
            user_data['scbe_id'] = row[0]

    update.message.reply_text("Masukkan NIK Teknisi Kedua \n"
                              "Track ID : {}\n"
                              "Teknisi : {}".format(user_data['assigned_myir'], user_data['first_technician_name']))
    return bot_main.ASSIGN_WO


def assign_wo(bot, update, user_data):
    text = update.message.text
    if text == "⬅️ Kembali":
        return bot_main.start(bot, update, user_data)
    sql = "SELECT * FROM ezpro_user WHERE name = '%s'" % text
    cursor = bot_main.db.query(sql)
    records = cursor.fetchall()
    bot_main.db.commit()

    if cursor.rowcount > 0:
        for row in records:
            user_data['first_technician_id'] = row[0]
            user_data['first_technician_name'] = row[7]
            user_data['first_technician_tele'] = row[8]

    sql = "SELECT * FROM ezpro_scbe WHERE track_id = '%s' " % user_data['assigned_myir']
    cursor = bot_main.db.query(sql)
    records = cursor.fetchall()
    bot_main.db.commit()

    if cursor.rowcount > 0:
        for row in records:
            user_data['scbe_id'] = row[0]

    placeholders = "id = '%s'" % (user_data['scbe_id'])
    columns = "status_id = '%s', first_technician_id = '%s'" % \
              (2, user_data['first_technician_id'])
    table = 'ezpro_scbe'
    sql = "UPDATE %s SET %s WHERE %s" % (table, columns, placeholders)
    bot_main.db.query(sql)
    bot_main.db.commit()

    update.message.reply_text("WO Dengan data : \n"
                              "Track ID : {}\n"
                              "Teknisi : {} \n"
                              "Telah di assign ke teknisi."
                              .format(user_data['assigned_myir'], user_data['first_technician_name']),
                              reply_markup=ReplyKeyboardMarkup([['⬅️ Kembali']], one_time_keyboard=True,
                                                               resize_keyboard=True))

    msg = "Anda mendapat WO :\n" \
          "Track ID : %s\n" \
          "Silahkan masuk ke menu List WO untuk melihat detil WO" % user_data['assigned_myir']
    bot_main.send_message(bot, msg, user_data['first_technician_tele'])
    return ConversationHandler.END

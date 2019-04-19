#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Simple Bot to reply to Telegram messages
# This program is dedicated to the public domain under the CC0 license.
"""
This Bot uses the Updater class to handle the bot.
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, ParseMode)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler, CallbackQueryHandler)
from zeep import Client

import bot_register
import bot_data
import db_connect
import logging
import model

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Database Init
db = db_connect.DB()

REGISTER_TA, REGISTER_MITRA, REGISTER_TELKOM, REGISTER_SALES, APPROVE_TA, APPROVE_MITRA, \
APPROVE_TELKOM, APPROVE_SALES, REGISTER, PHOTO, LOCATION, BIO, MAIN_MENU, CEK_SC, \
CEK_TRACKID, CEK_SCBE, CEK_ORDER, PUSH_MAIN, PUSH_PI, RESULT_PUSH, \
PUSH_DECISION, PUSH_PI_ODP, PUSH_PI_LOCATION, PUSH_PI_CONFIRMATION, \
KENDALA, TIPE_KENDALA, DETIL_KENDALA, GET_MYIR_WO, ASSIGN_WO, ASSIGN_TEKNISI, \
ASSIGN_SECOND_TEKNISI, KEMBALI, LOCATION_KENDALA, CEK_WO, CEK_WO_TL = range(35)

reply_keyboard_user = [['📋 List Work Order'], ['🔍 Cek TrackID', '🔍 Cek SC']]
reply_keyboard_tl = [['🌐 List SCBE'], ['🔍 Cek TrackID', '🔍 Cek SC']]
reply_keyboard_sales = [['📋 List Order'], ['🔍 Cek TrackID', '🔍 Cek SC']]


def array_to_str(user_data):
    facts = list()
    for key, value in user_data.items():
        if key != 'chat_id':
            facts.append("{} : <code>{}</code>".format(key, value))

    return "\n".join(facts).join(['\n', '\n'])


def send_message(bot, text, chat_id):
    bot.send_message(text=text,
                     chat_id=chat_id)


def update_db(placeholders, columns, table):
    sql = "UPDATE %s SET %s WHERE %s" % (table, columns, placeholders)
    db.query(sql)
    db.commit()


def select_db(query):
    sql = query
    cursor = db.query(sql)
    records = cursor.fetchall()
    db.commit()
    if cursor.rowcount > 0:
        return records


def unavailable(bot, update, user_data):
    reply_keyboard_registered = [['⬅️ Kembali']]
    update.message.reply_text('⚠️ *Error*\n\n'
                              'Mohon maaf, perintah tidak dikenali\n'
                              'Silahkan ulangi request', parse_mode=ParseMode.MARKDOWN,
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard_registered, one_time_keyboard=True,
                                                               resize_keyboard=True))
    return start(bot, update, user_data)


def start(bot, update, user_data):
    cancel(bot, update)
    user_data.clear()
    db_data = {}
    reply_keyboard = [['Teknisi TA', 'Teknisi Mitra'], ['Telkom', 'Sales']]
    user = update.message.from_user
    user_data['username'] = user.first_name
    user_data['chat_id'] = user.id

    sql = "SELECT * FROM ezpro_user WHERE chat_id = '%s'" % user.id
    cursor = db.query(sql)
    records = cursor.fetchall()
    db.commit()

    if cursor.rowcount > 0:
        for row in records:
            db_data['user_role'] = row[15]
        if db_data['user_role'] == 4:
            user_data['role'] = 'TL'
            update.message.reply_text(
                '⚙️ *Main Menu*\n\nSilahkan pilih menu yang tersedia.\n',
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=ReplyKeyboardMarkup(reply_keyboard_tl, one_time_keyboard=True, resize_keyboard=True))
            print('LOGIN AS TL - ', user_data['username'])
        elif db_data['user_role'] == 2:
            user_data['role'] = 'SALES'
            update.message.reply_text(
                '⚙️ *Main Menu*\n\nSilahkan pilih menu yang tersedia.\n',
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=ReplyKeyboardMarkup(reply_keyboard_sales, one_time_keyboard=True, resize_keyboard=True))
            print('LOGIN AS SALES - ', user_data['username'])
        else:
            user_data['role'] = 'USER'
            update.message.reply_text(
                '⚙️ *Main Menu*\n\nSilahkan pilih menu yang tersedia.\n',
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=ReplyKeyboardMarkup(reply_keyboard_user, one_time_keyboard=True, resize_keyboard=True))
            print('LOGIN AS USER - ', user_data['username'])
        return MAIN_MENU
    else:
        update.message.reply_text(
            'Akun Telegram anda belum terdaftar.\n'
            'Silahkan pilih Unit anda',
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))
        return REGISTER


def main_menu(bot, update, user_data):
    text = update.message.text
    reply_keyboard = [['Not FU', 'Assign Teknisi'], ['Push PI', 'Kendala Teknis'], ['Kendala Pelanggan', 'PI'],
                      ['⬅️ Kembali']]
    wo_keyboard = [['Assign Teknisi', 'Push PI'], ['PI', '⬅️ Kembali']]
    kembali_keyboard = [['⬅️ Kembali']]

    if text == "📋 List Work Order":
        update.message.reply_text('📋 *List WO*\n\nSilahkan Pilih Status WO',
                                  parse_mode=ParseMode.MARKDOWN,
                                  reply_markup=ReplyKeyboardMarkup(wo_keyboard, one_time_keyboard=True,
                                                                   resize_keyboard=True))
        print('List Work Order - ', user_data['username'])
        if user_data['role'] == 'USER':
            return CEK_WO
        elif user_data['role'] == 'TL':
            return CEK_WO_TL

    elif text == "🌐 List SCBE":
        update.message.reply_text('🌐 *SCBE*\n\nSilahkan Pilih Status SCBE',
                                  parse_mode=ParseMode.MARKDOWN,
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True,
                                                                   resize_keyboard=True))
        print('List SCBE - ', user_data['username'])
        return CEK_SCBE

    elif text == "📋 List Order":
        update.message.reply_text('📋 *List Order*\n\nSilahkan Pilih Status Order',
                                  parse_mode=ParseMode.MARKDOWN,
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True,
                                                                   resize_keyboard=True))
        print('List SCBE - ', user_data['username'])
        return CEK_ORDER

    elif text == "Push PI":
        update.message.reply_text('Silahkan Input Track ID yang akan di Push',
                                  reply_markup=ReplyKeyboardMarkup(kembali_keyboard, one_time_keyboard=True,
                                                                   resize_keyboard=True))
        print('Push PI - ', user_data['username'])
        return PUSH_MAIN

    elif text == "🔍 Cek TrackID":
        update.message.reply_text('🔍 *Cek Track ID*\n\nSilahkan Input Track ID yang akan di cek',
                                  parse_mode=ParseMode.MARKDOWN,
                                  reply_markup=ReplyKeyboardMarkup(kembali_keyboard, one_time_keyboard=True,
                                                                   resize_keyboard=True))
        print('Cek Track ID - ', user_data['username'])
        return CEK_TRACKID

    elif text == "🔍 Cek SC":
        update.message.reply_text('🔍 *Cek SC*\n\nSilahkan Input No. SC yang akan di cek',
                                  parse_mode=ParseMode.MARKDOWN,
                                  reply_markup=ReplyKeyboardMarkup(kembali_keyboard, one_time_keyboard=True,
                                                                   resize_keyboard=True))
        print('Cek SC - ', user_data['username'])
        return CEK_SC


def push_main(bot, update, user_data):
    reply_keyboard = [['Push', 'Kendala']]
    query = update.callback_query
    text = query.data
    user_data['myir'] = text
    if text == "⬅️ Kembali":
        return start(bot, update, user_data)
    bot.send_message(text="✉️ *Update WO*\n\nSilahkan pilih tipe laporan", parse_mode=ParseMode.MARKDOWN,
                     chat_id=query.message.chat_id, reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                                                     one_time_keyboard=True,
                                                                                     resize_keyboard=True))
    # update.message.reply_text(
    #     "✉️ *Update WO*\n\nSilahkan pilih tipe laporan",
    #     parse_mode=ParseMode.MARKDOWN, reply_markup=ReplyKeyboardMarkup(reply_keyboard,
    #                                                                     one_time_keyboard=True, resize_keyboard=True))
    return PUSH_DECISION


def push_decision(bot, update, user_data):
    reply_keyboard = [['Kendala Pelanggan', 'Kendala Teknis'], ['⬅️ Kembali']]
    text = update.message.text
    user_data['Decision'] = text
    if text == 'Push':
        update.message.reply_text("✉️ *Update WO*\n\nSilahkan masukkan nama ODP Real\n"
                                  "Contoh Format Penulisan ODP : \n"
                                  "ODP-XXX-XX/00\n"
                                  "Jika tidak ada nama ODP\n"
                                  "Ketik NO LABEL atau TANPA TUTUP", parse_mode=ParseMode.MARKDOWN)
        return PUSH_PI_LOCATION
    elif text == 'Kendala':
        update.message.reply_text("Silahkan pilih kendala",
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True,
                                                                   resize_keyboard=True))
        return KENDALA
    else:
        print('END')
        return ConversationHandler.END


def push_pi_odp(bot, update, user_data):
    text = update.message.text
    user_data['Mboh'] = text
    update.message.reply_text("Silahkan masukkan nama ODP Real\n"
                              "Contoh Format Penulisan ODP : \n"
                              "ODP-XXX-XX/00\n"
                              "Jika tidak ada nama ODP\n"
                              "Ketik NO LABEL atau TANPA TUTUP")
    return PUSH_PI_LOCATION


def push_pi_location(bot, update, user_data):
    text = update.message.text
    user_data['ODP REAL'] = text
    update.message.reply_text("Silahkan kirim tagging lokasi rumah pelanggan")
    return PUSH_PI_CONFIRMATION


def confirm_push_pi(bot, update, user_data):
    reply_keyboard = [['Ya', 'Tidak']]
    user_location = update.message.location
    user_data['Latitude'] = user_location.latitude
    user_data['Longitude'] = user_location.longitude
    update.message.reply_text(
        "Apakah data ini sudah benar ?"
        "{}".format(array_to_str(user_data)), parse_mode=ParseMode.HTML,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))
    return PUSH_PI


def push_pi(bot, update, user_data):
    db_data = {}
    nama_teknisi = ""
    nama_tl = ""
    text = update.message.text
    if text == 'Ya':
        select = "SELECT * FROM ezpro_scbe A " \
                 "LEFT JOIN ezpro_user_sto B ON A.sto_id = B.sto_id " \
                 "LEFT JOIN ezpro_user C ON B.customuser_id = C.id " \
                 "WHERE A.track_id = '%s' AND C.user_role_id = '4'" % user_data['myir']
        cursor = db.query(select)
        records = cursor.fetchall()
        db.commit()
        if cursor.rowcount > 0:
            for row in records:
                db_data['user_id'] = row[0]
                db_data['service_id'] = row[12]
                nama_teknisi = model.get_teknisi(row[8])
                nama_tl = row[29]
                db_data['chat_id_tl'] = row[30]

        placeholders = "id = '%s'" % db_data['user_id']
        columns = "status_id = '%s', category_result_id = '%s'" % (3, 1)
        table = 'ezpro_scbe'
        update_db(placeholders, columns, table)

        placeholders_service = "id = '%s'" % db_data['service_id']
        columns_service = "odp_real = '%s', customer_latitude = '%s', customer_longitude = '%s'" % \
                          (user_data['ODP REAL'], user_data['Latitude'], user_data['Longitude'])
        table_service = 'ezpro_service'
        update_db(placeholders_service, columns_service, table_service)

        update.message.reply_text('Terimakasih, Data akan segera kami proses',
                                  reply_markup=ReplyKeyboardMarkup([['⬅️ Kembali']], one_time_keyboard=True,
                                                                   resize_keyboard=True))

        msg = "PUSH PI\n\n" \
              "Track ID : %s\n" \
              "Teknisi : %s\n" \
              "Telah di Push Teknisi" % (user_data['myir'], nama_teknisi)
        send_message(bot, msg, db_data['chat_id_tl'])

        msg = "Anda mendapat WO :\n" \
              "Track ID : %s\n" \
              "TL : %s\n" \
              "Teknisi : %s\n" \
              "Silahkan masuk ke menu List WO untuk melihat detil WO" % (user_data['myir'], nama_tl, nama_teknisi)
        send_message(bot, msg, '109891020')
        send_message(bot, msg, '94075377')
        send_message(bot, msg, '67974274')

        return ConversationHandler.END
    if text == 'Tidak':
        update.message.reply_text("Terimakasih",
                                  reply_markup=ReplyKeyboardMarkup([['⬅️ Kembali']], one_time_keyboard=True,
                                                                   resize_keyboard=True))
        return ConversationHandler.END


def kendala(bot, update, user_data):
    text = update.message.text
    user_data['kendala'] = text
    if text == 'Kendala Pelanggan':
        reply_keyboard = [['Manja', 'ATK/RNA', 'Pelanggan Menolak']]
        update.message.reply_text("Pilih jenis kendala",
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True,
                                                                   resize_keyboard=True))
        return TIPE_KENDALA
    elif text == 'Kendala Teknis':
        reply_keyboard = [['Tidak ada jaringan', 'ODP Penuh', 'ODP Salah STO'],
                          ['Tambah Tiang', 'Tarikan Jauh', 'Izin Penarikan'], ['Double Input']]
        update.message.reply_text("Pilih jenis kendala",
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True,
                                                                   resize_keyboard=True))
        return TIPE_KENDALA


def tipe_kendala(bot, update, user_data):
    text = update.message.text
    user_data['tipe_kendala'] = text
    update.message.reply_text("Silahkan kirim tagging lokasi rumah pelanggan")
    return LOCATION_KENDALA


def location_kendala(bot, update, user_data):
    user_location = update.message.location
    user_data['Latitude'] = user_location.latitude
    user_data['Longitude'] = user_location.longitude
    update.message.reply_text("Silahkan ketik detil kendala")
    return DETIL_KENDALA


def detil_kendala(bot, update, user_data):
    text = update.message.text
    status_id = model.get_status_id(user_data['kendala'])
    category_result_id = model.get_category_id(user_data['tipe_kendala'])
    user_data['detil_kendala'] = text
    db_data = {}

    select = "SELECT * FROM ezpro_scbe A " \
             "LEFT JOIN ezpro_user_sto B ON A.sto_id = B.sto_id " \
             "LEFT JOIN ezpro_user C ON B.customuser_id = C.id " \
             "WHERE A.track_id = '%s' AND C.user_role_id = '4'" % user_data['myir']
    cursor = db.query(select)
    records = cursor.fetchall()
    db.commit()
    if cursor.rowcount > 0:
        for row in records:
            db_data['user_id'] = row[0]
            db_data['service_id'] = row[12]
            db_data['chat_id_tl'] = row[30]

    placeholders = "id = '%s'" % db_data['user_id']
    columns = "status_id = '%s', category_result_id = '%s', detail_result = '%s'" % \
              (status_id, category_result_id, user_data['detil_kendala'])
    table = 'ezpro_scbe'
    update_db(placeholders, columns, table)

    placeholders_service = "id = '%s'" % db_data['service_id']
    columns_service = "customer_latitude = '%s', customer_longitude = '%s'" % \
                      (user_data['Latitude'], user_data['Longitude'])
    table_service = 'ezpro_service'
    update_db(placeholders_service, columns_service, table_service)

    msg = "Kendala WO :\n" \
          "Track ID : %s\n" \
          "Tipe Kendala : %s\n" \
          "Silahkan masuk ke menu List SCBE untuk melihat Detil Kendala" % (
              user_data['myir'], user_data['tipe_kendala'])
    send_message(bot, msg, db_data['chat_id_tl'])

    update.message.reply_text(
        "Terimakasih, data akan segera kami verifikasi"
        "{}".format(array_to_str(user_data)), parse_mode=ParseMode.HTML,
        reply_markup=ReplyKeyboardMarkup([['⬅️ Kembali']], one_time_keyboard=True, resize_keyboard=True))
    return ConversationHandler.END


def cancel(bot, update):
    return ConversationHandler.END


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater("684315307:AAET1HUSKfgf4BxZconvh_-F_QDQhOiCh7Q")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start, pass_user_data=True),
                      RegexHandler('^(⬅️ Kembali)$', start, pass_user_data=True)],

        states={
            MAIN_MENU: [RegexHandler('^(📋 List Work Order|📋 List Order|🌐 List SCBE|Push PI|🔍 Cek TrackID|🔍 Cek SC)$',
                                     main_menu, pass_user_data=True)],

            CEK_SC: [MessageHandler(Filters.text, bot_data.cek_sc)],

            CEK_TRACKID: [MessageHandler(Filters.text, bot_data.cek_myir)],

            CEK_ORDER: [MessageHandler(Filters.text, bot_data.cek_order)],

            CEK_WO: [MessageHandler(Filters.text, bot_data.cek_wo)],

            CEK_WO_TL: [MessageHandler(Filters.text, bot_data.cek_wo)],

            CEK_SCBE: [RegexHandler('^(Not FU|Assign Teknisi|Push PI|Kendala Teknis|Kendala Pelanggan|PI)$',
                                    bot_data.cek_scbe)],

            GET_MYIR_WO: [CallbackQueryHandler(bot_data.get_myir_wo, pass_user_data=True)],

            ASSIGN_SECOND_TEKNISI: [MessageHandler(Filters.text, bot_data.assign_second_teknisi, pass_user_data=True)],

            ASSIGN_WO: [MessageHandler(Filters.text, bot_data.assign_wo, pass_user_data=True)],

            PUSH_MAIN: [CallbackQueryHandler(push_main, pass_user_data=True)],

            PUSH_DECISION: [RegexHandler('^(Push|Kendala)$', push_decision, pass_user_data=True)],

            PUSH_PI_ODP: [MessageHandler(Filters.text, push_pi_odp, pass_user_data=True)],

            PUSH_PI_LOCATION:
                [RegexHandler(
                    '^((ODP|OTB|GCL)-\D{3}-((\D{2,4}|\d{2,3}|\D\d{2,3})\/\d{1,3}|\d{2,3})|NO LABEL|TANPA TUTUP)$'
                    , push_pi_location, pass_user_data=True)],

            PUSH_PI_CONFIRMATION: [MessageHandler(Filters.location, confirm_push_pi, pass_user_data=True)],

            PUSH_PI: [MessageHandler(Filters.text, push_pi, pass_user_data=True)],

            KENDALA: [MessageHandler(Filters.text, kendala, pass_user_data=True)],

            TIPE_KENDALA: [MessageHandler(Filters.text, tipe_kendala, pass_user_data=True)],

            LOCATION_KENDALA: [MessageHandler(Filters.location, location_kendala, pass_user_data=True)],

            DETIL_KENDALA: [MessageHandler(Filters.text, detil_kendala, pass_user_data=True)],

            REGISTER:
                [RegexHandler('^(Teknisi TA|Teknisi Mitra|Telkom|Sales)$', bot_register.register, pass_user_data=True)],

            REGISTER_TA: [MessageHandler(Filters.text, bot_register.register_teknisi_ta, pass_user_data=True)],

            REGISTER_MITRA: [MessageHandler(Filters.text, bot_register.register_teknisi_mitra, pass_user_data=True)],

            REGISTER_TELKOM: [MessageHandler(Filters.text, bot_register.register_teknisi_mitra, pass_user_data=True)],

            REGISTER_SALES: [MessageHandler(Filters.text, bot_register.register_sales, pass_user_data=True)],

            APPROVE_TA: [RegexHandler('^(Ya|Tidak)$', bot_register.approve_teknisi_ta, pass_user_data=True)],

            APPROVE_TELKOM: [RegexHandler('^(Ya|Tidak)$', bot_register.approve_telkom, pass_user_data=True)],

            APPROVE_MITRA: [RegexHandler('^(Ya|Tidak)$', bot_register.approve_teknisi_mitra, pass_user_data=True)],

            APPROVE_SALES: [RegexHandler('^(Ya|Tidak)$', bot_register.approve_sales, pass_user_data=True)]
        },

        fallbacks=[CommandHandler('cancel', cancel),
                   RegexHandler('^(⬅️ Kembali)$', start, pass_user_data=True)]
    )
    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()

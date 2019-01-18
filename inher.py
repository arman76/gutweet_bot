# -*- coding: utf-8 -*-
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
import re

admin_chat_id = ''
channel_post_chat_id = ''


def text_to_HTML_parse_mode(text, entity):
    if entity.type == 'bold':
        return '<b>{}</b>'.format(text), 7
    elif entity.type == 'italic':
        return '<i>{}</i>'.format(text), 7
    elif entity.type == 'pre':
        return '<pre>{}</pre>'.format(text), 11
    elif entity.type == 'code':
        return '<code>{}</code>'.format(text), 13
    elif entity.type == 'text_link':
        return '<a href="{url}">{txt}</a>'.format(url=entity.url, txt=text), 15+len(entity.url)
    elif entity.type == 'text_mention':
        return '<a href="tg://user?id={id}">{txt}</a>'.format(id=entity.user.id, txt=text), 28+len(str(entity.user.id))


def text_with_parse_mode(text, entities):
    parse_mode = None
    extra_size = 0
    for ent in list(filter(lambda x: x.type in ['text_mention', 'pre', 'bold', 'italic', 'code', 'text_link'], entities)):
        parse_mode = 'HTML'
        beta_text, beta_extra_size = text_to_HTML_parse_mode(
            text[ent.offset + extra_size:ent.offset + ent.length + extra_size], ent)
        text = text[0:ent.offset + extra_size] + beta_text + text[ent.offset + ent.length + extra_size:]
        extra_size += beta_extra_size
    print(text)
    if not (re.search(r'^\@gutweet$', text) or re.search(r'^\@gutweet\W', text) or re.search(r'\W\@gutweet\W', text) or re.search(r'\W\@gutweet$', text)):
        text += '\n@gutweet'
    return text, parse_mode


def send_any_message(bot, chat_id, message, reply_to_message_id, reply_markup=None):
    if message.photo is not None and message.photo != []:
        text, parse_mode = text_with_parse_mode(message.caption, message.caption_entities)
        return bot.send_photo(chat_id=chat_id, photo=message.photo[-1].file_id,
                              caption=text, reply_to_message_id=reply_to_message_id,
                              reply_markup=reply_markup, parse_mode=parse_mode)
    elif message.text is not None:
        text, parse_mode = text_with_parse_mode(message.text, message.entities)
        return bot.send_message(chat_id=chat_id, text=text,
                                reply_to_message_id=reply_to_message_id,
                                reply_markup=reply_markup, parse_mode=parse_mode)
    elif message.audio is not None:
        text, parse_mode = text_with_parse_mode(message.caption, message.caption_entities)
        return bot.send_audio(chat_id=chat_id, audio=message.audio.file_id,
                              duration=message.audio.duration, performer=message.audio.performer,
                              title=message.audio.title, caption=text,
                              reply_to_message_id=reply_to_message_id, reply_markup=reply_markup, parse_mode=parse_mode)
    elif message.document is not None:
        text, parse_mode = text_with_parse_mode(message.caption, message.caption_entities)
        return bot.send_document(chat_id=chat_id, document=message.document.file_id,
                                 filename=message.document.file_name, caption=text,
                                 reply_to_message_id=reply_to_message_id, reply_markup=reply_markup, parse_mode=parse_mode)
    elif message.sticker is not None:
        return bot.send_message(chat_id=chat_id, sticker=message.sticker,
                                reply_to_message_id=reply_to_message_id, reply_markup=reply_markup)
    elif message.video is not None:
        text, parse_mode = text_with_parse_mode(message.caption, message.caption_entities)
        return bot.send_video(chat_id=chat_id, video=message.video.file_id,
                              duration=message.video.duration, caption=text,
                              reply_to_message_id=reply_to_message_id, reply_markup=reply_markup, parse_mode=parse_mode)
    elif message.video_note is not None:
        return bot.send_video_note(chat_id=chat_id, video_note=message.video_note.file_id,
                                   duration=message.video_note.duration, length=message.video_note.length,
                                   reply_to_message_id=reply_to_message_id, reply_markup=reply_markup)
    elif message.voice is not None:
        text, parse_mode = text_with_parse_mode(message.caption, message.caption_entities)
        return bot.send_voice(chat_id=chat_id, video=message.voice.file_id,
                              duration=message.voice.duration, caption=text,
                              reply_to_message_id=reply_to_message_id, reply_markup=reply_markup, parse_mode=parse_mode)
    elif message.venue is not None:
        return bot.send_venue(chat_id=chat_id, venue=message.venue,
                              foursquare_id=message.venue.foursquare_id, reply_to_message_id=reply_to_message_id,
                              reply_markup=reply_markup)
    elif message.location is not None:
        return bot.send_location(chat_id=chat_id, location=message.location,
                                 reply_to_message_id=reply_to_message_id, reply_markup=reply_markup)


def start(bot, update):
    update.message.reply_text('سلام. به ربات توییتر دانشگاه گیلانیها خوش اومدید. توییت های خودتون رو به همراه نام مستعار (در یک پیام) برای من بفرستید.')


def button(bot, update):
    print(update)
    query = update.callback_query
    if query.data[0:4] == 'user':
        print('<a href="tg://user?id={}">inline mention of a user</a>'.format(query.data[4:]))
        bot.send_message(chat_id=admin_chat_id,
                         text='<a href="tg://user?id={}">از طرف اینه!</a>'.format(query.data[4:]), parse_mode='HTML',
                         reply_to_message_id=query.message.message_id, timeout=10)
        # bot.answer_callback_query(callback_query_id=query.id, text='testtest', show_alert=False)

    if query.data == 'ye':
        reply_to_message_id = None
        if query.message.reply_to_message is not None:
            reply_to_message_id = query.message.reply_to_message.forward_from_message_id
        send_any_message(bot=bot, chat_id=channel_post_chat_id, message=query.message,
                         reply_to_message_id=reply_to_message_id)
    if query.data == 'ye' or query.data == 'no':
        bot.delete_message(chat_id=admin_chat_id, message_id=query.message.message_id)


def get_all(bot, update):
    print(update)
    global channel_post_chat_id
    global admin_chat_id
    if update.message is not None:
        if update.message.chat.type == 'private':
            if update.message.forward_from_chat is not None:
                if update.message.forward_from_chat.id == channel_post_chat_id:
                    print('cancel')
                    return
            keyboard = [[InlineKeyboardButton("اوکی 👍", callback_data='ye'),
                         InlineKeyboardButton("نوکی 👎", callback_data='no')],
                        [InlineKeyboardButton('از طرف کیه؟', callback_data='user' + str(update.message.from_user.id))]]
            markup = InlineKeyboardMarkup(keyboard)
            reply_to_message_id = None
            if update.message.reply_to_message is not None:
                if update.message.reply_to_message.forward_from_chat is not None:
                    if update.message.reply_to_message.forward_from_chat.id == channel_post_chat_id:
                        forwarded_message = bot.forward_message(chat_id=admin_chat_id,
                                                                from_chat_id=update.message.chat_id,
                                                                message_id=update.message.reply_to_message.message_id)
                        reply_to_message_id = forwarded_message.message_id
            print(reply_to_message_id)
            send_any_message(bot=bot, chat_id=admin_chat_id, message=update.message, reply_markup=markup,
                             reply_to_message_id=reply_to_message_id)
            update.message.reply_text('با تشکر ' + update.message.from_user.first_name + ' . توییت شما دریافت شد!')
    if update.channel_post is not None:
        if update.channel_post.chat.type == 'channel' and channel_post_chat_id == '':
            channel_post_chat_id = update.channel_post.chat_id
            print(channel_post_chat_id)


def get_contact(bot, update):
    print(update)
    global channel_post_chat_id
    global admin_chat_id
    if update.message is not None:
        if update.message.chat.type == 'private':
            if update.message.contact is not None:
                if update.message.contact.phone_number == '115':
                    admin_chat_id = update.message.chat_id
                    bot.send_message(chat_id=admin_chat_id, text='عه تو ادمین شدی!!!!!')
                    return
            if update.message.forward_from_chat is not None:
                if update.message.forward_from_chat.id == channel_post_chat_id:
                    print('cancel')
                    return
            keyboard = [[InlineKeyboardButton("اوکی 👍", callback_data='ye'),
                         InlineKeyboardButton("نوکی 👎", callback_data='no')],
                        [InlineKeyboardButton('از طرف کیه؟', callback_data='user' + str(update.message.from_user.id))]]
            markup = InlineKeyboardMarkup(keyboard)
            reply_to_message_id = None
            if update.message.reply_to_message is not None:
                if update.message.reply_to_message.forward_from_chat is not None:
                    if update.message.reply_to_message.forward_from_chat.id == channel_post_chat_id:
                        forwarded_message = bot.forward_message(chat_id=admin_chat_id,
                                                                from_chat_id=update.message.chat_id,
                                                                message_id=update.message.reply_to_message.message_id)
                        reply_to_message_id = forwarded_message.message_id
            print(reply_to_message_id)
            send_any_message(bot=bot, chat_id=admin_chat_id, message=update.message, reply_markup=markup,
                             reply_to_message_id=reply_to_message_id)
    if update.channel_post is not None:
        if update.channel_post.chat.type == 'channel' and channel_post_chat_id == '':
            channel_post_chat_id = update.channel_post.chat_id
            print(channel_post_chat_id)


def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater("427411167:AAEwT1ByVafesnS-kn1ITebZ8zy2SAoUGEk")

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_handler(MessageHandler(Filters.contact, get_contact))
    updater.dispatcher.add_handler(MessageHandler(Filters.photo, get_all))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, get_all))
    updater.dispatcher.add_handler(MessageHandler(Filters.audio, get_all))
    updater.dispatcher.add_handler(MessageHandler(Filters.document, get_all))
    updater.dispatcher.add_handler(MessageHandler(Filters.sticker, get_all))
    updater.dispatcher.add_handler(MessageHandler(Filters.video, get_all))
    updater.dispatcher.add_handler(MessageHandler(Filters.video_note, get_all))
    updater.dispatcher.add_handler(MessageHandler(Filters.voice, get_all))
    updater.dispatcher.add_handler(MessageHandler(Filters.venue, get_all))
    updater.dispatcher.add_handler(MessageHandler(Filters.location, get_all))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

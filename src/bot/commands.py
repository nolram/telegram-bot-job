
from typing import Tuple, Dict, Any

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ConversationHandler,
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    Filters,
)

SELECTING_ACTION, ADDING_DATA, SHOWING_DATA = map(chr, range(3))

STOPPING, SHOWING = map(chr, range(3, 5))

SELECTING_FEATURE, TYPING = map(chr, range(5, 7))

SELECTING_LEVEL = map(chr, range(7, 8))
# Different constants for this example
(
    DATA,
    AGE,
    NAME,
    EMAIL,
    PHONE,
    START_OVER,
    FEATURES,
    CURRENT_FEATURE,
    CURRENT_LEVEL,
    ADD_INFO,
    SELF,
) = map(chr, range(10, 21))

END = ConversationHandler.END


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""

    text = (
           'Por favor, nos informe os dados abaixo para podermos indentificar-mos você!'
    )
    buttons = [
        [
            InlineKeyboardButton(text='Cadastro', callback_data=str(ADD_INFO)),
        ],
        [
            InlineKeyboardButton(text='Mostrar Dados', callback_data=str(SHOWING)),
            InlineKeyboardButton(text='Concluir', callback_data=str(END)),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    if context.user_data.get(START_OVER):
        update.callback_query.answer()
        update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    else:
        update.message.reply_text(
            'Olá! Bem vindo ao Southon, o bot do Southon!'
        )
        update.message.reply_text(text=text, reply_markup=keyboard)

    context.user_data[START_OVER] = False
    return SELECTING_ACTION


def ask_for_input(update: Update, context: CallbackContext) -> str:
    """Prompt user to input data for selected feature."""
    context.user_data[CURRENT_FEATURE] = update.callback_query.data
    text = 'Certo! Digite o seu dado'

    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text)

    return TYPING


def save_input(update: Update, context: CallbackContext) -> str:
    """Save input for feature and return to feature selection."""
    user_data = context.user_data
    user_data[FEATURES][user_data[CURRENT_FEATURE]] = update.message.text

    user_data[START_OVER] = True

    return select_feature(update, context)


def select_feature(update: Update, context: CallbackContext) -> str:
    """Select a feature to update for the person."""
    buttons = [
        [
            InlineKeyboardButton(text='Nome', callback_data=str(NAME)),
            InlineKeyboardButton(text='Idade', callback_data=str(AGE)),
        ],
        [
            InlineKeyboardButton(text='E-mail', callback_data=str(EMAIL)),
            InlineKeyboardButton(text='Telefone', callback_data=str(PHONE)),
        ],
        [
            InlineKeyboardButton(text='Voltar', callback_data=str(END)),
        ]
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    # If we collect features for a new person, clear the cache and save the gender
    if not context.user_data.get(START_OVER):
        context.user_data[FEATURES] = {}
        text = 'Please select a feature to update.'

        update.callback_query.answer()
        update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    # But after we do that, we need to send a new message
    else:
        text = 'Got it! Please select a feature to update.'
        update.message.reply_text(text=text, reply_markup=keyboard)

    context.user_data[CURRENT_LEVEL] = SELF
    context.user_data[START_OVER] = False
    return SELECTING_FEATURE



def end_describing(update: Update, context: CallbackContext) -> int:
    """End gathering of features and return to parent conversation."""
    user_data = context.user_data
    level = user_data[CURRENT_LEVEL]
    if not user_data.get(level):
        user_data[level] = []
    user_data[level].append(user_data[FEATURES])

    user_data[START_OVER] = True
    start(update, context)

    return END


def show_data(update: Update, context: CallbackContext) -> str:
    """Pretty print gathered data."""

    def prettyprint(user_data: Dict[str, Any], level: str) -> str:
        people = user_data.get(level)
        if not people:
            return '\nNo information yet.'

        text = ''
        for person in user_data[level]:
            text += f"\nName: {person.get(NAME, '-')}, Age: {person.get(AGE, '-')}"
        return text

    user_data = context.user_data
    text = f"Yourself:{prettyprint(user_data, SELF)}"

    buttons = [[InlineKeyboardButton(text='Back', callback_data=str(END))]]
    keyboard = InlineKeyboardMarkup(buttons)

    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    user_data[START_OVER] = True

    return SHOWING

def stop_nested(update: Update, context: CallbackContext) -> str:
    """Completely end conversation from within nested conversation."""
    update.message.reply_text('Okay, bye.')

    return STOPPING

def end(update: Update, context: CallbackContext) -> int:
    """End conversation from InlineKeyboardButton."""
    update.callback_query.answer()

    text = 'See you around!'
    update.callback_query.edit_message_text(text=text)

    return END


def stop(update: Update, context: CallbackContext) -> int:
    """End Conversation by command."""
    update.message.reply_text('Okay, bye.')

    return END

def prepare_handler() -> ConversationHandler:
    
    description_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                select_feature, pattern='^' + str(ADD_INFO) + '$'
            )
        ],
        states={
            SELECTING_FEATURE: [
                CallbackQueryHandler(ask_for_input, pattern='^(?!' + str(END) + ').*$')
            ],
            TYPING: [MessageHandler(Filters.text & ~Filters.command, save_input)],
        },
        fallbacks=[
            CallbackQueryHandler(end_describing, pattern='^' + str(END) + '$'),
            CommandHandler('stop', stop_nested),
        ],
        map_to_parent={
            # Return to second level menu
            END: SELECTING_LEVEL,
            # End conversation altogether
            STOPPING: STOPPING,
        },
    )
    
    selection_handlers = [
        description_conv,
        CallbackQueryHandler(show_data, pattern='^' + str(SHOWING) + '$'),
        CallbackQueryHandler(end, pattern='^' + str(END) + '$'),
    ]

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SHOWING: [CallbackQueryHandler(start, pattern='^' + str(END) + '$')],
            SELECTING_ACTION: selection_handlers,
            SELECTING_LEVEL: selection_handlers,
            ADDING_DATA: [description_conv],
            STOPPING: [CommandHandler('start', start)],
        },
        fallbacks=[CommandHandler('stop', stop)],
    )

    return conv_handler
    
import time
import logging
from typing import Dict, Optional

try:
    from models.dynamodb.user import HistoryChatModel, UserModel
except ImportError:
    from ..models.dynamodb.user import HistoryChatModel, UserModel

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext
)

# Enable logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

NAME, LOCATION, LOCATION_DETAILS, WORKING_MODEL, INTERVIEW_MODEL  = range(5)

JOB_TYPE, JOB_SKILLS, END_REGISTER = range(5,8)


def save_user_data(update: Update, type_data: int) -> None:
    text = update.message.text
    user = update.message.from_user
    try:
        user_id = str(user.id)
        logger.info(f"Save User Data: {user_id}")
        user_model = UserModel.get(user_id, 'telegram')
    except UserModel.DoesNotExist:
        user_model = UserModel(user_id=user_id, chat_type='telegram')
    
    if type_data == NAME:
        user_model.name = text
    elif type_data == LOCATION_DETAILS:
        user_model.address = text
    elif type_data == WORKING_MODEL:
        option_details_text = update.message.text
        user = update.message.from_user
        option = option_details_text.strip().split('-')[0]
        user_model.working_model = int(option)
    elif type_data == INTERVIEW_MODEL:
        option_details_text = update.message.text
        user = update.message.from_user
        option = option_details_text.strip().split('-')[0]
        user_model.interview_model = int(option)
    elif type_data == JOB_TYPE:
        user_model.jobs_preference = text.split(',')
    elif type_data == JOB_SKILLS:
        user_model.skills = text.split(',')

    user_model.save()


def get_user_data(user_id: str) -> Optional[UserModel]:
    try:
        return UserModel.get(user_id)
    except UserModel.DoesNotExist:
        return None

def get_last_state(update: Update) -> int:
    """
        Get the last update.
    """
    user_id = update.message.from_user.id
    history = HistoryChatModel.query(str(user_id), limit=1, scan_index_forward=False)
    for item in history:
        return item.last_state
    return None

def save_last_state(state: int, user_id: str) -> None:
    """Save the last state."""
    logger.info(state)
    logger.info(user_id)
    date_chat = time.time()
    history = HistoryChatModel(user_id=user_id, last_state=state, date_chat=str(date_chat))
    history.save()

# @save_last_state(GENDER)
def start(update: Update, context: CallbackContext) -> None:
    """
        Inicia a conversa com a pessoa
    """
    reply_keyboard = [['Sim', 'Não']]

    update.message.reply_text(
        'Olá, eu sou o Jobson! Seu amigo na hora de procurar um Job.\n\n'
        'Você gostaria de fazer um cadastro para ver nossas vagas de emprego?\n\n',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='Sim ou Não'
        ),
    )

    save_last_state(NAME, str(update.message.from_user.id))


def name(update: Update, context: CallbackContext) -> None:
    """
        Verifica a opção escolhida de pessoa e solicita o nome dela
    """
    user = update.message.from_user
    logger.info("Name of %s: %s", user.first_name, update.message.text)
    if update.message.text.lower() == 'sim':
        update.message.reply_text(
            'Legal! Qual o seu nome completo?',
            reply_markup=ReplyKeyboardRemove(),
        )
        save_last_state(LOCATION, str(update.message.from_user.id))
    else:
        update.message.reply_text(
            'Tudo bem! Fica para a próxima, quando quiser se cadastrar digite o comando /start',
            reply_markup=ReplyKeyboardRemove(),
        )
        save_last_state(ConversationHandler.END, str(update.message.from_user.id))


def location(update: Update, context: CallbackContext) -> None:
    """
        Pega o nome da pessoa e solicita o endereço para ela
    """
    save_user_data(update, NAME)
    reply_keyboard = [['1 - Cidade e Bairro', ], ['2 - Endereço Completo']]
    user = update.message.from_user
    name = update.message.text
    logger.info("Location of %s: %s", user.first_name, name)
    update.message.reply_text(
        f'Certo, {name}. Prazer em te conhecer! \n\n'
        f'Agora eu preciso de informações do seu endereço. '
        f'Quanto mais específico podemos te ajudar melhor, mas a escolha é sua.'
        f'Digite o número da opção escolhida (1 ou 2) ou escolha a opção do teclado:\n\n'
        f'1 - Cidade e Bairro\n\n'
        f'2 - Endereço Completo\n\n',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='1- Cidade e Bairro ou 2 - Endereço Completo'
        )
    )
    save_last_state(LOCATION_DETAILS, str(update.message.from_user.id))
    

def location_details(update: Update, context: CallbackContext) -> None:
    option_details_text = update.message.text
    user = update.message.from_user
    logger.info("Location details of %s: %s", user.first_name, option_details_text)
    option = option_details_text.strip().split('-')[0]
    logger.info("Location details of %s: %s", user.first_name, option)
    try:
        option = int(option)
        if option == 1:
            update.message.reply_text(
                'Digite o nome da cidade e o bairro separados por vírgula',
                reply_markup=ReplyKeyboardRemove(),
            )
            save_last_state(WORKING_MODEL, str(update.message.from_user.id))
        elif option == 2:
            update.message.reply_text(
                'Digite o endereço completo',
                reply_markup=ReplyKeyboardRemove(),
            )
            save_last_state(WORKING_MODEL, str(update.message.from_user.id))
        else:
            update.message.reply_text(
                'Opção inválida, escolha novamente',
                reply_markup=ReplyKeyboardRemove(),
            )
            save_last_state(LOCATION, str(update.message.from_user.id))
    except ValueError:
        update.message.reply_text(
            'Opção inválida, escolha novamente',
            reply_markup=ReplyKeyboardRemove(),
        )
        save_last_state(LOCATION, str(update.message.from_user.id))


def working_model(update: Update, context: CallbackContext) -> None:
    """
        Pega o endereço da pessoa e solicita o modelo de trabalho
    """
    save_user_data(update, LOCATION_DETAILS)
    reply_keyboard = [['1- 100% remoto', ], ['2 - misto, parte remoto parte presencial'],
                      ['3 - 100% presencial'], ['4 - tanto faz']]
    user = update.message.from_user
    logger.info("Working model of %s: %s", user.first_name, update.message.text)
    update.message.reply_text(
        'Qual o modelo de trabalho que você gostaria de trabalhar?\n\n'
        'Digite o número da opção escolhida (1, 2, 3 ou 4) ou escolha a opção do teclado:\n\n'
        '1- 100% remoto\n\n'
        '2 - misto, parte remoto parte presencial\n\n'
        '3 - 100% presencial\n\n'
        '4 - tanto faz\n\n',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='1- 100% Remoto ou 2 - Misto ou 3 - 100% Presencial ou 4 - Tanto faz'
        )
    )
    save_last_state(INTERVIEW_MODEL, str(update.message.from_user.id))


def interview_model(update: Update, context: CallbackContext) -> None:
    reply_keyboard = [['1- Presencialmente', ], ['2 - Online'],
                      ['3 - Tanto faz']]
    option_details_text = update.message.text
    user = update.message.from_user
    option = option_details_text.strip().split('-')[0]
    logger.info("Interview model of %s: %s", user.first_name, update.message.text)
    try:
        option = int(option)
        if option < 1 or option > 4:
            update.message.reply_text(
                'Opção inválida, escolha novamente',
                reply_markup=ReplyKeyboardRemove(),
            )
            save_last_state(WORKING_MODEL, str(update.message.from_user.id))
        else:
            save_user_data(update, WORKING_MODEL)
            update.message.reply_text(
                'Qual o modelo de entrevista você gostaria de fazer?\n\n'
                'Digite o número da opção escolhida (1, 2 ou 3) ou escolha a opção do teclado:\n\n'
                '1- Presencialmente\n\n'
                '2 - Online\n\n'
                '3 - Tanto faz\n\n',
                reply_markup=ReplyKeyboardMarkup(
                    reply_keyboard, one_time_keyboard=True, input_field_placeholder='1- Presencialmente ou 2 - Online ou 3 - Tanto faz'
                )
            )
            save_last_state(JOB_TYPE, str(update.message.from_user.id))
    except ValueError:
        update.message.reply_text(
            'Opção inválida, escolha novamente',
            reply_markup=ReplyKeyboardRemove(),
        )
        save_last_state(WORKING_MODEL, str(update.message.from_user.id))


def job_type(update: Update, context: CallbackContext) -> None:
    save_user_data(update, INTERVIEW_MODEL)
    option_details_text = update.message.text
    user = update.message.from_user
    option = option_details_text.strip().split('-')[0]
    logger.info("Job type of %s: %s", user.first_name, update.message.text)
    try:
        option = int(option)
        if option < 1 or option > 3:
            update.message.reply_text(
                'Opção inválida, escolha novamente',
                reply_markup=ReplyKeyboardRemove(),
            )
            save_last_state(INTERVIEW_MODEL, str(update.message.from_user.id))
        else:
            update.message.reply_text(
                'Ok, para qual vaga você gostaria de se candidatar?\n\n' 
                'Ex: Engenheiro Civil, Pedreiro, '
                'Auxiliar de administração, Auxiliar de limpeza...\n\n'
                'Digite as vagas de seu maior interesse separadas por vírgulas. Digite as mais importantes primeiro.',
                reply_markup=ReplyKeyboardRemove()
            )
            save_last_state(JOB_SKILLS, str(update.message.from_user.id))
    except ValueError:
        update.message.reply_text(
            'Opção inválida, escolha novamente',
            reply_markup=ReplyKeyboardRemove(),
        )
        save_last_state(INTERVIEW_MODEL, str(update.message.from_user.id))


def job_skills(update: Update, context: CallbackContext) -> None:
    save_user_data(update, JOB_TYPE)
    user = update.message.from_user
    logger.info("Job skills of %s: %s", user.first_name, update.message.text)
    update.message.reply_text(
        'Ok, agora preciso saber das tuas habilidades.\n\n' 
        'Digite as habilidades que você se identifica mais. '
        'Ex: Marcenaria, Cuidado de pacientes, Gestão de pessoas... ',
        reply_markup=ReplyKeyboardRemove()
    )
    save_last_state(END_REGISTER, str(update.message.from_user.id))


def end_register(update: Update, context: CallbackContext) -> None:
    save_user_data(update, JOB_SKILLS)
    user = update.message.from_user
    logger.info("End register of %s: %s", user.first_name, update.message.text)
    update.message.reply_text(
        'Cadastro realizado com sucesso! \n\n'
        'Agora vamos juntar seu perfil com as vagas disponíveis. '
        'Assim que der match nós vamos te avisar por aqui.',
        reply_markup=ReplyKeyboardRemove()
    )

def cancel(update: Update, context: CallbackContext) -> None:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Certo! Até mais! Se quiser falar comigo digite /start', reply_markup=ReplyKeyboardRemove()
    )

def handlers_state() -> Dict:
    return  {
        NAME: MessageHandler(Filters.text & ~Filters.command, name),
        LOCATION: MessageHandler(Filters.text & ~Filters.command, location),
        LOCATION_DETAILS: MessageHandler(Filters.text & ~Filters.command, location_details),
        WORKING_MODEL: MessageHandler(Filters.text & ~Filters.command, working_model),
        INTERVIEW_MODEL: MessageHandler(Filters.text & ~Filters.command, interview_model),
        JOB_TYPE: MessageHandler(Filters.text & ~Filters.command, job_type),
        JOB_SKILLS: MessageHandler(Filters.text & ~Filters.command, job_skills),
        END_REGISTER: MessageHandler(Filters.text & ~Filters.command, end_register),
    }


def prepare_handler(update: Update):
    """Run the bot."""
    last_state = get_last_state(update)
    logger.info(f"Last State: {last_state}")

    handlers = []
    handlers.append(CommandHandler('start', start))
    handlers.append(CommandHandler('cancel', cancel))

    handlers_state_dict = handlers_state()
    if last_state in handlers_state_dict:
        handlers.append(handlers_state_dict[last_state])

    logger.info('Handlers: {}'.format(handlers))
    return handlers
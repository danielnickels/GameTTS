
from datetime import datetime
from pathlib import Path
import platform
from app.utils import *
import telegram
from telegram.ext import Updater
import logging
from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import CommandHandler
import sys

try:
    from vits.synthesizer import Synthesizer

    synthesizer = Synthesizer(TTS_CONFIG_PATH)

    if TTS_MODEL_PATH.exists():
        synthesizer.load_model(TTS_MODEL_PATH)
    else:
        download_model("G_600000.pth")
        synthesizer.load_model(TTS_MODEL_PATH)

    synthesizer.init_speaker_map(SPEAKER_CONFIG)

except ImportError as err:
    print(err)
    eel.call_torch_modal()  # call javascript modal if torch not available


def synthesize(text, speaker_id, speaker_name, params):
    audio_data = synthesizer.synthesize(text, speaker_id, params)
    cur_timestamp = datetime.now().strftime("%m%d%f")
    tmp_path = Path("static_web", "tmp")

    if not tmp_path.exists():
        tmp_path.mkdir()

    file_name = "_".join(
        [str(speaker_id), speaker_name, str(cur_timestamp), "tmp_file"]
    )

    return save_audio(tmp_path, file_name, audio_data)


def start(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Ich bin...")

from telegram.ext import MessageHandler, Filters

def echo(update: Update, context: CallbackContext):
    params = {"speech_var_a": 0.3, "speech_var_b": 0.5, "speech_speed": 1.3}
    audiopath = synthesize(update.message.text, speaker, "nameloser_held",params)
    context.bot.send_audio(chat_id=update.effective_chat.id, audio=open(audiopath, 'rb'))

# start telegram bot
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Du idiot musst deinen telegram bot token und eine speaker id angeben")
        sys.exit()
    bottoken = str(sys.argv[1])
    global speaker
    speaker = int(sys.argv[2])
    updater = Updater(token=bottoken, use_context=True)
    bot = telegram.Bot(token=bottoken)
    dispatcher = updater.dispatcher
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)
    echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    dispatcher.add_handler(echo_handler)

    print(bot.get_me())
    updater.start_polling()
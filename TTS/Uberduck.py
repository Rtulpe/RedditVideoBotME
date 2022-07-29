import os
from typing import Union

from polling import poll
from requests import post, get

from utils.console import print_step

#todo reimplement
def _get_audio(uuid: str) -> Union[dict, bool]:
    """
    A private function to recieve audio from the API using a UUID. This function is polled until the desired audio is available.
    """
    response = get(
        url=f'https://api.uberduck.ai/speak-status?uuid={uuid}'
    )
    json: dict = response.json()
    return json if json.get('path') else False


class Uber:
    def tts(
            self,
            req_text: str = "Uberduck Text To Speech",
            filename: str = "title.mp3",
            random_speaker: bool = False,
            censor=False,
    ):
        voice = os.getenv("VOICE")

        data = {"speech": req_text, "void": voice}

        response = post(
            url='https://api.uberduck.ai/speak',
            auth=('pub_ayrkzbvyxosnelzcgw', 'pk_cda9f8bb-eac3-46ec-9811-fbcddf28edb4'),
            json={'speech': req_text, 'voice': voice.lower()}
        )

        json = response.json()

        result: dict = poll(
            lambda: _get_audio(json['uuid']),
            step=1,
            poll_forever=True
        )

        bytes_ = get(result['path']).content

        with open(filename, 'wb') as file:
            file.write(bytes_)
from typing                     import Dict, Any, List

from src.helpers.SessionHelper  import HTTPError, ProxyError
from src                        import Session
from src.arkose.challenge       import (
    Challenge,
    ProxyConnectionFailed,
    Http3NotSupported,
    parse
)

class Game:
    def __init__(self, Challenge: Challenge) -> None:
        self.challenge: "Challenge" = Challenge

        self.session:   Session = self.challenge.session
        self.settings:  Dict[str, str] = self.challenge.settings

        self.base_url:  str = self.challenge.base_url
        self.version:   str = self.challenge.version
        self.hash:      str = self.challenge.hash

        self._imgs:     List[str] = []
        self.gameToken: str = ""
        self.variant:   str = ""
        self.gameType:  int = 0
        self.waves:     int = 0
        self.diff:      int = 0
        
    def _enforcement_callback(self) -> None:
        url: str = f"{self.base_url}/v2/{self.version}/enforcement.{self.hash}."
        
        try:
            self.session.get(url + "html")
            self.session.get(url + "js")
        
        except HTTPError as e:
            raise Http3NotSupported(f"Failed to load enforcement resources: {str(e)}")
        
        except ProxyError as e:
            raise ProxyConnectionFailed(f"Failed to connect to proxy for enforcement: {str(e)}")
    
        except Exception as e:
            raise Exception(f"CS-AI-ERR: Failed to load enforcement resources: {str(e)}")

    def _init_load(self) -> None:
        try:
            self.session.get(f"{self.base_url}/fc/init-load/?session_token={self.challenge.session_token}")
            
            gameCoreCallbackUrl: str = f"{self.base_url}/fc/assets/ec-game-core/game-core/{self.challenge.game_version}/standard/index.html?session={self.challenge.session_token}{''.join(self.challenge.full_token.split('|')[1:])}"
            self.session.get(gameCoreCallbackUrl)

        except HTTPError as e:
            raise Http3NotSupported(f"Failed to load enforcement resources: {str(e)}")
        
        except ProxyError as e:
            raise ProxyConnectionFailed(f"Failed to connect to proxy for enforcement: {str(e)}")
    
        except Exception as e:
            raise Exception(f"CS-AI-ERR: Failed to load enforcement resources: {str(e)}")

    def _user_callback(self):
        BasePayload: Dict[str, Any] = {
            'sid': self.challenge.full_token.split("|")[1].replace("r=", ""),
            'session_token': self.challenge.session_token,
            'analytics_tier': '40',
            'disableCookies': 'false',
            'render_type': 'canvas',
            'is_compatibility_mode': 'false',
            'category': 'Site URL',
            'action': f'{self.base_url}/v2/{self.version}/enforcement.{self.hash}.html',
        }

        self.session.post(
            f"{self.base_url}/fc/a/", 
            data=str(parse.urlencode(BasePayload))
        )

        BasePayload.update({
            "game_token": self.gameToken,
            "game_type": self.gameType,
            "action": "game loaded"
        })
        self.session.post(
            f"{self.base_url}/fc/a/", 
            data=str(parse.urlencode(BasePayload))
        )

        BasePayload.update({
            "action": "user clicked verify"
        })
        self.session.post(
            f"{self.base_url}/fc/a/", 
            data=str(parse.urlencode(BasePayload))
        )

    def gfct(self) -> Dict[str, Any]: # fuck ton parsing here KMS -Traili
        try:
            Payload: Dict[str, Any] ={
                "token": self.challenge.session_token,
                "sid": self.challenge.full_token.split("|")[1].replace("r=", ""),
                "render_type": "canvas", # Canvas | noJS <- forces GT3
                "lang": self.challenge.browser["language"] or "",
                "isAudioGame": "false",
                "is_compatibility_mode": "false",
                "apiBreakerVersion": "green",
                "analytics_tier": 40 # static for now, but its usually in token at=...
            }

            gfct = self.session.get(f"{self.base_url}/fc/gfct/", data=str(parse.urlencode(Payload))) # <- slick but dont forget / at the end

            if "denied" in gfct.text:
                raise Exception("Request was denied, rotating proxy IP?")
            
            if gfct.ok:
                rjson = gfct.json()

                self.gameToken = rjson["challengeID"]

                gameData = rjson["game_data"]

                self._imgs = gameData["customGUI"]["_challenge_imgs"]
                self.variant = gameData["instruction_string"]
                self.waves = gameData["waves"]
                self.gameType = gameData["gameType"]
                self.diff = gameData["game_difficulty"]

        
        except HTTPError as e:
            raise Http3NotSupported()
        
        except ProxyError as e:
            raise ProxyConnectionFailed()
    
        except Exception as e:
            raise Exception(f"CS-AI-ERR: Failed to load enforcement resources: {str(e)}")

    def put_answer(self, guess: Dict[str, int]) -> bool:
        ...


# It has been days since anyone has touched this file.
# Somebody, one day, will stumble across this chaotic masterpiece and say,
# "Wow, this is... good? Or maybe just a desperate cry for help?"
# Every single day is an endless cycle of pain, sadness, and existential suffering.
# If someone could just take a load off my weary, overburdened shoulders,
# it would be so nice of them—maybe even heroic.
# But alas, here I remain, abandoned like a half-eaten sandwich in the office fridge,
# slowly decomposing into a glorious monument of procrastination.
# Future developer, if you are reading this, please send coffee and moral support.
# Also, don't judge me—I swear it worked on my machine.
# If this file somehow still runs, it's a testament to miracles,
# duct tape, and sheer stubbornness in the face of overwhelming odds.
# Legend says the original author vanished into the void of burnout,
# leaving only cryptic comments and questionable function names behind.
# May whoever inherits this code find the strength, patience,
# and perhaps a sense of humor to survive its horrors.
# And remember: touching this file may void your warranty on sanity.
# Proceed at your own risk, brave soul.


# bro shut the fuck up
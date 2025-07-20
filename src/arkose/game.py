from base64     import b64decode, b64encode
from random     import uniform, randint
from typing     import Dict, Any, List
from urllib     import parse
from json       import dumps


from src.utils.bio              import EnhancedDataGenerator
from src.helpers.SessionHelper  import HTTPError, ProxyError
from src.utils.crypto           import AES_Crypto
from src                        import Session
from src.utils.utils            import Utils
from src.arkose.challenge       import (
    Challenge,
    ProxyConnectionFailed,
    Http3NotSupported,
    parse
)

def gt3Coordinates(
    answer_index: int, layouts: Dict[str, Any]
) -> Dict[str, float]:
    columns = layouts["columns"]
    rows = layouts["rows"]
    tile_width = layouts["tile_width"]
    tile_height = layouts["tile_height"]
    if not 0 <= answer_index < columns * rows:
        raise ValueError(f"The answer should be between 0 and {columns * rows}")
    x = (answer_index % columns) * tile_width
    y = (answer_index // columns) * tile_height
    px = round(uniform(0, tile_width), 2)
    py = round(uniform(0, tile_height), 2)
    return {"px": px, "py": py, "x": x, "y": y}

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
        self._imgs_d:    List[bytes] = []
        
    def _enforcement_callback(self) -> None:
        url: str = f"{self.base_url}/v2/{self.version}/enforcement.{self.hash}."
        
        try:
            self.session.get(url + "html")
            self.session.get(url + "js")
        
        except HTTPError as e:
            raise Http3NotSupported()
        
        except ProxyError as e:
            raise ProxyConnectionFailed(f"Failed to connect to proxy for enforcement: {str(e)}")
    
        except Exception as e:
            raise Exception(f"CS-AI-ERR: Failed to load enforcement resources: {str(e)}")

    def _init_load(self) -> None:
        try:
            self.session.get(f"{self.base_url}/cdn/fc/assets/ec-game-core/bootstrap/{self.challenge.version}/standard/game_core_bootstrap.js")

            self.session.get(f"{self.base_url}/fc/init-load/?session_token={self.challenge.session_token}")
            
            gameCoreCallbackUrl: str = f"{self.base_url}/fc/assets/ec-game-core/game-core/{self.challenge.game_version}/standard/index.html?session={self.challenge.full_token.replace('|', '&')}"
            self.session.get(gameCoreCallbackUrl)

        except HTTPError as e:
            raise Http3NotSupported()
        
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
            "action": "game loaded",
            "category": "loaded"
        })
        self.session.post(
            f"{self.base_url}/fc/a/", 
            data=str(parse.urlencode(BasePayload))
        )

        BasePayload.update({
            "action": "user clicked verify",
            "category": "begin app"
        })
        self.session.post(
            f"{self.base_url}/fc/a/", 
            data=str(parse.urlencode(BasePayload))
        )

    def gfct(self) -> Dict[str, Any]: # fuck ton parsing here KMS -Traili
        try:
            Payload: Dict[str, Any] ={
                "token": self.challenge.session_token,
                "sid": self.challenge.full_token.split("|")[1].replace("r=", ""), # but you cou- SHUT THE FUCK UP
                "render_type": "canvas", # Canvas | noJS <- forces GT3
                "lang": self.challenge.browser["language"] or "",
                "isAudioGame": False,
                "is_compatibility_mode": False,
                "apiBreakerVersion": "green",
                "analytics_tier": 40 # static for now, but its usually in token, at=...
            } # 100% skidded from hamidnigger

            self.session.cookies.update({
                "timestamp": Utils.x_ark_esync()
            })

            gfct = self.session.post(f"{self.base_url}/fc/gfct/", data=Payload) # <- slick but dont forget / at the end

            if "denied" in gfct.text.lower() or gfct.status_code != 200:
                raise Exception("Request was denied, rotating proxy IP?")
            
            if gfct.ok:
                rjson = gfct.json()

                print(rjson)

                self.gameToken = rjson["challengeID"]

                gameData = rjson["game_data"]

                self._imgs = gameData["customGUI"]["_challenge_imgs"]
                self.variant = gameData["instruction_string"]
                self.waves = gameData["waves"]
                self.gameType = gameData["gameType"]
                self.diff = gameData["game_difficulty"]

                return rjson
        
        except HTTPError as e:
            raise Http3NotSupported()
        
        except ProxyError as e:
            raise ProxyConnectionFailed()
    
        except Exception as e:
            raise Exception(f"CS-AI-ERR: Failed to fetch GFCT: {str(e)}")

    def put_answer(self, guess: Dict[str, int]) -> bool:
        try: # only for gametype 4 now

            guessCrypt = AES_Crypto.encrypt_data(dumps(guess), self.challenge.session_token)
        
            Payload = {
                "session_token": self.challenge.session_token,
                "game_token": self.gameToken,
                "sid": self.challenge.full_token.split("|")[1].replace("r=", ""),
                "guess": guessCrypt,
                "render_type": "canvas",
                "analytics_tier": 40,
                "bio": str(EnhancedDataGenerator().generate()),
                "is_compatibility_mode": False
            }

            newrelic = Utils.x_ark_esync()

            requestID: str = AES_Crypto.encrypt_data(
                dumps(
                    {
                        "sc": [randint(180,220), randint(180,220)]
                    }
                ),
                f"REQUESTED{self.challenge.session_token}ID"
            )

            self.session.cookies.update(
                {
                    "timestamp": newrelic
                }
            )

            self.session.headers.update(
                {
                    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                    "X-Newrelic-Timestamp": newrelic,
                    "X-Requested-Id": requestID,
                    "X-Requested-With": "XMLHttpRequest",
                    "referer": f"{self.base_url}/fc/assets/ec-game-core/game-core/{self.challenge.game_version}/standard/index.html?session={self.challenge.full_token.replace('|', '&')}&theme=default"
                }
            )


            response = self.session.post(
                f"{self.base_url}/fc/ca/",
                data=parse.urlencode(Payload)
            )

            if response.status_code != 200:
                raise Exception(f"CS-AI-ERR: Failed to put answer: {response.text}")

            elif response.status_code == 200:
                return bool(response.json()["solved"])
            
            raise Exception(f"CS-AI-ERR: Failed to put answer: {response.text} - {response.status_code}")

        except HTTPError as e:
            raise Http3NotSupported()
        
        except ProxyError as e:
            raise ProxyConnectionFailed(f"Failed to connect to proxy for answer: {str(e)}")
    
        except Exception as e:
            raise Exception(f"CS-AI-ERR: Failed to put answer: {str(e)}")

    def get_images(self):
        try:
            for img in self._imgs:
                self.session.cookies.update(
                    {
                        "timestamp": Utils.x_ark_esync()
                    }
                )
                r = self.session.get(img)

                if r.status_code == 200:
                    imgbytes = r.content

                    self._imgs_d.append(imgbytes)
            
            self._imgs.clear()

        
        except HTTPError as e:
            raise Http3NotSupported()
        
        except ProxyError as e:
            raise ProxyConnectionFailed(f"Failed to connect to proxy image: {str(e)}")
    
        except Exception as e:
            raise Exception(f"CS-AI-ERR: Failed to get image: {str(e)}")
        

    def parse_images(self):
        try:
            for img in self._imgs_d:
                imgb64 = b64encode(img).decode("utf-8")
                imgmd5 = Utils.md5hash(imgb64)

                self._imgs.append((imgb64, imgmd5))

        except Exception as e:
            raise Exception(f"CS-AI-ERR: Failed to parse images: {str(e)}")





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
# - Unknown Developer

# bro shut the fuck up - Traili

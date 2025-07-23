import time, random, json
from curl_cffi import requests


class Game:

    @staticmethod
    def remove_all_html_tags(text):
        pattern = compile(r'<[^>]+>')
        return pattern.sub('', text)

    @staticmethod
    def is_flagged(data):
        if not data or not isinstance(data, list):
            return False
        values = [value for d in data for value in d.values()]
        if not values:
            return False

        def ends_with_uppercase(value):
            return value and value[-1] in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

        return all(ends_with_uppercase(value) for value in values)

    def __init__(self, session, game_data: dict) -> None:
        self.waves: int = game_data['game_data']['waves']
        self.type: int = game_data['game_data']['gameType']
        self.game_variant: str = game_data['game_data']["instruction_string"] if self.type == 4 else \
        game_data['game_data']["game_variant"]
        print(game_data)
        self.prompt: str = self.remove_all_html_tags(
            game_data["string_table"][f"{self.type}.instructions-{self.game_variant}"])

        self.dapib_url: str = game_data["dapib_url"] if "dapib_url" in game_data else None
        self.session_token: str = game_data["session_token"]
        self.challenge_id: str = game_data["challengeID"]

        self.customGUI = game_data["game_data"]["customGUI"]
        self.layouts = self.customGUI["_challenge_layouts"] if self.type == 3 else None
        self.image_urls = self.customGUI["_challenge_imgs"]

        self.guess = []
        self.guessind = []
        self.tguess = []

        self.session = session

    def get_image(self, number):
        response = self.session.get(self.image_urls[number], tls=False)
        if response.status_code != 200:
            raise Exception("Failed to get image: " + response.text)

        return response.content

    def get_tguess_crypt_two(self):
        session, ion = self.session_token.split(".")
        answers = []
        for guess in self.guess:
            if "index" in guess:
                answers.append({"index": guess["index"], session: ion})
            else:
                answers.append({"px": guess["px"], "py": guess["py"], "x": guess["x"], "y": guess["y"], session: ion})

        payload = {
            "answers": answers,
            "dbapi": self.session.get(
                self.dapib_url,
                headers={
                    "accept": "*/*",
                    "accept-language": "en-US,en;q=0.9",
                    "cache-control": "no-cache",
                    "origin": "https://client-api.arkoselabs.com",
                    "pragma": "no-cache",
                    "sec-ch-ua": "\"Google Chrome\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": '"Windows"',
                    "sec-fetch-dest": "script",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-site": "same-origin",
                    "sec-gpc": "1",
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
                },
            ).text,
        }


class CaptchaProcessor:
    def _parse_arkose_token(self):
        token = "token=" + self.token
        assoc = {}
        for field in token.split("|"):
            s = field.partition("=")
            key, value = s[0], s[-1]
            assoc[key] = value
        return assoc

    def __init__(self, proxy, blob):
        a, b = str(time.time()).split(".")
        self.ts = str(a + b[0:5])
        self.token = ""
        self.assoc = ""
        self.session_token = ""
        self.sid = ""
        self.analytics_tier = ""
        self.session = requests.Session(impersonate="safari260_ios", default_headers=False, verify=False, allow_redirects=True)
        if proxy is not None:
            if "http://" in proxy:
                self.proxy = proxy
            else:
                self.proxy = "http://" + proxy
            self.session.proxies = {"http": proxy, "https": proxy}
        self.blob = blob

        self.esync = str(int(time.time() - (time.time() % 21600)))
        self.enforcement, self.api_ver = self._fetch_api_info()
        self.mainLogic()

    def _fetch_api_info(self) -> tuple:
        return "df45d93b7883fed1e47dedac58c1d924", "3.5.0"

    def get_challenge(self):
        self.session.get(
            f'https://arkoselabs.roblox.com/v2/476068BF-9607-4799-B53D-966BE98E2B81/settings',
            headers={
                "sec-ch-ua-platform": "\"Windows\"",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
                "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
                "sec-ch-ua-mobile": "?0",
                "accept": "*/*",
                "sec-fetch-site": "same-site",
                "sec-fetch-mode": "cors",
                "sec-fetch-dest": "empty",
                "accept-encoding": "gzip, deflate, br, zstd",
                "accept-language": "en-US,en;q=0.9",
            }
        )

        headers = {
            "sec-ch-ua-platform": "\"Windows\"",
            "x-ark-esync-value": self.esync,
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "sec-ch-ua-mobile": "?0",
            "accept": "*/*",
            "origin": "https://www.roblox.com",
            "sec-fetch-site": "same-site",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            'referer': "https://www.roblox.com/",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
        }

        payload = {            
            "public_key": "476068BF-9607-4799-B53D-966BE98E2B81",
            "capi_version": self.api_ver,
            "capi_mode": "inline",
            "rnd": str(random.random() - random.uniform(float(f"0.00{random.randint(0,1)}001"), 0.0001)),
            "style_theme": "default",
            "bda": "eyJjdCI6ImYxRVIrSTE5aGVFVEZRdVBRRUZaT3FXbE4vTGYvRnBGVXdmY1pEc0h2Vm1KYUlITE5EbkErQy9wY2tTSEpZRmNQQ21RMDQrNEJjVDE3ZHlGaGhQNnlLTlZyR0M4U0JhYnZ2MkNyTzBvNHhWN3lWQjVKKzF4S0NUVDdnNjRjL1hUbFJuRGJIS3VmV21qcWgwcWZweGNsNTFWVlRZMGxxM1hWQ252U0l1Y1duakNxZzNoVW5WdUJidnY5a09lUFd3dmJUK2pOVUJMRi80blJyc2E4WWQ0dVlDNDRkcXI1ckI1TUxzcVFab0ZHTXJLMC91dVc0TWhSZ0cwdG1ZTnpiMzNuSUxSazMxVCtRallMeTNvUlFRSE1lVHJoUnc5Y3N1akFrbjB2SnlFZmF4UGIwS3IxVmIwT2JHUkpOWnJQSXlaU3FHM0k4RzRtREREL00yeU9JRzdUTTlUeVljelJQRGtPMUtuZXBzUEhtUWQxQ2JUUzJXbzBDQWZDdWVjYjNwTFQxRENBdkV2OGI3UmhVdW9mUUFXc0lqRitlYXgxVVpxZEhaUWFEc1J0OHlDdzF5TlkrMHdYUjlZYjlhU2d0TFlUcE0xM0szVEI5Q2VjaGd3ckgrVjVHMUdXVFNtVExjRTJ6b0JZQlVSUnY1ZDJpanhoZ0xvTzRZRkRud09ZMkRZb0FZeUdyRzN0aysxMlVEWXdiWE5kTVQ3Y3QrWnlKb09CZkMzeTFEbzUrQWloUmZvTjF0S1Rrb1RIbnVtUXprVjlXZzJJa3U5aXB5bStRRmZHamh0bERWQWhGTXhaWlBXMFVKc0lNV0Q1cWdjcExRS0MwUTRrR0FFYll5dVhyS0pSbHFuQ2JYN2hhNkFxLzY1SUZEYzRTem9sR1dteGN0Uno4clJzU1NGZVYraEREeVNmM3pzNGl3TEFPaFpMWXZqbkZkUk15QURseXQ4SUd3MmFOTlo2QU02UDAycjFvL1Z5a3lqQVpmcEFIUVhuamhJdkJ4UGFjUTNMazZDQmhvRklGN2htV21LQ04rZWh4VzE3SlIyRlg2REJ0UXhKNUZEUG92QnhLRmhSNlNrcmRQODJhVGM5aldIayszL0VHWGxScHRqU1hhVW1nN3hKNkFNNityNHU0USt1K2djTjdCek9ScmYwcVlySHlpTUtQb3h6ZG9tZ09TSHVvNVZ2U21DKzFuMlFCNzc5bGJXa2lneDF6WHc5VW1jWXdIaXFLSHlOUlFydFdiaWg0elJlbjJFc2psY0k3RWxMQTVWbXFXZG9wVXZ2T0J4dE9lOHZuZytpaGVrNGlYWDMxZXVMSmhyOVRGOGZ0dDVwWENPZW1rUWN3c2U3UVFkLzZhRm53cVlBNlFsVE05TWVwVEIzVUZUa2ttZEtFWjFXTU92NHlaWUo4Qk9Ud0NwMDdoT2Z5dzYvdzQ0aHR2cjA5MDJiemFPbzA1RGhNTUVrK3NsN29MM0VoVm9GUVJlb29JQmhkUVltWmYva0xpRXlseXQ2TE9JMENqNzNoTGNYaVRWdDYxRlk1SFo4RitXTUNETHNENlI4OXZFUU1WZENpaFBsZWcxVXJtY0VkYUt3bnFQcUgzcTlEVkxUTGRVVXJ2d21PYThJdjg4QW1iYi9YTE9nOTlnK2dxb2VYWTMzRE1BZ1JJYnEyaFJmZ2s0MmtiM0c0K0h1N016dm5vWmF3OVQyRGR4bm5Jd3VURXVjMDVtZlo2YWNSMWRyUFpyWFNBYUpoS3Y4SEpGdHZaVFNlVVpWRDMzOThHMmpXd2I3aXdKZWJIeDVGN2lKV1ZZV0xCbEVOek5wRDFTUFNuRStFL0hicTVLNiswY0JJYnF6ZUlnMlVFSjRZWWYraEZ0aWRiaFpjdHMwd1JyLzFZR1M5TG5xT1VKRUxmWjMyblExTFpkWi9uNFBoMFZFVElOUElscms1d0hIdXJqMEJLWEJLeEZhWGROdUE1WXpRTjFXeXR5U2M0T3VFWnF2QnZtam5QMHdvaHVrWEw2L1JOc1J6S0lqRm4vMnFtSE8vWGtORHFEOHdvaVcyQXhDOUpSazYvcXJUaFFHRmNDclNxSzI1S1psVFdwTnVyN3dxRmM4ZGU0TThFYm16d2daU3ZMZklxcFdhQjVwOVFrOTc0aW1iSmV1eCtRS0RaOS9wcVJVVWlqOWVJNDI5NDkzVm5LVVpUWkxWa0VjWGFUY0xlN1pIV2RiY08rYzRaMnlKU2x4TjZkZ0xNcFlpazhnUjA4UXBpelRFbWsrUmgzdHdZUEMyNnpZWEF0NmtFNEEzU3padzl5QXZnV3ZpTzVmVGlYK3dUaHFtbHg5RlBYenVnRTVvK0xqZXViWG1zVHVzbzVobnJjdlJjazNoWmtvSzIzZFA0OXJlaU5YMU5zNTUzejJ1a0ZuUHVBLys4WmpPejFaT2llMHdVdHg0N3lmTDNhYzhib3dhQ2s0ZVVTRWdUem1NUVpZSmV6Nk1pY0cydFdXdWcyc3VyMUZiN01KTEQwV0FSazY1azVJRDJOVTZEU01JNWFRZ2d6blZtZ1Q2RGRhMnhtazFkNmxicWhGY3hndjEzSXdjUFBjMktTVldabFNTUSs1NmFFZmd1czJFc1ZJYjJoeGhZcTlyZlYwZG9uUTRwMUw1MDQvSm9Nbk13dHJGU0pnQXFibXF5N0wwNXBQaEcxc2xLNDhwbnNPY1RSVjBiQzFsWmhGUU0vcGFCYWV4ZTNTS1NxeE94QjhCMFh1RnFXemc4RXkyekphSG5abkRSWlNDb1ZsQnJveXRBQ3pZZk91WkdTS0duV2FvbHZ1MnJMQ1B1TVQrU3BNYUE1NTR2V0xLaTZ4UFJVNUI5YUNFN2Q0NkJhNW02V0JwUWgvbVZDbjJKcmQwOFh2VXlYdk9xR0VmNUNMY3krdjZPcTJVeVdEYVgzUnloMDF1TkVFMnR1cEJodUJUUmg1eklWcTlkYWd6ZkZGQzdtMFRNcGtuUVYrdHpETzJHVEN6dVlwOXlCYVVBWkQwVFMxVWZzek5qSUMrSldwNG5vQ2JOZW1GVlhmemxnYzdNL1RIelR0M1VLV0hpejR1OE1SYVBydm80VVhOVFFJWjJKTlk3VkdEbDdQelR0OGFCcUdMbEY5eFpiazhGY2IyZFhkQnc5ZFVyd2ovSmtaQzZxc0ZVZi9VUXR2akl5eWpkampkSS9ydzdaQms0M3p6dnRjeVV5QnRVcytpNHZqRkhPeHFicmJIWXgvaFoxSGUvSUttQ1J3ZlJMd2plZGk3S0dNaGRCL1kzZ1BoY0ZRVGg1ZVQ1Q3YrNGlMT3U0R2pMTWpRMVlRZGl5ZkFVQjR6YXVGdmVVUDd4UzVqVHc0Y2tWNys1bmFmUnl5K1QyMTNQdU5ISTkybHdZWWpobkVvbUFodVBZUkpyaFFnaVA3a3UzaE9lWGEyNUdGenFSM2tjNFA5VWtQR1p0SVZEZ1ZpcUFmZ2JoR3B2OTh1SFlxQXlQWENJdEp2NjNxRlFpY2dJeHZnUTVVU0ZNekJGTEJmOSs1QTZpYmcwdElSUkpUQWhnR0EySTV1ZzQveSsxeHJtdlExUXA5WEk2RWRpQi8wUnM0Slo4OW1kN1hCTDJnRWluem5LMFpsTDZTM0tGMWt2cjZFbE5NSzZwTWVqaS9YMEFzUS9yWFg0VkxwS2JHTkxIT0FmOTRtSEFNMlhpNWtFOTJKcmt1OHV5Q3lvWDdOVHpyNXJNUUJPd05ON3ZJdmN5bmlmdm9VV2I3MU9tMFlibmpOZ21JMlFrbnpWZUljczNkcjRkV3ZjUkxsNmI3ZDBtRU9vNWo2RmxRdTZEQTJRUW9ROXloS0lEWHp4TXpXWi81V2kxZlplS0g2Znh6cVBiaWVPUnR1OENzY1hMbUkyemhJZEV6cXVBRmEzVGFHS0NtWUJSTUQrbFZlM20rNTdGeFY5QWlZTzY3MHRCSGFMZWVBczZFYmxMVURQL1NPcy9iMTNlUnR3NVMzVlNoWW1uQ1R1Q0xuME94a2xvWXZRdjFiVCsxRDZITWtUcGJOck92Nk1TRDVKakxZMW8yditlQnV5UC9zMDVaZkNyK0I4cFROYWZGYzR4cm9GczMxVHZFWEEzSnB5SmZUNWdUM0xRMnhYbno1MUJNYkk4bytPVTVOV0hBZUM0SmdWNnRyWWg0VXRITFcwS21QcGk3eGgvSHJ1SlExNk1Tc0NaN21LK3B3VEtqQmZWeFprZjVxSDFOMjUzRit5WTVIdlZudzluTkFRaTdONGdMbEx6ejZJTitablJrZ3U3K0hiRmpJTDBFaUJ2RG5KaUp4eDNTbHQ2YlJYYjhXUnBNcmM5eHJGL2cvblR1RVJFNjZ2a1BQTXFmUXd1RWRHb0RwMzhEZnhkSUoyZXUzdjNtanpaTHVkeStyN1hGcjM2dkVTTHc3QjlEd0R2REIrRkQzVG8rVzExZnVHbmRES2xWMHltTURqcVFXNmlnd3BoVFpkNmdMNVd1YnRZbWtueHFEbVc0TkZIQW42d2JwRVpCaXh3anBLTm9YZXNRRXFwMWJTY1Mzam1lU014V3pjLzhLVTEvUHpOR0FZZVJteDBQNThZcG1jTmlzWmdkaHdvWTB2MGZhZmtmamxJeWJZK3dXNmxPcVlUWk5IR2FpNXRBNUJBcWxxdFlacTdrR1NZUi9UY21nWlZTNzg1RlM3YkpqNWNWQVRLODdmbTdOaTExRzdrdkN3Z0I0QXlDbnNjZGpsVFR1VndVQjNLenE3dlRhS2JNMVQwK29CbHJYY09rbjBTcGlSWFNyRjZmOG5ZblU2SUdVNzcvb1Myd1BHRzhDT1JoUHhuczlzK3NZT3ZtTVo3bHZmNFdnYmRWV0JZYmY5QkZhQTZQUTBmZmloNE1KakE4cnRRMUJyNWVBeE5lZnR6c3JTMlBiZEw1WkllUVBWbnRkc1NtNi9kRHI2eGZyemNPK3BYa3VzSGNzRzlZeDloTUF6ZzRJaFh6by9Jem13cHRLcEljY3E3WUF2SVIyMnR2Wk5wSXRXZjlXcHdBcTArWFRSUFhtcks0cmtQdXBkaERFTWZmd3JTU3JXYk12dWFvM2tqZ3FMdjR4eHUrcmswbXpZWndJZjdsMndLMTRVN29FdjhlRDhRaFVOdHFjWUJPMWk2UFl3bFlMWWFhVXcxcTI5Y3hhbHlBQml4OTB2QitTTFhUN3lOMThpcy9zZ2RITERod0s3VmlVWGVJUVZ1Q0MvK2Y4OVczOUErdHo1VDhBSDJVeTdKbVN3U0tEemlEMmVJcEhLWm56dUh2YUFNbzk3TTBLNGhJcWE1ZnVCcjluRklXYng1MUFSR3NwanlvQkpSZFNOZDFLYXhqK1Z6RFY3ZVY2cHU2WVZYU0FrTUFkMEFWaEFjL1hGdEwwaFI3MGp3amd0ZmpaT21ubk9FWWdpbHc4bmZXVTluVHBUVEppUGdCRzFlTStuWFFnR2tTZEU4UmRDN1Mzak55ZS9yMTh0S3VKL2pRQ1pyUGxSYWk1QUNyaFE0cHZqcVpLNGs2WEFBSkZ4dURoRDhGaElqYzdJOEJyb3pUZGhPbmFwRk9hQ1U0Ny83YmhTRXNBZFZqa0dIYzk0QmU4M1RxenFPT0NCUGxNVGdFZ1hOUG9GQVNhWVI1NlFEWHZ5WlROck9jbmJwTTVqdnZFcnBqbGhqd3ZVNG15NVc2YWNmLzdsUDRHTi9mUm9BVFlrL2V3VkpWZlNBSGNqMEU0Uk5PNUNhQjJTTzZCTjVZZmI4TUxHU0hpa2tJQkFGRUR4akNGdFlhUjRvRHo4VzA3S1hwZXM3d0xWTWcxbmtDRHRWT1d6SHZ0L05qSDBwaHlGM2owbGpJenVNYU5LVzArZllaRGlrVWxWRGJMMC8yS2xtVkxSZll0QkRyRWZodVBiNnZXQ1hjNU5hZjVNVEVTR3FRTGZFOEd4S2ZhTXd6UTlrYVdQNmJmSy9oUzNOYTJ2M0ZrMEFSQlNXWjZQQURBYWw2UzM5Tk8rTVJ5aEVOd0N4MXd3b2V4V1VhWG1BOUNzaXpkcGx0UDdaWXgzbFpQeng1MUUrdTVNQThuRE1FS1hGTmhNOURrQnhvNFg4Q0JrcjBGMzVYM2dPK3o4c1IrOG0ybUU0MU90d3Jya1J6azBTcStacVk3dVlJMStQVWtXMUJCY2pLWlF4ZGQvZWlyNFJ3M2ppbG9SRXZlUFBud0xOUjdkcDcxTEZrMFZlMWlGcmhrUHpjN1ZzTFFiSUFqOEVnbFh1UGFFKzZySUN5N2YyQjNBU1FwKzBPaXUwaDkybUxGY252Yjh3TXdzS2dIVldoMkorZE1MSTZkbloxeVF2L3hITTJSTkdFN1gyTitBRHpsYlRQbHVJZFBIeHhFOFNWeFpGNFpSYXk0M2I5K1RwYzNObjFoVHZtTzZ5SGVwYkJDanJLTCtBREIzT0ZzaVFCYW42WHpKUFdjLzZjWVF2YVhjYk4yVTRFRGUyZWxXZXBUdW1QeGdROTErUFNsS2p0K3NYN1QzbzVxd1paNWlCQUpFNEdHUy9kd0ZZSkxrNHE4OXVwa2xNZ2FBcjhoOXpMdzZDSExrOHlrUnVRcDNSTS82UFRkUmxTYWU5TnVacytDek9sYXBQZ0lKQjdqQ0FqSXpSejRiYUJsaE5GUDl3cEZEYXNNRk51dDdsemxhMWZleFNQTmxxN3FLWWtCRlJmc0VRTHV3dVM0ZFloandReFdseEpNRW90bXl5T2Z2ZWFhYW94eGxJQ1N5YXNqSDFtMG1HYWlxWWhSQmN4M0ZWZHZrTkRteCs1d2dBVENYZGJuS2JVdE9qWVRyM2V6cHQ4U3pMdURwV3FZUGRtajVncVBPZ096bjNreXlyL0R5SlZGMnNlUmRCOXlBQTY5aHZ3eG4yU3MyVDVpcUVjdHNSRXBZQ2tHODF6aVQ5TnhaS1RoT29kM3djUlBUTlBCVnFNL0t5eFNmQVBMcTJ1WWtsb2VqRnBlQ2tvQnNmOTM4MlVpTGlqNkVUaU5QNmV6UjQvSWhXOVEwWlAzQzlXdzFrM29aTnRWQnlMNU96c0F1eDJkZE9kT2w0d0d3QkpDbnRPRGFGck1NaURBN0NWK3pIWHdLcXd2d2Zla3pFRlBOdUZUenVtYU1mSk5hY3ltSTVEMHNiUEtmVXBDL1JmUm1ZZmg5Um0wMnJ6eUVXdFFzRjNKRlppeXEwcU1GSVYwNHFZUWZkcGxtM2Z0b01LeDdLOXcrNG1nTU54bHREcnZJZk91SHhvcEtER2UzaHZrOTNwcUNoVHZNZ2svT1J2NjBxeENEMDlJYSs5QkIrVHRrcnNXTis5ZmE2NkhWT3FHbEFKUmUvL0svSmx4VGRwQ3dvZDgxVU53NFZmU29aeEpFNkcyQTNRV001NjhRM0d0L1U2bmEvWkFZUkJvTkd6MExRRjBtVzJWWk52c3JVTm9WdTdsTFdySVFvRGNleUNIaFA0bmIvTVQzYk9mQjIzOE1FS0ZDTGp2bmVWRmI3S2MvZjZ5YXJ2WTNNV0JMM3ZqRDZPUklZdDR0eVdSVGRFYUFuM2VTNVd2K1d4Q1gyK0JBL3BsTEdzUkZUR1BuUTBhRWNUQkMrTkRMR3YxdEhFeSsvSG5sYXk2enJiWGZWa0l0TEdjMkloN0cxb3NtY2dkWFBFa2ZPWWxPcGc1RlBlTXF2ZXBHZEg3MW5ZdHBlRnF5VG5MRk50dHFqRURnck5ra3pDdmxFOXFuV0d6WDRFdnVEcnFiZ2haWDRTKzd6dHBid01uTFZZOGViWmhjUU82SUtxckhqK0ZtcG9xYUs0RzVIT2hNVXhwWG94ZlVSVVBVallXNytoNmNkVko3R01rOCtLeE5iNEJRbmsreVBrOEt2NHhVUUpBUUpSQ0NQQ1JRUnJ0WXd1WHVzVVl6V1QyVCtndXlsOHo5RDA0dU9TUkVPL2tjT3NzMndDYVhvYi9EV3BUbDlSNDZXZXB1UTdybEdpN2dEZzlYd1RFOG9wOXRra1ZleTFlTW5UdStmS2RrcnlyNkdQSFgrRkQ1cHd1UG01ZmlJdEZlZzN2QnJ1Yk9SSzZCWjI3ZDZnaXhkT3dRUWFtU3oyNUsrYTFGd3lRSDJEdXRvV21tRkt1TDV2R3JEMWtZYU1wZ2x5NnRkNFdtckNQVS9IMVB0M2NZR3NsZjVQVlVoS3NNSkxxeXJHMmxwRnNoejZYekJUbTViOHEyMFBVRngyekRLcmdTYURQbzhmR1JFYmJwQlorU3pLSktrL1VhdHlNOE5OV0ZCL0tjQVU0YWo3RWpSY3B4MExtR1V5NDM3dWVJNWFiWDAybnh6cHdZRkhMZ2U5Nmk5ZExNam9sc2lsZzl4YXNoYlM0b292WDBYQk9HVHN3V2p4ZjI1R3ZhNTFIZCttSGF6M2tyRnJpR1hJemFEV1FwMzl4WVFRSzRwNWtQQnFpM2xwdEF0YUZ4OU9oQkhFSzNsbFgxOGRGOGlaYllSVDM0akNwL0EvTGMzMFkwakpCU2RUeFdkTEN0allCUEtVZk16dFNPT0Y5V0tsRG5XQjdnTzNVSk9qTmdYZGl4WCtJUkYyNmcwVzRDZTRteHhscW1kOFJSVWs3MWljbTVqeHFIdkE0Wnh4Nlc1UmdNZnBJa1Bhc1BiWElKWDhxSHR3a2I2UXJqNW9wWU5SK29rYTk4b0lRSWVuSEFSRDlvWFpPK3lzbVVlWURBNFgzQThKRUNYSlkxY2ZScWlDVW1WSzhEcXZtSWFPOElyOUs1eE9KUml4TWV6cUJCMDlLTWxjZ1pycmtwYUhEeVdkNFVmVDQvejgwMk0zWEtad0lsbWNnaXBxN2pNeUpROURETlNKaFF4WGZ2U1czNFhhZFRzU1hpVHIrY1BuRTJzaU9IR2lvSnQ0UVVsRGtGcWpkMnN2WFFvd1hCZnhCdGU4STZmV2RjTnZQUG9XemFncVJrU2dyeEVYRVNHR1FBamkrYVNxN00wdGFSdEljSDV4OWtELzNiVG9pN0RqTldFOHVCWlQ4ZVM5VnBLT3ltRThoQ2VPMStuUk4yWHpmTURrSlhTbG5xcTh2SENsMWZ6RGE3NkI1bnltU1lXM0tpYVJYUEZ5YzhUNFlHWEo1d2ZYUE1mSk8wSndYWUF5M0VINEM2eGtlUUFPa2FSeWZZcFRqR2p5SGw1UXFNZmNLekZyS041OXUyRStGTklwQ1Y5ZXZXazBFd1Y3VksyVUdtVTF5MEpMNkloSmt4QUhwbm5sNmQvUHZORTZGZmRFdzllR1FNVjRrTllHR2txbXduMU5NdnlaVmVYLzlqYzhRcGZnWTBFZ2p5bXgvZVNvMVFRUXBmQjdIdnNzalhZL1Jkd2VzUVpaYjlUVnAxaGxlMVl5WVZSSVd6emFrc0xHRitVVklJcFlPMWJKNktDaXUvZHl0ZjlHai9GNmZQQlJNdTlsOTA1R0s5NldkSy9VVnBhY1hVVzlhZ0hFL0lMMU5uc0NUZ2c5ajkwTE1hUkFhMnVCanQ3ZXZWYm96VzlaVk5COWZGUTUxeVV0bTRRUnNBQUVpVmk5VWdNQ1JkRm8ycG0veFZuZUpTTCt0VkszQ0ZDNFFIZjNvNHpZNnVsTk1FbVk0SDR5Sm5UK3FzcFpMZkZ5THJXbU1CVWlGRk9hckY5MzBGQUlQdzZ6bVJGb0RWUHlCcjYyUTJOZ3dEbjhacU9Hc21SUkdSZXlYTkVmUkd5c3hzdXdrUXdXS1dQVE05ODVjb0RiUVNkcmhZb1BsSExEaHhpaGZWSzJYRUFDaVdwcWdSVGROblZqN1Z3SHUyU0Nzam51WDZpdEtUZ3kxU1BPaFFOMUN1eisrSEFNSVpreGVtbjEwblIrQzFIeVVDWlFCRXRja1UwVExVNkpMbFpMN2dtMUVWam1HVnlzRkVsbUMvNmxZLzlSUzlNK0g4N2QzK0tmYWtjWitkKytUdUt5bWFiUU82eDBtTlIza2NiSk1hdWxLbWlmb1BHems1NnV0TWduaDlJcVNtaENHWHp3TGVzc1pmNlpWOGJBTG1iakxpKzNmNFpBK0tsL3BTVGtRUXh2dGJVdU1wQXpDV0Z5NHJKRFYwb0ovWFhnaEw5QUJiZjBwS1FXSDMwbXVOWmtKRGVlempwR3hzY3RaQytBbk53QUJPQ0ZZUW9XZHZXaWNZenpmVWptRGRiUWpOcFIwU2F3c3BtUzNtemttV2h2L1lxeklhbzZoRHJWN1RnTU9WNUtCcmtXWCtDSWxNS2ZwQmlCcWVlOUE3U0M0N2V0bHovY3N4c2dXcFhJRll2WlpXdDB2bmtyUUNKNmgrdzFwOGtyMUhqNHJwNmhvcE51dEVPU1BydjVMd1g2ZjJtS2xURUl5bmw1R3BMM1RYT21PazlwUHlxOGpYV05nejFqdE02Ny8wM1dxeDdKTDFpMTMrRDRIWjhKMEdwa09Xck9KUjNuOG9CRHhRc0FFZWoyK0c0SUlTeWkzVndGQWlYRlBnMWhjbTRvZmRoYWhXczYrQk1MRVZiYzVyMklML2NNSHRBWkJBVzN3RlBYUVQzam01MzdJaXJ5OTlIcThYYktITlFlZmFpMEtNVWRlVy9UL281MzJiODBCbktOdnJLdk5aak1tWStDRWpnd2RuRmkyQ2lDTjZXQlYwWnE2VWV1eXJBZW9IcW1BZ0pRSFZ0ZHI1MDNMdlk5NmNwN2twMUNTYzludXJpc0lwT3hvN1ppREU1RWFxaUlMT3krQ1Q5WVZOV3lxZktxOUd1eUQwYkJMaTRxNmh0bzROWXB5cngwcU1Cdzl1cHNVb1VpU0Z0cXJEc2k0WTZyRGF0NXUrdjhnWnlaMHhkSW16Tzc2T0ttZktBR1pyMUNkRUJWUG5GdzNuSHJVbjdPQ2huVC9lbldNR1RodGdGdzMwaThLVXAvT3htbHBpR0daVlN5aW5DM1FKSEJMamgvT2JMb2lDa2NVUDNNS0lpYmwyOGQyTmpJZnZzR0hnUE82VTlQL2FoeHJLVDFtVXhpZnlhaHNuY2t0NFcyU2JoclE0RUIrRmlvbDlhVU9BT3B0ZnhFYXF5SEprUTU1TnZSdTZRdHowaUFCUkd1MTJSSnNPRStoQml0WHVZeHJrV2MyU0pxVVdhOFhVZjNPQ2ZKelBEZExmTGhIQ1Zub3FzQThkUkJkVEtVNUU4YStvVkVkeDhubHBHWWtOOEtJOEtHam1KdmFtMDdBT2FISDkwbEp4QU0wZmNKaSttczlQaHQ5RzVSeG5EamhYOHhZTFNGcmRzRVMzVG8xVzJCTDBVb2hHVVkzZVhXVU5DUHJncVg3eWdZbCtMdFVjSSt1U3krdnZEWUVxRTREcERib3RmRklHUEtmNE5xWWZyTzQ0SEtFbmNZZTBUZThmQnV4NnNuRDBZSHJZU3ZPejJ6NDZwNVI3dHArbGhac1NxVWFDZElabkpiZVdzbG9pYnMwcjk5OWZReEVoZnVuT1MzZ1h6SlZvSlVEb2NBR080UzI3VkE1bmd3MTF1Q2Y5U2ppSFdUVUl6TG11bUh1WjVJUHNvUjM1bElNSnJIdzR0K0JnTldyVklFL2lFeW13eVg4ZEUybmZ2MVlMMWQwdnU3b3oycVd4ZkpSSTlRd1U3OTJ4ZkNHU2NwUFMwcC9iUnkwQWgyZmJyT1oyZXN5MVgxYXZ1cEQ2UjRyUkRubXJ5LzdkWmsxbFo3UlBOS1ZNUFpLUXFQUjNRR2g3WjhYa1BVMEVxMzlGd2QxTHhjcTZJNlJHNi9jNjdxVkFoa2ZzSkVwZ0tva2xkbHhTcS9FYnlEREZ4OVlLd2F2NVZaZW0wTVgydFJmMnc2M3VPVDQ3d0t1bEtGVzc5L0lzQk9Nb0tRR1ZMMnd6SUZTelM2NzcrdkxBeklWVlorRGxSMThOcnVCSVRrTEE1QVAxWHNmak5PYnZjT1BTMDVpNG16TWp5YWN6TXV6UG5aTVhlY25kSm0wckdiUUR6aEM0ZXBDaE92cXVWNC9MRlEzVnhua0xKaG1JeHBscDI1UG1FVmhyRkZUQ0pYTTBKQmNtTDF0T2lHcmtpREpDQjNkanJGYUlxcUxGeVFVYWVNNWhJV2tmTDhuejMrZEMrdG5QL09YbmRhWXB5eVkrUDhDOFpzVFIvVFlmNXFwd3EzWU5rMFgxblZ1aG1EcDRWNGZqaEVuZXppUzArekNrdk03TGsyVit3MCtHMVlzdVZ5M2ZWbXlydkFEZWZPclpsZlc0UDZRRSs5aXpDMXhKbWZFcTU2SDRkSmlkTkxDbmFMNTZVSXNpYTNHRVpQSytNcjlDMDdEZzBsdUI4VHozODZmS3RiakkyZXBzZzlxNUU3Nk9OVjl5alRsZktXTDI1d0xVV3BVekpoQWdkbGVJd1FTS1g1V0dUdjVGOGVFMjc1QXdhN1NhTXBCUHZxckxSVWVXbUl5NDBjM1VwQXVsdlNZaTZVR29BMDBYV0hvU05QcDg5Z2Y2VnUvdkVzUE91a3VNNlVnbVFyMmpaYklMcTd6dEkzWmNkVkFEN1hNVzd2QWxzZDIvYzNnZ3MrQkRlcTBlRTZYOHFRMUZnbWI5Z2dCNitIdmlLWlE9PSIsInMiOiIyOTA0ODQ2MTU3NzBkZGU0IiwiaXYiOiJjY2RhZjQ4NzU4ZGRlYzFiOGViYTI1ZDIxN2E5OWNiOCJ9",
            "site": "https://www.roblox.com",
            "userbrowser": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        }
        payload[f'data[blob]'] = self.blob
        response = self.session.post(
            f'https://arkoselabs.roblox.com/fc/gt2/public_key/476068BF-9607-4799-B53D-966BE98E2B81',
            headers=headers,
            data=payload
        )
        print(response.text)
        return json.loads(response.text)

    def _send_callback(self, data: dict):
        a, b = str(time.time()).split(".")
        self.ts = str(a + b[0:5])
        res = self.session.post(
            f'https://arkoselabs.roblox.com/fc/a/',
            headers={
                "sec-ch-ua-platform": "\"Windows\"",
                "cache-control": "no-cache",
                "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
                "sec-ch-ua-mobile": "?0",
                'x-newrelic-timestamp': self.ts,
                "x-requested-with": "XMLHttpRequest",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
                "accept": "*/*",
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                'origin': "https://www.roblox.com/",
                "sec-fetch-site": "same-site",
                "sec-fetch-mode": "cors",
                "sec-fetch-dest": "empty",
                "accept-encoding": "gzip, deflate, br, zstd",
                "accept-language": "en-US,en;q=0.9",
                "referer": self.referer_url_long,
            },
            data=data
        )

    def _get_game(self):
        a, b = str(time.time()).split(".")
        self.ts = str(a + b[0:5])
        response = self.session.post(
            "https://arkoselabs.roblox.com/fc/a/",
            headers={
                "sec-ch-ua-platform": "\"Windows\"",
                "cache-control": "no-cache",
                "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
                "sec-ch-ua-mobile": "?0",
                "x-newrelic-timestamp": self.ts,
                "x-requested-with": "XMLHttpRequest",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
                "accept": "*/*",
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                'origin': "https://roblox.com/",
                "sec-fetch-site": "same-site",
                "sec-fetch-mode": "cors",
                "sec-fetch-dest": "empty",
                'referer': "https://www.roblox.com/",
                "accept-encoding": "gzip, deflate, br, zstd",
                "accept-language": "en-US,en;q=0.9",
            },
            data={
                'sid': self.sid,
                'session_token': self.session_token,
                'analytics_tier': self.analytics_tier,
                'disableCookies': 'false',
                'render_type': 'canvas',
                'is_compatibility_mode': 'false',
                'category': 'Site URL',
                'action': f'https://arkoselabs.roblox.com/v2/{self.api_ver}/enforcement.{self.enforcement}.html',
            }
        )
        a, b = str(time.time()).split(".")
        self.ts = str(a + b[0:5])
        response = self.session.post(
            f'https://arkoselabs.roblox.com/fc/gfct/',
            headers={
                "sec-ch-ua-platform": "\"Windows\"",
                "cache-control": "no-cache",
                "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
                "sec-ch-ua-mobile": "?0",
                "x-newrelic-timestamp": self.ts,
                "x-requested-with": "XMLHttpRequest",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
                "accept": "*/*",
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                'origin': "https://roblox.com/",
                "sec-fetch-site": "same-site",
                "sec-fetch-mode": "cors",
                "sec-fetch-dest": "empty",
                'referer': "https://roblox.com/",
                "accept-encoding": "gzip, deflate, br, zstd",
                "accept-language": "en-US,en;q=0.9",
            },
            data={
                'token': self.session_token,
                'sid': self.sid,
                'render_type': 'canvas',
                'lang': '',
                'isAudioGame': 'false',
                'is_compatibility_mode': 'false',
                'apiBreakerVersion': 'green',
                'analytics_tier': self.analytics_tier,
            }
        )
        if response.status_code == 200:
            game = Game(self.session, response.json())
        else:
            raise Exception(f"Get game failed: {response.text}")

        return game

    def mainLogic(self):
        response_text = self.get_challenge()
        self.token = response_text['token']
        self.assoc = self._parse_arkose_token()
        self.session_token = self.assoc["token"]
        self.sid = self.assoc["r"]
        self.analytics_tier = self.assoc["at"]
        self.session.get(
            f'https://arkoselabs.roblox.com/fc/init-load/',
            params={
                "session_token": self.session_token
            },
            headers={
                "sec-ch-ua-platform": "\"Windows\"",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
                "sec-ch-ua": "\"Google Chrome\";v=\"137\", \"Not-A.Brand\";v=\"24\", \"Chromium\";v=\"137\"",
                "sec-ch-ua-mobile": "?0",
                "accept": "*/*",
                "sec-fetch-site": "same-origin",
                "sec-fetch-mode": "cors",
                "sec-fetch-dest": "empty",
                'referer': f'https://arkoselabs.roblox.com/v2/{self.api_ver}/enforcement.{self.enforcement}.html',
                "accept-encoding": "gzip, deflate, br, zstd",
                "accept-language": "en-US,en;q=0.9",
            }
        )
        self.referer_url_long = self.session.get(
            f'https://arkoselabs.roblox.com/cdn/fc/assets/ec-game-core/bootstrap/1.27.4/standard/game_core_bootstrap.js',
            headers={
                "sec-ch-ua": "\"Google Chrome\";v=\"137\", \"Not-A.Brand\";v=\"24\", \"Chromium\";v=\"137\"",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"Windows\"",
                "upgrade-insecure-requests": "1",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "sec-fetch-site": "same-origin",
                "sec-fetch-mode": "navigate",
                "sec-fetch-dest": "iframe",
                'referer': f'https://arkoselabs.roblox.com/v2/{self.api_ver}/enforcement.{self.enforcement}.html',
                "accept-encoding": "gzip, deflate, br, zstd",
                "accept-language": "en-US,en;q=0.9",
            },
            params={
                'session': self.session_token,
                'r': self.sid,
                'meta': '3',
                'meta_width': '558',
                'meta_height': '523',
                'metabgclr': 'transparent',
                'metaiconclr': '#555555',
                'guitextcolor': '#000000',
                'pk': "476068BF-9607-4799-B53D-966BE98E2B81",
                'at': self.analytics_tier,
                'ag': '101',
                'cdn_url': f'https://arkoselabs.roblox.com/cdn/fc',
                'surl': f'https://arkoselabs.roblox.com',
                'smurl': f'https://arkoselabs.roblox.com/cdn/fc/assets/style-manager',
                'theme': 'default'
            }
        ).url
        print(self.token)
        if "sup=1|" in self.token:
            self._send_callback({
                'sid': self.sid,
                'session_token': self.session_token,
                'analytics_tier': self.analytics_tier,
                'disableCookies': 'false',
                'render_type': 'canvas',
                'is_compatibility_mode': 'false',
                'category': 'Site URL',
                'action': f'https://arkoselabs.roblox.com/v2/{self.api_ver}/enforcement.{self.enforcement}.html',
            })
            self._send_callback({
                "callback": f"__jsonp_{str(int(time.time() * 1000))}",
                "category": "loaded",
                "action": "game loaded",
                "session_token": self.token,
                "data[public_key]": "476068BF-9607-4799-B53D-966BE98E2B81",
                "data[site]": "https://www.roblox.com"
            })
            return{
                "challenge": None,
                "solved": True,
                "token": self.token,
                "waves": 0,
            }
        else:
            game = self._get_game()


ui = input("Blob: ")
FunCaptcha = CaptchaProcessor("http://afobnianzlyneqp160986-zone-lightning-session-QRnLLUESUEZz-sessTime-1:eexlechpdu@res-ww.lightningproxies.net:9999", f"{ui}")


from typing     import Dict, Any
from celery     import Celery


from src                                import proxyHelper, key_service
from src.browser.fingerprint            import BDA
from src.arkose.challenge               import Challenge
from src.utils.utils                    import Utils
from src.utils.presets                  import Preset
from src.arkose.game                    import Game


celery_app = Celery(
    "src.api.tasks",
    broker="redis://144.76.218.98:6379/0",
    backend="redis://144.76.218.98:6379/0"
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_hijack_root_logger=False,
)


@celery_app.task
def solve(type: str, **kwargs) -> str:
    key: str = kwargs.get("key", None)

    if key == None:
        return {
            "error": "Key is missing."
        }
    
    if not key_service.key_exists(key):
        return {
            "error": "Key does not exists on our database"
        }
    
    keydata = key_service.key_manager.get_key_data(key)
    if (keydata.bought - keydata.solved) < 1:
        return {
            "error": "Key does not have any balance, refill at None"
        }
        

    if type == "FunCaptcha":
        blob = kwargs.get("blob", None)
        site_url = kwargs.get("site_url")
        action = kwargs.get("action")
        proxy = proxyHelper.parse(kwargs.get("proxy", None))

        options, info = Preset.get_options(action)
        settings: Dict[str, Any] = {}
        browser:  Dict[str, Any] = {}

        settings["blob"] = blob
        settings["site"] = site_url
        settings["proxy"] = proxy
        settings["service_url"] = info["surl"]
        settings["cmode"] = info["cmode"]
        settings["public_key"] = info["pkey"]

        browser["language"] = info["lang"]

        headers = {
    'accept': '*/*',
    'accept-language': 'en,de-DE;q=0.9,de;q=0.8,en-US;q=0.7',
    'cache-control': 'no-cache',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'origin': 'https://www.roblox.com',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://www.roblox.com/',
    'sec-ch-ua': '"Not/A)Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'sec-gpc': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
    'x-ark-esync-value': Utils.short_esync(),
}

        bda = BDA(proxy, action, headers['user-agent'], headers['accept-language'])
        bda.update_fingerprint()

        settings["bda"] = bda.encryptedfingerprint

        try:
            challenge: Challenge = Challenge(headers, proxy, settings, browser)
            challenge._pre_load()
            challenge.gt2()

            challenge.session.headers = headers = {
    'accept': '*/*',
    'accept-language': 'en,de-DE;q=0.9,de;q=0.8,en-US;q=0.7',
    'cache-control': 'no-cache',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'origin': 'https://arkoselabs.roblox.com',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://arkoselabs.roblox.com/v2/3.5.0/enforcement.df45d93b7883fed1e47dedac58c1d924.html',
    'sec-ch-ua': '"Not/A)Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'sec-gpc': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
    'x-newrelic-timestamp': Utils.x_ark_esync(),
    'x-requested-with': 'XMLHttpRequest',
    # 'cookie': 'GuestData=UserID=-403029659; .RBXIDCHECK=bef37345-66a6-4006-a342-daed0439ea78; RBXSource=rbx_acquisition_time=06/27/2025 02:18:07&rbx_acquisition_referrer=https://www.roblox.com/games/77520849581419/Actually-Good-JToH-Difficulty-Chart-Obby&rbx_medium=Social&rbx_source=www.roblox.com&rbx_campaign=&rbx_adgroup=&rbx_keyword=&rbx_matchtype=&rbx_send_info=0; RBXEventTrackerV2=CreateDate=07/10/2025 10:29:18&rbxid=579005&browserid=1744825028827006; RBXcb=RBXViralAcquisition%3Dtrue%26RBXSource%3Dtrue%26GoogleAnalytics%3Dtrue; .ROBLOSECURITY=_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_CAEaAhAB.666D1DA23FCC6663637174C4CE770F0986EA2C5B728B982CC222547851841F3C01A28239EBD7F230D12E5419923C021C289BE48423BCF519AC639DAD92DB69D8614FE4A262B88F2C015B28B2ACF854D4DC89301BF0A0CCDA2609A884770870707B6B8C93A599DCA5837695ACD7931237B8C379FFA09AA94784227BDDE6F619465A3854F98D6151B796278EAEECA59656E3CEBEAEB186B657110B9DC418463D856AC89C95A4238064AE0685594649221B7A4FC9404671BFFFB3DB56DA93D5E230298D9C6092E73D58687260EC5482BE8DD88B25DE69C4AAD22590651CA0FB09A68F2EA83B9AD8406E87CDEE78E24F47D72DD0B59053E18403D1FC028105D30EFC9575D01FD3C341101B4B060601C2EBF1705BF045D10A0FFFCA6520C39BCAA9212722588035FB94A88B79C71FA158C9F1282B1B484C96F8F6F3EC498A781B6218367E274AA11A34225FA28833516461222BE740FB7053C43E202AFE2AC6854B87A831D27FC3F79D197BFEE78A84A877C565D89FCE8865F7DBC6DE8BF2BD48E855140E2072F84ADD32835A7F929521BDDE83FB27CAE9BF457F553A9EBBA2E5A581AEC271F22A4F3F70D5056BBBCAAEA89F2B99D590C755F5AA819521E632161365A5418384AC876D62061FFBBADA19208905CC0E728D848731F1DE85492F0EFAD0B5CE7E677D2C37E4E75A54971EB1AB510B3F675EAE6713D27DA6D6441CE613EEDD74E4FAB81C5AB7ED3129A90862A840E9B49568ABB9EB3589003ADE2DF0B1A5E2C2A8683733A271F1EE916B9455188CE52DE2A21781DBBD7FA87A099E869D48E1A3E2DB390D0A70931F14885CC0F0F54195144D5D2036CD7ED4BC1994DD520169D83FC1326DEAC9AFB3CE4964878DF4CC81270D86E25651940E4E0F5916CC9DD83E547BC582EF6FC30C062B0DC5883A86AD8755A7417B3E2C5A68F377F36B455AE3746FA6BFF773ABBF166B5E4C2DF26F796321578DE0E67F5C72D53A60267A5F99EA4F298F07DAD9EC3857D7ADECA5D934F12896F97B10C7B638690E7603FEE8511F16DCF21BD497A7CBEC487ACF412AF4FD49DF0B1BFC31C24F80A6DB19E546E23111ED54AC656773505D300A974BE2F540A1418B0035F539945C4918C740AB50DAD1996D8EF0DF0BA034458D6BA5C732812B57166052D262EBA52859943CA02203C3727C235428291113AED283624EA0ED50; RBXSessionTracker=sessionid=5da78d85-65e3-4c21-97bf-cd1c64760d9c; rbxas=edc485d3fcf8ece9000798e1f1e349d961941c5c8ff4fd69b3e881d4058a9c1b; _cfuvid=2Tcy_EqLJ0qhYnviOGCTm_1P9sZBMu9.hAx5FSqz2z4-1717104076479-0.0.1.1-604800000; rbx-ip2=1; timestamp=175262500614829',
}


            game: Game = Game(challenge)
            game._enforcement_callback()
            game._init_load()
            r = game.gfct()
            print(r)

            return dict({"solution": challenge.full_token})
        except Exception as e:
            print(e)
            return dict({"error": str(e)})
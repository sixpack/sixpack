import unittest
from sixpack.server import is_robot


user_agents = {
    "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)": True,
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/536.28.10 (KHTML, like Gecko) Version/6.0.3 Safari/536.28.10": False,
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; MDDR; .NET4.0C; .NET4.0E)": False,
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)": True,
    "Pingdom.com_bot_version_1.4_(http://www.pingdom.com/)": True,
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.65 Safari/537.31": False
}


class TestBotDetection(unittest.TestCase):

    unit = True

    def test_is_bot(self):
        for ua, is_bot in user_agents.items():
            self.assertEqual(is_robot(ua), is_bot)

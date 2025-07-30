import hashlib
import unittest

from src.cjlutils import EncodeUtil

origins = [
    '1',
    '123',
    '11111111',
    '12121212',
    '121212121',
    '12121212121',
    '111122223333',
    'a',
    'abc',
    '一',
    '一二三',
    '123abc一二三',
    '`-=[]\\;\',/',
    '~!@#$%^&*()_+{}|:"<>?',
    '`-=【】、；，。、',
    '~！@#￥%……&*（）——+「」|："《》？',
    '`~!@#$%^&*()_+-=[]{}|;:,.<>?/\\',
    '饕餮',
    '魑魅魍魉',
    '鳏寡孤独',
    'œ∑´®†¥¨ˆøπ“‘',
    'œ∑®†¥¥øπåß∂ƒ©˙∆˚¬…æΩ≈ç√∫µ≤≥µ¡™£¢∞§¶•ªº–≠',
    'Œ∑´®†Á¨ˆØ∏ÅÍÎÏ©ÓÔ˚Ò…ÆΩ≈Ç√ı˜Â≤≥ı¡™£¢∞§¶•ªº–≠',
]
special_origins = {
    "<unk>", "<pad>", "<s>", "</s>",
    "\'", "\"", "’", "‘", "“", "”", "\\", "?", "%",
    "'⋆⃝",
    "'⚜",
    "'🇹🇷҉͜͡★KILIC⍣✮",
    "'الو ",
    "'乖乖-emo",
    "'𓆩ℍ𝕖𝕒𝕣𝕥",
    "🔥迎中秋特惠买4送1：‍🔥",
    "'The game wheel of fortune you participated in 🇹🇷҉͜͡★KILIC⍣✮",
    "'❥͢",
    "فر☛Ɠɦ᭄يدة ",
    "ᴬᴰᴹᴵᴺ᭄🇰​🇦​🇦​🇳​",
    "🖤ꙵ͜͡✵кяιsтαℓ",
    "✌️𝙛𝙞𝙙𝙚𝙡 𝙝𝙖𝙣✌️ ",
    "Sÿ🔥حاتم",
    "ادم 😎adam",
    "غـᬼ🇵🇸⑅⃝ـᬼزاوية🇪🇬𓅇꙰᭄ɳ",
    "تـ͢آڵــᬼᬼ🫀⑅⃝ـينℳ⁷⁷⁷",
    "♛جہوكُہر♛",
    "👑أّلَمشُـرفُـ🔥ميّأّر𓅇꙰",
    "ÃĤϻẸĎ..ẸĹ.ŤỖŘЌẸЎ♥🔥",
    "𝗕𝗼𝘀𝘀⚡",
    "وكيلͣــͫــͥـͬــͣـᷜــة❣️",
    "نقاء الروح ⭐҉⍣⃝M🧿",
    "⭐نوتيلا⭐",
    "💥ᓚ⅃ᴝ♡Lჺ💥 ",
    "🥂محمོ࿆ــᩧودღ🥂",
    "تـ͢آڵــᬼᬼ🫀⑅⃝ـينℳ⁷⁷⁷",
    "وكيـ𓆩𓃗‌⍣⃝ŤŘẸŇĎـ⍣⃟𖣘 ـل",
    "الساهر ❌ 🇸🇦",
    "مغلق حساب ",
    "𝄠",
    "\'𝄠",
    "🐰⃝꙰🇹𝐴𝑅𝑎🐰⃝꙰🐰agency",
    "🔰",
    "M⑅⃝S",
    "كيداهم🏵️",
    "𝄠𝄠🌠بًــ፝͡ۦحًــر.༄ᵛᶦᵖ🥃",
    "ERDAL🪓21",
    "🎙سـᘓ᭄⑅ــيرينᴬᵈᵐⁱⁿ᭄",
    "💞⋆ᤢⷦ⋆ᤢᷴ⋆ᷢᤢ⋆ⷮᤢ🅒🅘🅦🅐🅝",
    "🎙سـᘓ᭄⑅ــيرينᴬᵈᵐⁱⁿ᭄",
    "M⑅⃝S💔ᤂ᪱ɹ̤ᓗฺใ⎽බᦇɹɹɹمشر فة",
    "『𝕬𝖘𝖎𝖘𝖙𝖆𝖓 𝕰𝖑𝖆",
    "²³⁰",
    "ȷ᎗ᓄ",
    "𓆩ℍ𝕖𝕒𝕣𝕥",
    "⏤͟͟͞𓄂",
    "✪»ⷨ͢🇮🇳𝐌𝐫.𝐀яυη",
    "خي 🇱🇧 وكيل ",
    "✮͜͡❥ɒɛɩɪॖӈѧтսͷ",
    "⚜️Edward♘",
    "🌹🎇 COFFEE LOVELY 💫✨",
    "ťȁ🐯ïǥȩȑ🆚️",
    "草莓🀼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰼󤰧",
    "😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡 😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡😡🐧",
    "family 𝐕❍𝐈𝐂𝐄𔒝AττracτᎥoภ you applied for has passed your joining application.",
    "'حـᬼuـنـ𓆩a𓆪",
    "@✬͜͡𝑨𝒕𝒕𝒊𝒕𝒖𝒅𝒆▓࿐",
    """[الشحن من وكيل الشحن] لقد نجحت في إرسال عملات ذهبية.
المرسل:
مستر علي U.A⚜️（ID：80003）
المستفيد:
 عــᬼ™ـدنـ𓆩𓆪ـآטּ☝（ID：2100744）
الوقت:
2023-11-27 09:54:04 (توقيت السعودية)
مبلغ الشحن (العملات الذهبية):
800""",
    """声音大 玩的🌸	状态‍🔥热 还
可以看🦋下雨""",
    """


    """,
    "حـ",
    " عــᬼ™ـدنـ𓆩𓆪ـآטּ☝（ID：2100744）",
    "ok吖这回真晚安💤",
}


# def encode_md5(message: bytes) -> None | bytes:
class EncodeMd5Test(unittest.TestCase):

    def test_none(self):
        self.assertIsNone(EncodeUtil.encode_md5(None))

    def test_empty(self):
        self.assertEqual(EncodeUtil.encode_md5(b''), hashlib.md5(b'').digest())

    def test_single(self):
        for i in range(256):
            message = bytes([i])
            expected_output = hashlib.md5(message).digest()
            self.assertEqual(EncodeUtil.encode_md5(message), expected_output)

    def test_multiple(self):
        message = b''.join([bytes([i]) for i in range(256)])
        expected_output = hashlib.md5(message).digest()
        self.assertEqual(EncodeUtil.encode_md5(message), expected_output)

    def test_valid_message(self):
        message = b"test message"
        expected_output = hashlib.md5(message).digest()
        self.assertEqual(EncodeUtil.encode_md5(message), expected_output)


class EncodeBase64Test(unittest.TestCase):

    def text_none(self):
        self.assertIsNone(EncodeUtil.encode_base64(None))

    def test_empty(self):
        origin_bytes = b''
        encoded_bytes = EncodeUtil.encode_base64(origin_bytes)
        self.assertEqual(encoded_bytes.decode(), '')

    def test_regular(self):
        original_message = "Hello, World!"
        origin_bytes = original_message.encode()
        encoded_bytes = EncodeUtil.encode_base64(origin_bytes)
        encoded_message = encoded_bytes.decode()
        self.assertEqual(encoded_message, 'SGVsbG8sIFdvcmxkIQ==')


class DecodeBase64Test(unittest.TestCase):

    def test_none(self):
        self.assertIsNone(EncodeUtil.decode_base64(None))

    def test_empty(self):
        encoded_bytes = b''
        decoded_bytes = EncodeUtil.decode_base64(encoded_bytes)
        self.assertEqual(decoded_bytes.decode(), '')

    def test_regular(self):
        encoded_message = 'SGVsbG8sIFdvcmxkIQ=='
        encoded_bytes = encoded_message.encode()
        decoded_bytes = EncodeUtil.decode_base64(encoded_bytes)
        self.assertEqual(decoded_bytes.decode(), "Hello, World!")


class EncodeUrlTest(unittest.TestCase):

    def test_none(self):
        self.assertIsNone(EncodeUtil.encode_url(None))

    def test_empty(self):
        url = ''
        self.assertEqual(EncodeUtil.encode_url(url), '')

    def test_regular(self):
        url = 'https://www.google.com/search?q=python'
        self.assertEqual(EncodeUtil.encode_url(url), 'https%3A%2F%2Fwww.google.com%2Fsearch%3Fq%3Dpython', f'origin url is {url}')


class DecodeUrlTest(unittest.TestCase):

    def test_none(self):
        self.assertIsNone(EncodeUtil.decode_url(None))

    def test_empty(self):
        url = ''
        self.assertEqual(EncodeUtil.decode_url(url), '')

    def test_regular(self):
        url = 'https%3A%2F%2Fwww.google.com%2Fsearch%3Fq%3Dpython'
        self.assertEqual(EncodeUtil.decode_url(url), 'https://www.google.com/search?q=python', f'encoded url is {url}')


if __name__ == '__main__':
    unittest.main()

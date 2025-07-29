"""Imperial Occasions Dictionary
=============================

Contains mappings of imperial calendar dates to culturally significant 
ancient Persian celebrations and commemorative occasions.

This dictionary is structured by month and day, enabling access to
events in both Persian (FA) and English (EN).
These events are drawn from pre-Islamic Zoroastrian and imperial 
traditions, including Nowruz, Sadeh, Mehregan, and other seasonal
festivals aligned with the ancient Aryan worldview.

Format:
-------
IMPERIAL_OCCASIONS = {
    <month_number>: {
        <day_number>: ("<Persian Name>", "<English Name>"),
        ...
    },
    ...
}

Example:
--------
>>> IMPERIAL_OCCASIONS[1][1]
("نوروز", "Nowruz")
"""

IMPERIAL_OCCASIONS = {
    1: {
        1: ("نوروز", "Nowruz"),
        2: ("روز امید و آغاز پادشاهی جمشید", "Hope Day – Founding of Jamshid's Monarchy"),
        6: ("خردادروز - زادروز زرتشت", "Khordad Day - The Birthday of Zoroaster"),
        13: ("سیزده‌به‌در", "Sizdah Bedar – Nature Day"),
        19: ("فروردگان بزرگ", "Farvardegan – Ancestors' Day"),
    },
    2: {
        3: ("جشن گل‌ریزگان", "Golrizgan – Flower Festival"),
        6: ("اردیبهشت‌روز", "Ordibehesht Day"),
        15: ("جشن اردیبهشتگان", "Ordibeheshtgan Festival"),
        19: ("زامیادگان", "Zamiyadgan – Earth/Yazata Celebration"),
    },
    3: {
        6: ("خردادروز", "Khordad Day"),
        6: ("جشن نیلوفر", "Nilufar Festival – Water Lily Day"),
        15: ("جشن خردادگان", "Khordadgan Festival"),
    },
    4: {
        6: ("تیرروز", "Tir Day"),
        10: ("تیرگان (آب‌پاشان)", "Tirgan – Water Festival"),
    },
    5: {
        6: ("امردادروز", "Amordad Day"),
        7: ("جشن امردادگان", "Amordadgan Festival"),
    },
    6: {
        6: ("شهریورروز", "Shahrivar Day"),
        15: ("جشن شهریورگان", "Shahrivargan Festival"),
        30: ("گاهنبار شهریورگان", "Shahrivar Gahambar – Festival of Metal and Labor"),
    },
    7: {
        1: ("آبان‌گاه", "Abangah – Prelude to Water Festival"),
        6: ("مهرروز", "Mehr Day"),
        10: ("مهرگان بزرگ", "Great Mehregan Festival"),
        16: ("مهرگان کوچک", "Minor Mehregan"),
    },
    8: {
        6: ("آبان‌روز", "Aban Day"),
        10: ("آبانگان", "Abangan – Water Goddess Festival"),
        26: ("جشن آناهیتا", "Anahita Day – Water Deity Festival"),
    },
    9: {
        6: ("آذرروز", "Azar Day"),
        9: ("آذرگان", "Azargan – Fire Festival"),
        15: ("میانهٔ زمستان", "Mid-Winter Celebration"),
    },
    10: {
        6: ("دِی‌روز", "Dey Day"),
        8: ("جشن دیگان نخست", "First Deygan Festival"),
        15: ("جشن دیگان دوم", "Second Deygan Festival"),
        23: ("جشن دیگان سوم", "Third Deygan Festival"),
    },
    11: {
        2: ("بهمنگان", "Bahmangan – Festival of Good Thought"),
        6: ("بهمن‌روز", "Bahman Day"),
        26: ("سپندارمذگان", "Sepandarmadgan – Women and Earth Day"),
    },
    12: {
        5: ("سپندارمذگان", "Sepandarmadgan – Spenta Armaiti Day"),
        6: ("اسفندروز", "Esfand Day"),
        29: ("چهارشنبه‌سوری", "Chaharshanbe Suri – Fire Jumping Festival"),
        30: ("بهیزَک", "Behizak – Leap Day"),
    },
}

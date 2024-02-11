from environs import Env

# environs kutubxonasidan foydalanish
env = Env()
env.read_env()

# .env fayl ichidan quyidagilarni o'qiymiz
BOT_TOKEN = env.str("BOT_TOKEN")  # Bot toekn
ADMINS = env.list("ADMINS")  # adminlar ro'yxati
IP = env.str("ip")  # Xosting ip manzili

regions_uz = [
    "Toshkent shahri",
    "Namangan viloyati",
    "Toshkent viloyati",
    "Navoiy viloyati",
    "Qoraqalpogʻiston Respublikasi",
    "Qashqadaryo viloyati",
    "Andijon viloyati",
    "Samarqand viloyati",
    "Buxoro viloyati",
    "Sirdaryo viloyati",
    "Fargʻona viloyati",
    "Surxondaryo viloyati",
    "Jizzax viloyati",
    "Xorazm viloyati",
]

regions_ru = [
    "город Ташкент",
    "Наманганская область",
    "Ташкентская область",
    "Навоийская область",
    "Республика Каракалпакстан",
    "Кашкадарьинская область",
    "Андижанская область",
    "Самаркандская область",
    "Бухарская область",
    "Сырдарьинский область",
    "Ферганская область",
    "Сурхандарьинская область",
    "Джизакская область",
    "Хорезмская область"
]

sciences_uz = [
    "ONA TILI",
    "INGLIZ TILI",
    "MATEMATIKA",
    "FIZIKA",
    "KIMYO",
    "TARIX",
    "BIOLOGIYA",
]

sciences_ru = [
    "РОДНОЙ ЯЗЫК",
    "АНГЛИЙСКИЙ ЯЗЫК",
    "МАТЕМАТИКА",
    "ФИЗИКА",
    "ХИМИЯ",
    "ИСТОРИЯ",
    "БИОЛОГИЯ",
]

sciences_dict = {
    "РОДНОЙ ЯЗЫК": "ONA TILI",
    "АНГЛИЙСКИЙ ЯЗЫК": "INGLIZ TILI",
    "МАТЕМАТИКА": "MATEMATIKA",
    "ФИЗИКА": "FIZIKA",
    "ХИМИЯ": "KIMYO",
    "ИСТОРИЯ": "TARIX",
    "БИОЛОГИЯ": "BIOLOGIYA",
}

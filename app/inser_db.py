import sqlite3
import os

# Beállítás: az adatbázis elérési útja a projekt struktúrád alapján
base_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(base_dir)
db_path = os.path.join(project_dir, 'quiz_backend', 'db.sqlite3')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# DATE típusú kérdések: (kérdés_szöveg, helyes_dátum [YYYY-MM-DD])
date_questions = [
    ("Mikor történt az első ember holdra lépése?", "1969-07-20"),
    ("Mikor kezdődött a II. világháború?", "1939-09-01"),
    ("Mikor ért véget a II. világháború?", "1945-09-02"),
    ("Mikor esett le a berlini fal?", "1989-11-09"),
    ("Mikor alapították az ENSZ-t?", "1945-10-24"),
    ("Mikor történt az első számítógépes játék megjelenése?", "1962-11-01"),
    ("Mikor nyitotta meg a Louvre múzeumot?", "1793-08-10"),
    ("Mikor volt az USA függetlenségi napja?", "1776-07-04"),
    ("Mikor indult el az Apollo 11 küldetés?", "1969-07-16"),
    ("Mikor történt a berlini fal leomlása?", "1989-11-09"),
    ("Mikor született Albert Einstein?", "1879-03-14"),
    ("Mikor halt meg Leonardo da Vinci?", "1519-05-02"),
    ("Mikor kezdődött a francia forradalom?", "1789-07-14"),
    ("Mikor indult a Mars-küldetés (2020) a SpaceX által?", "2020-07-30"),
    ("Mikor építették meg a Taj Mahalt?", "1653-01-01"),
    ("Mikor született William Shakespeare?", "1564-04-26"),
    ("Mikor halt meg William Shakespeare?", "1616-04-23"),
    ("Mikor zajlott le az amerikai polgárháború kezdete?", "1861-04-12"),
    ("Mikor véget ért az amerikai polgárháború?", "1865-04-09"),
    ("Mikor indult az első világháború?", "1914-07-28"),
    ("Mikor ért véget az első világháború?", "1918-11-11"),
    ("Mikor született Mahatma Gandhi?", "1869-10-02"),
    ("Mikor halt meg Mahatma Gandhi?", "1948-01-30"),
    ("Mikor alapították az Európai Gazdasági Közösséget?", "1957-03-25"),
    ("Mikor nyitotta meg a Berlin Fal?", "1961-08-13"),
    ("Mikor vált függetlenné India?", "1947-08-15"),
    ("Mikor vált függetlenné Pakistan?", "1947-08-14"),
    ("Mikor történt a Csernobil baleset?", "1986-04-26"),
    ("Mikor alapították a Google-t?", "1998-09-04"),
    ("Mikor zajlott le a Wall Street-i összeomlás (1929)?", "1929-10-24")
]

# STRING típusú kérdések: (kérdés_szöveg, helyes_szöveges_válasz)
string_questions = [
    ("Milyen színű a fű?", "zöld"),
    ("Milyen színű az ég?", "kék"),
    ("Milyen színű a napraforgó?", "sárga"),
    ("Melyik állat a legjobb barát az embernek?", "kutya"),
    ("Melyik gyümölcs piros és kerek?", "alma"),
    ("Melyik város Magyarország fővárosa?", "Budapest"),
    ("Melyik nyelvet beszélik Spanyolországban?", "spanyol"),
    ("Melyik város Franciaország fővárosa?", "Párizs"),
    ("Melyik évszakban hull a hó?", "tél"),
    ("Milyen irányba fúj a keleti szél?", "kelet"),
    ("Melyik kávéfajta a legnépszerűbb?", "arabica"),
    ("Mi a fővárosa Japánnak?", "Tokió"),
    ("Miből készül az üveg?", "szilícium-dioxid"),
    ("Melyik sportágban játszanak 22 játékossal egy csapatban?", "foci"),
    ("Milyen színű az alma, ha érett?", "piros"),
    ("Melyik országban található a Colosseum?", "Olaszország"),
    ("Melyik híres festő alkotta a Mona Lisát?", "Leonardo da Vinci"),
    ("Melyik bolygó a 'vörös bolygó'?", "Mars"),
    ("Melyik állat a legnagyobb a szárazföldön?", "elefánt"),
    ("Melyik gyümölcs ismert magas rosttartalmáról?", "alma"),
    ("Melyik virág a legnépszerűbb a világon?", "rózsa"),
    ("Melyik országban rendezik meg a Wimbledon tenisz tornát?", "Egyesült Királyság"),
    ("Melyik napot tartják a Föld napjának?", "föld napja"),
    ("Melyik hajnali órát nevezik a nap kezdetének?", "00:00"),
    ("Melyik országban található a Mount Everest?", "Nepál"),
    ("Melyik folyó a leghosszabb a világon?", "Nílus"),
    ("Melyik városban rendezik meg a karnevált Brazíliában?", "Rio de Janeiro"),
    ("Melyik országban található a Big Ben?", "Egyesült Királyság"),
    ("Melyik élőlény a legnagyobb az óceánban?", "kék bálna"),
    ("Melyik sportágban használnak ütőt és labdát udvaron?", "tenisz"),
    ("Mi az ember legnagyobb szerve?", "bőr"),
    ("Milyen színű a narancs?", "narancssárga"),
    ("Mi a világ legnagyobb szárazföldi országának neve?", "Oroszország"),
    ("Melyik országban látható a sarki fény gyakran?", "Izland"),
    ("Milyen nyelvet beszélnek Brazíliában?", "portugál")
]

# MC típusú kérdések: (kérdés_szöveg, helyes_válasz, hibás_válasz1, hibás_válasz2, hibás_válasz3)
mc_questions = [
    ("Milyen színű a levegő?", "kék", "zöld", "piros", "sárga"),
    ("Melyik bolygó a legnagyobb a Naprendszerben?", "Jupiter", "Mars", "Föld", "Venusz"),
    ("Hány kontinens van a világon?", "7", "5", "6", "8"),
    ("Mi az első szám a pozitív egész számok között?", "1", "0", "2", "3"),
    ("Melyik állat a leggyorsabb a világon?", "gepárd", "oroszlán", "medve", "tigris"),
    ("Melyik országban található a Párizsi Eiffel-torony?", "Franciaország", "Németország", "Olaszország", "Spanyolország"),
    ("Melyik sportágban játszanak labdával?", "foci", "kosárlabda", "tenisz", "kézilabda"),
    ("Melyik évben történt az első ember holdra lépése?", "1969", "1959", "1979", "1989"),
    ("Melyik híres festő festette a Mona Lisát?", "Leonardo da Vinci", "Pablo Picasso", "Vincent van Gogh", "Claude Monet"),
    ("Melyik ország fővárosa Budapest?", "Magyarország", "Románia", "Lengyelország", "Bulgária"),
    ("Melyik évben alapították a Microsoftot?", "1975", "1985", "1995", "1965"),
    ("Melyik országban található a Taj Mahal?", "India", "Pakisztán", "Banglades", "Nepál"),
    ("Melyik bolygó ismert gyűrűiről?", "Szaturnusz", "Jupiter", "Uranusz", "Neptunusz"),
    ("Hány nap van egy szökőévben?", "366", "365", "367", "364"),
    ("Melyik a legnagyobb óceán?", "Csendes-óceán", "Atlanti-óceán", "Indiai-óceán", "Jeges-tenger"),
    ("Mi a kémiai jele az aranynak?", "Au", "Ag", "Fe", "Pb"),
    ("Melyik városban rendezik meg az olimpiai játékokat 2020-ban?", "Tokió", "Róma", "Párizs", "London"),
    ("Melyik országban található Machu Picchu?", "Peru", "Brazília", "Argentína", "Chile"),
    ("Hány fok van egy teljes körben?", "360", "180", "90", "270"),
    ("Mi az állat, amelyik az erdő királyának is nevezhető?", "oroszlán", "tigris", "medve", "elefánt"),
    ("Melyik elem a leggyakoribb a Föld kérgében?", "Oxigén", "Szilícium", "Vas", "Alumínium"),
    ("Hány óra van egy napban?", "24", "12", "36", "48"),
    ("Melyik nyelv az egyik hivatalos nyelv az ENSZ-ben?", "francia", "spanyol", "arab", "összes"),
    ("Melyik sportban érik el a legtöbb pontot a profi játékosok?", "kosárlabda", "foci", "röplabda", "tenisz"),
    ("Melyik állat él a sivatagban és képes hosszú ideig vízhiányt tolerálni?", "kamél", "ló", "kecske", "szarvas"),
    ("Melyik a világ legnagyobb szárazföldi állata?", "elefánt", "zsiráf", "oroszlán", "medve"),
    ("Melyik országban rendezik meg a futball világbajnokságot 2018-ban?", "Oroszország", "Brazília", "Németország", "Spanyolország"),
    ("Mi az ember legnagyobb szervének a neve?", "bőr", "szív", "agy", "tüdő"),
    ("Melyik országban található a Colosseum?", "Olaszország", "Franciaország", "Spanyolország", "Görögország"),
    ("Melyik évben alapították a Google-t?", "1998", "2000", "1995", "2002")
]

# Függvény az MC típusú kérdések beszúrására
def insert_mc_question(text, option_a, option_b, option_c, option_d):
    cursor.execute("""
        INSERT INTO quiz_question (text, question_type, option_a, option_b, option_c, option_d, correct_option, times_asked, times_correct)
        VALUES (?, 'MC', ?, ?, ?, ?, 'A', 0, 0)
    """, (text, option_a, option_b, option_c, option_d))

# Függvény a DATE és STRING típusú kérdések beszúrására
def insert_question(text, qtype, correct_answer):
    cursor.execute("""
        INSERT INTO quiz_question (text, question_type, correct_answer, times_asked, times_correct)
        VALUES (?, ?, ?, 0, 0)
    """, (text, qtype, correct_answer))

# Beszúrjuk a DATE típusú kérdéseket
for q in date_questions:
    question_text, correct_date = q
    insert_question(question_text, "DATE", correct_date)

# Beszúrjuk a STRING típusú kérdéseket
for q in string_questions:
    question_text, correct_str = q
    insert_question(question_text, "STRING", correct_str)

# Beszúrjuk az MC típusú kérdéseket
for q in mc_questions:
    question_text, correct_ans, wrong1, wrong2, wrong3 = q
    insert_mc_question(question_text, correct_ans, wrong1, wrong2, wrong3)

conn.commit()
conn.close()

print("A kérdések sikeresen beszúrva az adatbázisba!")

import requests
from bs4 import BeautifulSoup
import time

WEBHOOK_URL = "https://discord.com/api/webhooks/1400926387900125276/_tuRD3GJWnegFeKx9EXblcNtK6xEUHsT0yKlD8iqfIaqOkCVlebfOFdO2WMafYJc84VF"
SØGEORD = "ralph lauren polo"
PRIS_MAKS = 120
TJEK_INTERVAL = 300  # tjek hvert 5. minut


def hent_vinted_scrape():
    base_url = "https://www.vinted.dk/catalog"
    params = {
        "search_text": SØGEORD,
        "price_to": PRIS_MAKS,
        "order": "newest_first"
    }
    headers = {
        "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/114.0.0.0 Safari/537.36")
    }
    try:
        r = requests.get(base_url, params=params, headers=headers, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        items = []
        for item_div in soup.select("div.feed-grid__item"):
            title_tag = item_div.select_one("a.feed-grid__item__title")
            price_tag = item_div.select_one("div.feed-grid__item__price")
            link_tag = item_div.select_one("a.feed-grid__item__link")
            if title_tag and price_tag and link_tag:
                title = title_tag.text.strip().lower()
                price_str = price_tag.text.strip().replace("kr.", "").replace(".", "").strip()
                try:
                    price = int(price_str)
                except:
                    price = 999999
                link = "https://www.vinted.dk" + link_tag.get('href')
                if all(word in title for word in SØGEORD.split()) and price <= PRIS_MAKS:
                    items.append({"title": title_tag.text.strip(),
                                 "price": price, "link": link})
        return items
    except Exception as e:
        print(f"[FEJL] Kunne ikke scrape Vinted: {e}")
        return []


def send_discord_notifikation(item):
    content = (f"🛍️ **Ny vare fundet!**\n"
               f"**{item['title']}**\n"
               f"Pris: {item['price']} kr.\n"
               f"[Se varen her]({item['link']})")
    try:
        r = requests.post(WEBHOOK_URL, json={"content": content})
        r.raise_for_status()
        print(f"[OK] Sendt til Discord: {item['title']}")
    except Exception as e:
        print(f"[FEJL] Kunne ikke sende til Discord: {e}")


def main():
    print("🤖 Starter Vinted-bot...")
    sendt_links = set()
    while True:
        print("🔍 Tjekker Vinted...")
        items = hent_vinted_scrape()
        if not items:
            print("Ingen nye varer fundet lige nu.")
        else:
            for item in items:
                if item["link"] not in sendt_links:
                    send_discord_notifikation(item)
                    sendt_links.add(item["link"])
        print(f"⏳ Venter {TJEK_INTERVAL // 60} minutter...")
        time.sleep(TJEK_INTERVAL)


if __name__ == "__main__":
    main()

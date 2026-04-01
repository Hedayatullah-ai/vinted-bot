import time
import requests
from threading import Thread
from keep_alive import keep_alive
from playwright.sync_api import sync_playwright

WEBHOOK_URL = "DIN_DISCORD_WEBHOOK_HER"

SØGEORD = "ralph lauren polo"
PRIS_MAKS = 120
TJEK_HVERT_MINUT = 5

sendt_links = set()

def hent_items():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        url = f"https://www.vinted.dk/catalog?search_text={SØGEORD}&price_to={PRIS_MAKS}&order=newest_first"
        page.goto(url)

        page.wait_for_selector("div.feed-grid__item")

        items = []
        cards = page.query_selector_all("div.feed-grid__item")

        for card in cards[:20]:
            try:
                title = card.inner_text().lower()

                link_el = card.query_selector("a")
                link = link_el.get_attribute("href")

                price_text = card.inner_text()
                price = int(''.join(filter(str.isdigit, price_text)))

                if price <= PRIS_MAKS and "ralph" in title:
                    items.append({
                        "title": title[:80],
                        "price": price,
                        "link": "https://www.vinted.dk" + link
                    })
            except:
                continue

        browser.close()
        return items


def send_discord(item):
    data = {
        "content": f"🔥 **Ny Ralph Lauren fundet!**\n\n{item['title']}\n💰 {item['price']} kr\n🔗 {item['link']}"
    }

    try:
        r = requests.post(WEBHOOK_URL, json=data)
        print("Sendt:", item["title"])
    except Exception as e:
        print("Discord fejl:", e)


def bot_loop():
    print("🤖 Bot startet...")
    while True:
        try:
            print("🔍 Scanner...")

            items = hent_items()
            print(f"Fundet {len(items)} items")

            for item in items:
                if item["link"] not in sendt_links:
                    send_discord(item)
                    sendt_links.add(item["link"])

        except Exception as e:
            print("FEJL:", e)

        time.sleep(TJEK_HVERT_MINUT * 60)


# Start server + bot
keep_alive()

Thread(target=bot_loop).start()

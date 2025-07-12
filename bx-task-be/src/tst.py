import requests

domains = 'https://idestiny.in', 'https://www.flipkart.com', 'https://www.bestbuy.com', 'https://www.indiaistore.com', 'https://www.apple.com', 'https://www.amazon.in', 'https://www.visible.com', 'https://smartbuy.myimaginestore.com', 'https://www.mobex.in', 'https://www.jiomart.com', 'https://www.futureworldindia.in', 'https://www.reliancedigital.in', 'https://shop.unicornstore.in', 'https://www.poorvika.com', 'https://itechstore.co.in', 'https://inventstore.in', 'https://iplanet.one', 'https://www.vijaysales.com', 'https://gogizmo.in', 'https://www.paiinternational.in', 'https://theinextstore.com', 'https://www.aptronixindia.com', 'https://www.imagineonline.store', 'https://theapplestore.in', 'https://www.designinfo.in', 'https://www.croma.com'

for domain in domains:
    resp = requests.get(f"{domain}/robots.txt")
    print(domain)
    print(resp.text)
    print(" ---------------------------- ")

from src.oxylabs.locations import locations as oll
from src.serp.locations import locations as sl

for serp_location in oll:
    found=False
    for oxylab_location in sl:
        if oxylab_location["country_name"].lower() == serp_location["country"].lower():
            found=True
            break
    if not found:
        print(serp_location["country"], "not found")

for oxylab_location in oll:
    print(F"<option value=\"{oxylab_location["domain"].split('-')[0]}\">{oxylab_location["country"]}</option>")
import requests
from datetime import datetime
import json
from time import sleep
from sql_interaction import sql_cnxn

endpoint = "https://coincodex.com/api/coincodexcoins/get_historical_data_by_slug/%s/2016-01-01/2023-05-08/1?t=5611669"
with requests.session() as s:
    # r = s.get(endpoint)
    # print(r.status_code, r.headers)
    with sql_cnxn() as cnxn:
        crsr = cnxn.cursor()
        crsr.execute("select distinct id, slug from CMCAssets where id not in "
                     "(select distinct CMCAsset from CoinCodexSlugs) "
                     "and cmc_rank is not null "
                     "order by cmc_rank asc")
        slugs = [x for x in crsr.fetchall()]
        for asset_id, slug in slugs:
            for _ in range(3):
                try:
                    r = s.get(endpoint % (slug,))
                    break
                except:
                    print("sleeping...")
                    sleep(30)
                    pass
            else:
                raise Exception("stopped")
            print(slug, r.status_code, r.headers)
            if r.status_code == 200:
                crsr.execute("insert into CoinCodexSlugs (CMCAsset, slug_exists) values (?, 1)", (asset_id,))
                json_data = r.json()
                for row in json_data["data"]:
                    end_time = datetime.strptime(row["time_end"], "%Y-%m-%d %H:%M:%S")
                    crsr.execute("insert into CoinCodexData (CMCAsset, time_end, price_open_usd, price_close_usd, "
                                 "price_high_usd, price_low_usd, volume_usd, market_cap_usd) values (?, ?, ?, ?, ?, ?, ?, "
                                 "?)", (asset_id, end_time, row["price_open_usd"], row["price_close_usd"],
                                        row["price_high_usd"], row["price_low_usd"], row["volume_usd"],
                                        row["market_cap_usd"]))
            elif r.status_code == 404:
                crsr.execute("insert into CoinCodexSlugs (CMCAsset, slug_exists) values (?, 0)", (asset_id,))
            else:
                input('>')
            cnxn.commit()
            # break
            # with open("output.json", 'w', encoding="utf-8") as wf:
            #     wf.write(json.dumps(r.json(), indent=4))

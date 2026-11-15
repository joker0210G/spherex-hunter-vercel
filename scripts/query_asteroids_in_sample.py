import asyncio

from backend.science.identification import SkyBoTClient


async def main():
    client = SkyBoTClient(timeout_sec=15.0)
    # Search 1.5 degree (5400 arcsec) cone around real FITS sample at MJD 60789.7514
    res = await client.query_cone_search(
        mjd=60789.7514,
        ra_deg=160.6152,
        dec_deg=30.6691,
        radius_arcsec=5400.0
    )
    print(f"Total known Solar System objects in field: {res['matched_count']}")
    for m in res['all_matches'][:15]:
        print(f"  Object: {m['object_name']} ({m['object_class']}) | Sep: {m['separation_arcsec']} arcsec | V: {m['v_mag']}")

if __name__ == "__main__":
    asyncio.run(main())


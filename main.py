from getReleases import get_upcoming_releases

if __name__ == "__main__":
    for ev in get_upcoming_releases():
        print(f"{ev['datetime']} — {ev['indicator']}")
        print(f"  Actual:   {ev['actual']}")
        print(f"  Forecast: {ev['forecast']}")
        print(f"  Previous: {ev['previous']}")
        print(f"  Link:     {ev['link']}")
        print()


# See PyCharm help at https://www.jetbrains.com/help/pycharm/


import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from datetime import datetime
import pytz

# Import fetcher functions
from fetchers.jobless_claims import fetch_jobless_claims
from fetchers.home_sales import fetch_existing_home_sales, fetch_new_home_sales
from fetchers.treasury_auctions import fetch_latest_auction_results
from fetchers.fed_speeches import fetch_fed_speeches
from fetchers.case_shiller import fetch_case_shiller
from fetchers.fomc_minutes import fetch_fomc_minutes
from fetchers.pce import fetch_pce_data
from fetchers.cpi import fetch_cpi_data
from fetchers.umich_sentiment import fetch_umich_sentiment
from fetchers.ism_manufacturing import fetch_ism_manufacturing
from fetchers.ism_services import fetch_ism_services
from fetchers.nfp import fetch_nfp_data
from fetchers.fomc_decision import fetch_fomc_decision
# Import TradingView calendar fetcher
from getReleases import get_tradingview_releases

# Email notifier and AI analysis
from notifier import send_raw_email, send_analysis_email
from ai_analyzer import analyze_release

# Time zone
ET = pytz.timezone("US/Eastern")

scheduler = BackgroundScheduler(timezone=ET)

# Generic on_release handler that accepts fetch_func & its kwargs

def on_release(fetch_func, indicator_name, recipients, **fetch_kwargs):
    """
    Fetch data, send raw email, run AI analysis, send analysis email.
    """
    # 1. Fetch data
    result = fetch_func(**fetch_kwargs)

    # 2. Send raw data email
    send_raw_email(indicator_name, result, recipients)

    # 3. Generate AI analysis
    context = {"name": indicator_name, "data": result}
    analysis = analyze_release(context)

    # 4. Send analysis email
    send_analysis_email(indicator_name, analysis, recipients)


def schedule_release(job_id: str, run_time: datetime, fetch_func, indicator_name: str, recipients: list, **fetch_kwargs):
    """
    Schedule a one-off job at run_time to call on_release with given fetch_func.
    """
    def job():
        on_release(fetch_func, indicator_name, recipients, **fetch_kwargs)

    scheduler.add_job(
        job,
        trigger=DateTrigger(run_date=run_time),
        id=job_id,
        name=job_id,
        misfire_grace_time=120
    )
    print(f"Scheduled {job_id} at {run_time}")


def fetch_te_event(event):
    """
    Identity fetcher for TradingView calendar events; returns the event data dict.
    """
    return event


def schedule_tradingview_events(recipients: list, days_ahead: int = 30):
    """
    Dynamically fetch upcoming events from TradingView and schedule them.
    """
    events = get_tradingview_releases(days_ahead=days_ahead)
    for ev in events:
        indicator = ev['indicator']
        run_time = ev['datetime_et']
        # Create unique job ID
        ts = run_time.strftime('%Y%m%dT%H%M')
        job_id = f"TE_{indicator.replace(' ', '_')}_{ts}"
        # Schedule using the generic on_release
        schedule_release(
            job_id=job_id,
            run_time=run_time,
            fetch_func=fetch_te_event,
            indicator_name=indicator,
            recipients=os.getenv("RECIPIENTS", "team@example.com").split(","),
            event=ev
        )


if __name__ == "__main__":
    # ENV recipients list
    recipients = os.getenv("RECIPIENTS", "team@example.com").split(",")

    # STATIC SCHEDULED JOBS (formulaic):
    from apscheduler.triggers.cron import CronTrigger

    # 1. Weekly Jobless Claims (Thursdays 8:30 AM ET)
    scheduler.add_job(
        lambda: on_release(fetch_jobless_claims, "Jobless Claims", recipients),
        CronTrigger(day_of_week='thu', hour=8, minute=30),
        id='Jobless_Claims_Weekly',
        name='Jobless Claims Weekly',
        misfire_grace_time=120
    )
    print("Scheduled weekly Jobless Claims (Thu 8:30 ET)")

    # 2. Monthly CPI (2nd Wednesday at 8:30 AM ET)
    scheduler.add_job(
        lambda: on_release(fetch_cpi_data, "CPI", recipients),
        CronTrigger(day='8-14', day_of_week='wed', hour=8, minute=30),
        id='CPI_Monthly',
        name='Monthly CPI 2nd Wed',
        misfire_grace_time=120
    )
    print("Scheduled monthly CPI (2nd Wed 8:30 ET)")

    # 3. Monthly Non-Farm Payrolls (1st Friday at 8:30 AM ET)
    scheduler.add_job(
        lambda: on_release(fetch_nfp_data, "Nonfarm Payrolls", recipients),
        CronTrigger(day='1-7', day_of_week='fri', hour=8, minute=30),
        id='NFP_Monthly',
        name='Monthly NFP 1st Fri',
        misfire_grace_time=120
    )
    print("Scheduled monthly NFP (1st Fri 8:30 ET)")

    # 4. Monthly PCE (Last business day at 8:30 AM ET) - approximate with day 28-31
    scheduler.add_job(
        lambda: on_release(fetch_pce_data, "PCE", recipients),
        CronTrigger(day='28-31', day_of_week='mon-fri', hour=8, minute=30),
        id='PCE_Monthly',
        name='Monthly PCE Last BD',
        misfire_grace_time=120
    )
    print("Scheduled monthly PCE (approx last biz day 8:30 ET)")

    # 5. Existing Home Sales (3rd Wednesday at 10:00 AM ET)
    scheduler.add_job(
        lambda: on_release(fetch_existing_home_sales, "Existing Home Sales", recipients),
        CronTrigger(day='15-21', day_of_week='wed', hour=10, minute=0),
        id='Existing_Home_Sales',
        name='Existing Home Sales Monthly',
        misfire_grace_time=120
    )
    print("Scheduled monthly Existing Home Sales (3rd Wed 10:00 ET)")

    # 6. New Home Sales (3rd Wednesday at 10:00 AM ET)
    scheduler.add_job(
        lambda: on_release(fetch_new_home_sales, "New Home Sales", recipients),
        CronTrigger(day='15-21', day_of_week='wed', hour=10, minute=0),
        id='New_Home_Sales',
        name='New Home Sales Monthly',
        misfire_grace_time=120
    )
    print("Scheduled monthly New Home Sales (3rd Wed 10:00 ET)")

    # 7. Treasury Auctions (weekly auctions vary by security) - poll daily at 2:00 PM ET
    scheduler.add_job(
        lambda: on_release(fetch_latest_auction_results, "Treasury Auction Results", recipients),
        CronTrigger(hour=14, minute=0),
        id='Treasury_Auctions_Daily',
        name='Daily Treasury Auction Poll',
        misfire_grace_time=120
    )
    print("Scheduled daily Treasury Auction polling (2:00 PM ET)")

    # DYNAMIC TRADINGVIEW EVENTS
    schedule_tradingview_events(
        recipients=recipients,
        days_ahead=30
    )

    # Start scheduler
    scheduler.start()
    print("Scheduler started. Press Ctrl+C to exit.")
    try:
        import time
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()

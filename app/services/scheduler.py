from apscheduler.schedulers.background import BackgroundScheduler


def start_sync_scheduler(sync_callable, hours: int = 1):
    scheduler = BackgroundScheduler()
    scheduler.add_job(sync_callable, "interval", hours=hours, id="gmail-sync", replace_existing=True)
    scheduler.start()
    return scheduler
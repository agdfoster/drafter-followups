from datetime import date, timedelta, datetime



fromdate = datetime.fromtimestamp(1497497412).date()
todate = datetime.fromtimestamp(1498697372).date()
daygenerator = (fromdate + timedelta(x + 1) for x in range((todate - fromdate).days))
print(sum(1 for day in daygenerator if day.weekday() < 5))
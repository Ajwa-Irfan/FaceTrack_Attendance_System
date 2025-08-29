from calendar import Calendar
from datetime import date
from django.shortcuts import get_object_or_404, render
from attendance_app.models import Member, Attendance

WEEKEND = {5, 6} 

def _six_weeks(cal, year, month):
    weeks = cal.monthdatescalendar(year, month)  
    while len(weeks) < 6:
        last_day = weeks[-1][-1]
        next_week = [last_day]  
        next_week = []
        d = last_day
        for _ in range(7):
            d = d.replace(day=d.day)  
        weeks.append(weeks[-1])
        break
    return weeks[:6]

def yearly_attendance(request, member_id):
    yr = int(request.GET.get("year", date.today().year))
    member = get_object_or_404(Member, pk=member_id)

    att_qs = Attendance.objects.filter(member=member, date__year=yr).only("date")
    present_days = {a.date for a in att_qs}

    cal = Calendar(firstweekday=6)  
    months = []

    for m in range(1, 13):
        weeks = cal.monthdatescalendar(yr, m)
        if len(weeks) < 6:
            while len(weeks) < 6:
                weeks.append([weeks[-1][-1] for _ in range(7)])
        elif len(weeks) > 6:
            weeks = weeks[:6]

        matrix = []
        for week in weeks:
            row = []
            for d in week:
                if d.month != m:
                    row.append({"blank": True})
                else:
                    status = "P" if d in present_days else "A"
                    row.append({
                        "blank": False,
                        "date": d.isoformat(),
                        "day": d.day,
                        "weekend": d.weekday() in WEEKEND,
                        "status": status,
                        "status_label": "Present" if status == "P" else "Absent",
                    })
            matrix.append(row)

        months.append({
            "name": date(yr, m, 1).strftime("%B"),
            "weeks": matrix, 
        })

    working_days = len(present_days)
    stats = {
        "leave_days": 0,
        "working_days": working_days,
        "sick_days": 0,
        "vacation_days": 0,
        "bereavement_days": 0,
        "other_days": 0,
    }

    year_choices = list(range(yr - 2, yr + 3))

    return render(request, "attendance_app/admin/employee_yearly_log.html", {
        "employee": member,     
        "year": yr,
        "year_choices": year_choices,
        "months": months,
        "stats": stats,
    })
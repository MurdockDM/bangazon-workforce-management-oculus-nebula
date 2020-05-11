import sqlite3
from django.shortcuts import render
from hrapp.models import Department, model_factory
from ..connection import Connection


def department_list(request):
    if request.method == 'GET':
        with sqlite3.connect(Connection.db_path) as conn:
            conn.row_factory = model_factory(Department)
            db_cursor = conn.cursor()

            db_cursor.execute("""
            select
                d.id,
                d.department_name,
                d.budget,
                e.start_date,
                e.is_supervisor
            from hrapp_department d
            """)

            all_departments = db_cursor.fetchall()



    template = 'employees/employees_list.html'
    context = {
        'employees': all_employees
    }

    return render(request, template, context)

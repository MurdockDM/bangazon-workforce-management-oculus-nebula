import sqlite3
from django.urls import reverse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from hrapp.models import TrainingProgram, Employee, TrainingProgramEmployee
from hrapp.models import model_factory
from ..connection import Connection


def create_training_program(cursor, row):
    _row = sqlite3.Row(cursor, row)

    training_program = TrainingProgram()
    training_program.id = _row["id"]
    training_program.title = _row["title"]
    training_program.start_date = _row["start_date"]
    training_program.end_date = _row["end_date"]
    training_program.capacity = _row["capacity"]

    # training_program.employees = []
    training_program_employee = TrainingProgramEmployee()
    training_program_employee.id = _row["id"]
    training_program_employee.employee_id = _row["employee_id"]
    training_program_employee.training_program_id = _row["training_program_id"]

    employee = Employee()
    employee.id = _row["employee_id"]
    employee.first_name = _row["first_name"]
    employee.last_name = _row["last_name"]
    employee.start_date = _row["start_date"]
    employee.is_supervisor = _row["is_supervisor"]

    # return (training_program, employee,)
    # training_program.training_program_employee = training_program
    training_program.employee = employee
    training_program.training_program_employee = training_program_employee
    return training_program


def get_training_program(training_program_id):
    with sqlite3.connect(Connection.db_path) as conn:
        conn.row_factory = create_training_program
        db_cursor = conn.cursor()

        db_cursor.execute("""
        SELECT
            tp.id,
            tp.title,
            tp.start_date,
            tp.end_date,
            tp.capacity,
            e.id,
            e.first_name,
            e.last_name,
            e.start_date,
            e.is_supervisor,
            etp.employee_id,
            etp.training_program_id
        FROM hrapp_trainingprogramemployee etp
        JOIN hrapp_trainingprogram tp ON tp.id = etp.training_program_id
        JOIN hrapp_employee e ON etp.training_program_id = tp.id
        WHERE tp.id = ?
        """, (training_program_id,))
        return db_cursor.fetchone()




def attendee_list(request, training_program_id):
    with sqlite3.connect(Connection.db_path) as conn:
        conn.row_factory = model_factory(TrainingProgram)
        db_cursor = conn.cursor()
        db_cursor.execute("""
        SELECT
             tp.id,
             tp.title,
             tp.start_date,
             tp.end_date,
             tp.capacity,
             e.id employee_id,
             e.first_name,
             e.last_name,
             e.start_date,
             etp.id,
             etp.employee_id,
             etp.training_program_id
         FROM hrapp_trainingprogramemployee etp
         JOIN hrapp_trainingprogram tp ON tp.id = etp.training_program_id
         JOIN hrapp_employee e ON etp.employee_id = e.id
        WHERE tp.id = ?
        """, (training_program_id,))
        data = db_cursor.fetchone()
        all_attendees = {}

        for item in data:
            if item.training_program_employee.employee_id not in all_attendees:
                all_attendees[item.training_program_employee.employee_id] = item.employee
                all_attendees.append(item)
            else:
                all_attendees[item.training_program_employee.employee_id].append(item)

        template = 'training_programs/training_program_details.html'
        context = {
            'all_attendees': all_attendees
        }
        return render(request, template, context)







@login_required
def training_program_details(request, training_program_id):
    if request.method == 'GET':
        training_program = get_training_program(training_program_id)
        template = 'training_programs/training_program_details.html'
        context = {
            "training_program": training_program
        }
        return render(request, template, context)

    elif request.method == 'POST':
        form_data = request.POST
        if (
            "actual_method" in form_data
            and form_data["actual_method"] == "PUT"
        ):
            with sqlite3.connect(Connection.db_path) as conn:
                db_cursor = conn.cursor()
                db_cursor.execute("""
                    UPDATE hrapp_trainingprogram
                    SET title = ?,
                        start_date = ?,
                        end_date = ?,
                        capacity = ?
                    WHERE id = ?
                """,
                    (form_data['title'], form_data['start_date'], form_data['end_date'],
                        form_data['capacity'], training_program_id,))
            return redirect(reverse('hrapp:trainingprograms'))

        if (
            "actual_method" in form_data and form_data["actual_method"] == "DELETE"
        ):
            with sqlite3.connect(Connection.db_path) as conn:
                db_cursor = conn.cursor()
                db_cursor.execute("""
                DELETE FROM hrapp_trainingprogram
                WHERE id = ?
                """, (training_program_id))
            return redirect(reverse('hrapp:trainingprograms'))

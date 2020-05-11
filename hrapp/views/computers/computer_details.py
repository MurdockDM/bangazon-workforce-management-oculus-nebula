import sqlite3
from django.urls import reverse
from django.shortcuts import redirect, render
from hrapp.models import model_factory, Computer
from ..connection import Connection

def get_computer(computer_id):
    #connect to the database
    with sqlite3.connect(Connection.db_path) as conn:
        #set row parameters and then set up the database cursor
        conn.row_factory = model_factory(Computer)
        db_cursor = conn.cursor()

        #database select
        db_cursor.execute("""
            SELECT
                c.id,
                c.make,
                c.manufacturer,
                c.purchase_date,
                c.decommission_date,
                ec.assign_date,
                ec.unassign_date,
                e.first_name,
                e.last_name
                from hrapp_computer c
                left join hrapp_employeecomputer ec on ec.computer_id = c.id
                left join hrapp_employee e on ec.employee_id = e.id
                where c.id = ?
        """, (computer_id,))
        #return the results from the fetch call
        return db_cursor.fetchone()

def computer_details(request, computer_id):
    print('comput', computer_id)
    if request.method == "GET":
        #fetch that one computer using helper function
        computer = get_computer(computer_id)

        template = 'computers/computer_details.html'
        context = {
            'computer': computer
        }
        #send the template and the computer to the html page
        return render(request, template, context)
    elif request.method == "POST":
        print('computer Id:', computer_id)
        form_data = request.POST
        #check to see if there is a hidden value field with delete and send the id to get deleted
        if (
            "actual_method" in form_data
            and form_data["actual_method"] == 'DELETE'
        ):
            print("yes we made it ya bish")
            with sqlite3.connect(Connection.db_path) as conn:
                db_cursor = conn.cursor()

                db_cursor.execute("""
                    DELETE
                    from
                    hrapp_computer 
                    where id=?

                """, (computer_id,))

            return redirect(reverse('hrapp:computers'))
        


def confirm_computer_delete(request, computer_id):

    template='computers/computer_delete.html'

    context = {
        'computer_id': int(computer_id)
    }

    return render(request, template, context)





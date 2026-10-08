from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from mysqlx import Row
import sqlite3
from db import Database

#age = num
#job = buy
#email = sale
#gender = to_set
#address = notes


db = "COLABA_DATA.db"
con = sqlite3.connect(db)
cur = con.cursor()	

sql = "create table employees(id Integer Primary Key,name text,age text,job text,email text,gender text,address text)"
#cur.execute(sql)
#con.commit()
root = Tk()
root.title('Employee Managent System')
root.geometry('1240x615+0+0')
root.resizable(False,False)
root.configure(bg='#2c3e50')
name = StringVar()
age = StringVar()
job = StringVar()
gender = StringVar()
email = StringVar()

logo = PhotoImage(file='ro (9).png')
res1 = logo.subsample(4,4)
lbl_logo = Label(root, bg= '#2c3e50', image=res1 )

lbl_logo.place(x=5,y=510)







#======== Entries Frame =========
entries_frame = Frame(root, bg='#2c3e50')
entries_frame.place(x=1,y=1,width=360,height=510)
title = Label(entries_frame,text='Employee comoany', font=('calibri',18,'bold'), bg='#2c3e50', fg='white')
title.place(x=10, y=1)

lblName = Label(entries_frame,text="Name", font=('calibri',16), bg='#2c3e50', fg='white')
lblName.place(x=10,y=50)
txtName = Entry(entries_frame,textvariable=name,width=20, font=('calibri',16))
txtName.place(x=120,y=50)

lbljob = Label(entries_frame,text="BUY", font=('calibri',16), bg='#2c3e50', fg='white')
lbljob.place(x=10,y=90)
txtjob = Entry(entries_frame,textvariable=job,width=20, font=('calibri',16))
txtjob.place(x=120,y=90)

lblGender = Label(entries_frame,text="TO_SET", font=('calibri',16), bg='#2c3e50', fg='white')
lblGender.place(x=10,y=130)
compGender = ttk.Combobox(entries_frame,textvariable=gender,state='readonly', width=18, font=('calibri',16))
compGender['values'] = ("Basic", "Side")
compGender.place(x=120,y=130)

lblAge = Label(entries_frame,text="NUM", font=('calibri',16), bg='#2c3e50', fg='white')
lblAge.place(x=10,y=170)
txtAge = Entry(entries_frame,textvariable=age,width=20, font=('calibri',16))
txtAge.place(x=120,y=170)

lblEamil = Label(entries_frame,text="SALE", font=('calibri',16), bg='#2c3e50', fg='white')
lblEamil.place(x=10,y=210)
txtEamil = Entry(entries_frame,textvariable=email,width=20, font=('calibri',16))
txtEamil.place(x=120,y=210)

lblAddress = Label(entries_frame,text="NOTES :", font=('calibri',16), bg='#2c3e50', fg='white')
lblAddress.place(x=10,y=250)
txtAddress = Text(entries_frame,width=30,height=2, font=('calibri',16))
txtAddress.place(x=10,y=290)

#======== [Define] ==========

def day_data():
    file = open("num_day.txt","r")
    day = int(file.read())
    dayStr =str(day + 1)
    file.close()
    file = open("num_day.txt","w")
    file.write(dayStr)
    file.close()
    db_day = "COLABA_DATA_day.db"
    con = sqlite3.connect(db_day)
    cur = con.cursor()
    sql_day = "create table employees"+ dayStr +"(id Integer Primary Key,name text,age text,job text,email text,gender text,address text)"
    cur.execute(sql_day)
    con.commit()
    root_day = Tk()
    root_day.title('Employee Managent System')
    root_day.geometry('1240x615+0+0')
    root_day.resizable(False,False)
    root_day.configure(bg='#2c3e50')

    #age = num
    #job = buy
    #email = sale
    #gender = to_set
    #address = notes

    name_day = StringVar()
    age_day = StringVar()
    job_day = StringVar()
    gender_day = StringVar()
    email_day = StringVar()










    #======== Entries Frame =========
    entries_frame_day = Frame(root_day, bg='#2c3e50')
    entries_frame_day.place(x=1,y=1,width=360,height=510)
    title_day = Label(entries_frame_day,text='Employee comoany', font=('calibri',18,'bold'), bg='#2c3e50', fg='white')
    title_day.place(x=10, y=1)

    lblName_day = Label(entries_frame_day,text="Name", font=('calibri',16), bg='#2c3e50', fg='white')
    lblName_day.place(x=10,y=50)
    txtName_day = Entry(entries_frame_day,textvariable=name_day,width=20, font=('calibri',16))
    txtName_day.place(x=120,y=50)

    lbljob_day = Label(entries_frame_day,text="BUY", font=('calibri',16), bg='#2c3e50', fg='white')
    lbljob_day.place(x=10,y=90)
    txtjob_day = Entry(entries_frame_day,textvariable=job_day,width=20, font=('calibri',16))
    txtjob_day.place(x=120,y=90)

    lblGender_day = Label(entries_frame_day,text="TO_SET", font=('calibri',16), bg='#2c3e50', fg='white')
    lblGender_day.place(x=10,y=130)
    compGender_day = ttk.Combobox(entries_frame_day,textvariable=gender_day,state='readonly', width=18, font=('calibri',16))
    compGender_day['values'] = ("Basic", "Side")
    compGender_day.place(x=120,y=130)

    lblAge_day = Label(entries_frame_day,text="NUM", font=('calibri',16), bg='#2c3e50', fg='white')
    lblAge_day.place(x=10,y=170)
    txtAge_day = Entry(entries_frame_day,textvariable=age_day,width=20, font=('calibri',16))
    txtAge_day.place(x=120,y=170)

    lblEamil_day = Label(entries_frame_day,text="SALE", font=('calibri',16), bg='#2c3e50', fg='white')
    lblEamil_day.place(x=10,y=210)
    txtEamil_day = Entry(entries_frame_day,textvariable=email_day,width=20, font=('calibri',16))
    txtEamil_day.place(x=120,y=210)

    lblAddress_day = Label(entries_frame_day,text="NOTES :", font=('calibri',16), bg='#2c3e50', fg='white')
    lblAddress_day.place(x=10,y=250)
    txtAddress_day = Text(entries_frame_day,width=30,height=2, font=('calibri',16))
    txtAddress_day.place(x=10,y=290)

    #======== [Define] ==========

    def hide_day():
        root_day.geometry("365x515+0+0")
    def show_day ():
        root_day.geometry('1240x615+0+0')
    btnhide_day = Button(entries_frame_day,text='HIDE',bg='white',bd=1,relief=SOLID,cursor='hand2', command=hide_day)
    btnhide_day.place(x=270, y=10)
    btnshow_day = Button(entries_frame_day,text='SHOW',bg='white',bd=1,relief=SOLID,cursor='hand2', command=show_day)
    btnshow_day.place(x=310, y=10)

    def getData_day(event):
        selected_row_day = tv_day.focus()
        data_day = tv.item(selected_row_day)
        global row_day
        row_day = data_day["values"]
        name_day.set(row_day[1])
        age_day.set(row_day[2])
        job_day.set(row_day[3])
        email_day.set(row_day[4])
        gender_day.set(row_day[5])
        txtAddress_day.delete(1.0,END)
        txtAddress_day.insert(END,row_day[6])

    def displayAll_day():
        def fetch_day():
            cur.execute("SELECT * FROM employees"+ dayStr )
            rows_day = cur.fetchall()
            return rows_day
        tv_day.delete(*tv_day.get_children())
        for row_day in fetch_day():
            tv_day.insert("",END,values=row_day)
    def clear_day():
        name_day.set("")
        age_day.set("")
        job_day.set("")
        email_day.set("")
        gender_day.set("")
        txtAddress_day.delete(1.0,END)

    def delete_day():
        def remove_day(id):
            cur.execute("delete from employees"+ dayStr +" where id=?",(id,))
            con.commit()
        remove_day(row_day[0])
        clear_day()
        displayAll_day()

    def add_employee_day():
        name_day = txtName_day.get()
        age_day=txtAge_day.get()
        job_day= txtjob_day.get()
        email_day=txtEamil_day.get()
        gender_day= compGender_day.get()
        address_day = txtAddress_day.get(1.0,END)
        if txtName_day.get() == "" or txtAge_day.get() == "" or txtjob_day.get() == "" or txtEamil_day.get() == "" or compGender_day.get() == "" or txtAddress_day.get(1.0,END) == "":
            messagebox.showerror("Error","please Fill all the Entry")
            return
        cur.execute("insert into employees"+ dayStr +"(name, age,job ,email ,gender , address ) values ('%s', '%s', '%s', '%s', '%s', '%s')"%(name_day,age_day,job_day,email_day,gender_day,address_day))
        con.commit()
        messagebox.showinfo("success","Added new Employee")
        clear_day()
        displayAll_day()
    def update_day():
        name_day = txtName_day.get()
        age_day=txtAge.get()
        job_day= txtjob_day.get()
        email_day=txtEamil_day.get()
        gender_day= compGender_day.get()
        address_day = txtAddress_day.get(1.0,END)
        if txtName_day.get() == "" or txtAge_day.get() == "" or txtjob_day.get() == "" or txtEamil_day.get() == "" or compGender_day.get() == "" or txtAddress_day.get(1.0,END) == "":
            messagebox.showerror("Error","please Fill all the Entry")
            return
            
        def Update2_day(id,name_day,age_day,job_day,email_day,gender_day,address_day):
            cur.execute("update employees"+ dayStr +"set name=?,age=?,job=?,email=?,gender=?,address=? where id=?",
                        (name_day,age_day,job_day,email_day,gender_day,address_day, id))
            con.commit()
        Update2_day(row_day[0],name_day,age_day,job_day,email_day,gender_day,address_day)
        messagebox.showinfo('success','The employee data is ubdate')
        clear_day()
        displayAll_day()
    def sum1_day():
        global sumAll_day
        sumAll_day = 0
        sumAll1_day = 0
        sumAll2_day = 0
        data_day = cur.execute("SELECT * FROM employees"+ dayStr)

        bv_day = ttk.Treeview(tree_frame_day,columns=(1,2,3,4,5,6,7),style="mystyle.Treeview")
        bv_day.heading("1",text="_")
        bv_day.column("1",width="40")
        bv_day.heading("2",text="_")
        bv_day.column("2",width="140")
        
        for sum2_day in data_day:
            sumAll_day += int(sum2_day[2])
        
        data_day = cur.execute("SELECT * FROM employees"+ dayStr )
        for sum3_day in data_day:
            sumAll1_day += int(sum3_day[3])
        data_day = cur.execute("SELECT * FROM employees"+ dayStr )
        for sum4_day in data:
            sumAll2_day += int(sum4_day[4])
        bv_day.heading("3",text=str(sumAll_day))
        bv_day.column("3",width="50")
        bv_day.heading("5",text=str(sumAll2_day))
        bv_day.column("5",width="150")
        bv_day.heading("4",text=str(sumAll1_day))
        bv_day.column("4",width="120")
        bv_day.heading("6",text="_")
        bv_day.column("6",width="90")
        bv_day.heading("7",text="_")
        bv_day.column("7",width="150")
        bv_day['show'] = 'headings'
        bv_day.bind("<ButtonRelease-1>", getData_day)
        bv_day.place(x=1,y=589,height= 20, width=875)
    #======== Buttons Frame =========
    btn_frame_day = Frame(entries_frame_day,bg= '#2c3e50',bd= 1,relief=SOLID)
    btn_frame_day.place(x=10,y=355, width=335,height=150)

    btnAdd_day = Button(btn_frame_day,
                    text='Add Details',
                    width=14,
                    height=1,
                    font=('calibri',16),
                    fg='white',
                    bg='#16a085',
                    bd=0,
                    command= add_employee_day
                    ).place(x=4,y=5)

    btnEdit_day = Button(btn_frame_day,
                    text='Update Details',
                    width=14,
                    height=1,
                    command=update_day,
                    font=('calibri',16),
                    fg='white',
                    bg='#2980b9',
                    bd=0
                    ).place(x=4,y=50)

    btnDelete_day = Button(btn_frame_day,
                    text='Delete Details',
                    width=14,
                    height=1,
                    command=delete_day,
                    font=('calibri',16),
                    fg='white',
                    bg='#c0392b',
                    bd=0
                    ).place(x=170,y=5)

    btnClear_day = Button(btn_frame_day,
                    text='Clear Details',
                    width=14,
                    height=1,
                    command= clear_day,
                    font=('calibri',16),
                    fg='white',
                    bg='#f39c12',
                    bd=0
                    ).place(x=170,y=50)
    btnSumv_day = Button(btn_frame_day,
                    text='SUM',
                    width=14,
                    height=1,
                    command=sum1_day,
                    font=('calibri',16),
                    fg='white',
                    bg='green',
                    bd=0
                    ).place(x=170,y=100)
    #============ [Table Frame] =========

    tree_frame_day = Frame(root_day, bg='white')
    tree_frame_day.place(x=365, y=1, width=875, height=610)
    style_day = ttk.Style()
    style_day.configure("mystyle1.Treeview",font=('calibri',20),rowheight=50)
    style_day.configure("mystyle1.Treeview.Heding", font=('calibri',20))

    tv_day = ttk.Treeview(tree_frame_day,columns=(1,2,3,4,5,6,7),style="mystyle1.Treeview")
    tv_day.heading("1",text="ID")
    tv_day.column("1",width="40")
    tv_day.heading("2",text="Name")
    tv_day.column("2",width="140")
    tv_day.heading("3",text= "Num")
    tv_day.column("3",width="50")
    tv_day.heading("4",text="Buy")
    tv_day.column("4",width="120")
    tv_day.heading("5",text="sale")
    tv_day.column("5",width="150")
    tv_day.heading("6",text="to_set")
    tv_day.column("6",width="90")
    tv_day.heading("7",text="Notes")
    tv_day.column("7",width="150")
    tv_day['show'] = 'headings'
    tv_day.bind("<ButtonRelease-1>", getData_day)
    tv_day.place(x=1,y=1,height= 610, width=875)


    displayAll_day()
    root_day.mainloop()

def hide():
    root.geometry("365x515+0+0")
def show ():
    root.geometry('1240x615+0+0')
btnhide = Button(entries_frame,text='HIDE',bg='white',bd=1,relief=SOLID,cursor='hand2', command=hide)
btnhide.place(x=270, y=10)
btnshow = Button(entries_frame,text='SHOW',bg='white',bd=1,relief=SOLID,cursor='hand2', command=show)
btnshow.place(x=310, y=10)

def getData(event):
    selected_row = tv.focus()
    data = tv.item(selected_row)
    global row
    row = data["values"]
    name.set(row[1])
    age.set(row[2])
    job.set(row[3])
    email.set(row[4])
    gender.set(row[5])
    txtAddress.delete(1.0,END)
    txtAddress.insert(END,row[6])

def displayAll():
    def fetch():
        cur.execute("SELECT * FROM employees")
        rows = cur.fetchall()
        return rows
    tv.delete(*tv.get_children())
    for row in fetch():
        tv.insert("",END,values=row)
def clear():
    name.set("")
    age.set("")
    job.set("")
    email.set("")
    gender.set("")
    txtAddress.delete(1.0,END)

def delete():
    def remove(id):
        cur.execute("delete from employees where id=?",(id,))
        con.commit()
    remove(row[0])
    clear()
    displayAll()

def add_employee():
    name = txtName.get()
    age=txtAge.get()
    job= txtjob.get()
    email=txtEamil.get()
    gender= compGender.get()
    address = txtAddress.get(1.0,END)
    if txtName.get() == "" or txtAge.get() == "" or txtjob.get() == "" or txtEamil.get() == "" or compGender.get() == "" or txtAddress.get(1.0,END) == "":
        messagebox.showerror("Error","please Fill all the Entry")
        return
    cur.execute("insert into employees(name, age,job ,email ,gender , address ) values ('%s', '%s', '%s', '%s', '%s', '%s')"%(name,age,job,email,gender,address))
    con.commit()
    messagebox.showinfo("success","Added new Employee")
    clear()
    displayAll()
def update():
    name = txtName.get()
    age=txtAge.get()
    job= txtjob.get()
    email=txtEamil.get()
    gender= compGender.get()
    address = txtAddress.get(1.0,END)
    if txtName.get() == "" or txtAge.get() == "" or txtjob.get() == "" or txtEamil.get() == "" or compGender.get() == "" or txtAddress.get(1.0,END) == "":
        messagebox.showerror("Error","please Fill all the Entry")
        return
        
    def Update2(id,name,age,job,email,gender,address):
        cur.execute("update employees set name=?,age=?,job=?,email=?,gender=?,address=? where id=?",
                    (name,age,job,email,gender,address, id))
        con.commit()
    Update2(row[0],name,age,job,email,gender,address)
    messagebox.showinfo('success','The employee data is ubdate')
    clear()
    displayAll()
def sum1():
    global sumAll
    sumAll = 0
    sumAll1 = 0
    sumAll2 = 0
    data = cur.execute("SELECT * FROM employees")

    bv = ttk.Treeview(tree_frame,columns=(1,2,3,4,5,6,7),style="mystyle.Treeview")
    bv.heading("1",text="_")
    bv.column("1",width="40")
    bv.heading("2",text="_")
    bv.column("2",width="140")
    
    for sum2 in data:
        sumAll += int(sum2[2])
    
    data = cur.execute("SELECT * FROM employees")
    for sum3 in data:
        sumAll1 += int(sum3[3])
    data = cur.execute("SELECT * FROM employees")
    for sum4 in data:
        sumAll2 += int(sum4[4])
    bv.heading("3",text=str(sumAll))
    bv.column("3",width="50")
    bv.heading("5",text=str(sumAll2))
    bv.column("5",width="150")
    bv.heading("4",text=str(sumAll1))
    bv.column("4",width="120")
    bv.heading("6",text="_")
    bv.column("6",width="90")
    bv.heading("7",text="_")
    bv.column("7",width="150")
    bv['show'] = 'headings'
    tv.bind("<ButtonRelease-1>", getData)
    bv.place(x=1,y=589,height= 20, width=875)
#======== Buttons Frame =========
btn_frame = Frame(entries_frame,bg= '#2c3e50',bd= 1,relief=SOLID)
btn_frame.place(x=10,y=355, width=335,height=150)

btnAdd = Button(btn_frame,
                text='Add Details',
                width=14,
                height=1,
                font=('calibri',16),
                fg='white',
                bg='#16a085',
                bd=0,
                command= add_employee
                ).place(x=4,y=5)

btnEdit = Button(btn_frame,
                text='Update Details',
                width=14,
                height=1,
                command=update,
                font=('calibri',16),
                fg='white',
                bg='#2980b9',
                bd=0
                ).place(x=4,y=50)

btnDelete = Button(btn_frame,
                text='Delete Details',
                width=14,
                height=1,
                command=delete,
                font=('calibri',16),
                fg='white',
                bg='#c0392b',
                bd=0
                ).place(x=170,y=5)

btnClear = Button(btn_frame,
                text='Clear Details',
                width=14,
                height=1,
                command= clear,
                font=('calibri',16),
                fg='white',
                bg='#f39c12',
                bd=0
                ).place(x=170,y=50)
btnSum = Button(btn_frame,
                text='SUM',
                width=14,
                height=1,
                command=sum1,
                font=('calibri',16),
                fg='white',
                bg='green',
                bd=0
                ).place(x=170,y=100)
btnday = Button(btn_frame,
                text='DAY',
                width=14,
                height=1,
                command=day_data,
                font=('calibri',16),
                fg='white',
                bg='blue',
                bd=0
                ).place(x=4,y=100)
#============ [Table Frame] =========

tree_frame = Frame(root, bg='white')
tree_frame.place(x=365, y=1, width=875, height=610)
style = ttk.Style()
style.configure("mystyle.Treeview",font=('calibri',13),rowheight=50)
style.configure("mystyle.Treeview.Heding", font=('calibri',13))

tv = ttk.Treeview(tree_frame,columns=(1,2,3,4,5,6,7),style="mystyle.Treeview")
tv.heading("1",text="ID")
tv.column("1",width="40")
tv.heading("2",text="Name")
tv.column("2",width="140")
tv.heading("3",text= "Num")
tv.column("3",width="50")
tv.heading("4",text="Buy")
tv.column("4",width="120")
tv.heading("5",text="sale")
tv.column("5",width="150")
tv.heading("6",text="to_set")
tv.column("6",width="90")
tv.heading("7",text="Notes")
tv.column("7",width="150")
tv['show'] = 'headings'
tv.bind("<ButtonRelease-1>", getData)
tv.place(x=1,y=1,height= 610, width=875)




displayAll()

root.mainloop()


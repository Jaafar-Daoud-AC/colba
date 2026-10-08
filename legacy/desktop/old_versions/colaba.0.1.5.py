from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from mysqlx import Row
import sqlite3
from db import Database
import time
#age = num
#job = buy
#email = sale
#gender = to_set
#address = notes


db = "COLABA_DATA_day.db"
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









#======== Entries Frame =========
entries_frame = Frame(root, bg='#2c3e50')
entries_frame.place(x=1,y=1,width=360,height=555)
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
    dayStr =str(day + 1 )
    file.close()
    file = open("num_day.txt","w")
    file.write(dayStr)
    file.close()
    sql_day = "create table employees"+ dayStr +"(id Integer Primary Key,name text,age text,job text,email text,gender text,address text)"
    cur.execute(sql_day)
    con.commit()
    root_day = Tk()
    root_day.title('Employee Managent System Day')
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
    txtName_day = Text(entries_frame_day,width=20,height=1, font=('calibri',16))
    txtName_day.place(x=120,y=50)

    lbljob_day = Label(entries_frame_day,text="BUY", font=('calibri',16), bg='#2c3e50', fg='white')
    lbljob_day.place(x=10,y=90)
    txtjob_day = Text(entries_frame_day,width=20,height=1, font=('calibri',16))
    txtjob_day.place(x=120,y=90)

    lblGender_day = Label(entries_frame_day,text="TO_SET", font=('calibri',16), bg='#2c3e50', fg='white')
    lblGender_day.place(x=10,y=130)
    compGender_day = Text(entries_frame_day,width=20,height=1, font=('calibri',16))
    compGender_day.place(x=120,y=130)

    lblAge_day = Label(entries_frame_day,text="NUM", font=('calibri',16), bg='#2c3e50', fg='white')
    lblAge_day.place(x=10,y=170)
    txtAge_day = Text(entries_frame_day,width=20,height=1, font=('calibri',16))
    txtAge_day.place(x=120,y=170)

    lblEamil_day = Label(entries_frame_day,text="SALE", font=('calibri',16), bg='#2c3e50', fg='white')
    lblEamil_day.place(x=10,y=210)
    txtEamil_day = Text(entries_frame_day,width=20,height=1, font=('calibri',16))
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
    def refresh_day():
        displayAll_day()
        clear_day()
    btnRefresh_day = Button(entries_frame_day,text='REFRESH',bg='white',bd=1,relief=SOLID,cursor='hand2', command=refresh_day)
    btnRefresh_day.place(x=210, y=10)
    btnhide_day = Button(entries_frame_day,text='HIDE',bg='white',bd=1,relief=SOLID,cursor='hand2', command=hide_day)
    btnhide_day.place(x=270, y=10)
    btnshow_day = Button(entries_frame_day,text='SHOW',bg='white',bd=1,relief=SOLID,cursor='hand2', command=show_day)
    btnshow_day.place(x=310, y=10)
    


    def getData_day(event):
        txtName_day["state"] = "normal"
        txtjob_day["state"] = "normal"
        txtEamil_day["state"] = "normal"
        compGender_day["state"] = "normal"
        txtAddress_day["state"] = "normal"
        selected_row_day = tv_day.focus()
        data_day = tv_day.item(selected_row_day)
        global row_day
        row_day = data_day["values"]
        txtName_day.delete(1.0,END)
        txtName_day.insert(END,row_day[1])
        txtAge_day.delete(1.0,END)
        txtAge_day.insert(END,row_day[2])
        txtjob_day.delete(1.0,END)
        txtjob_day.insert(END,row_day[3])
        txtEamil_day.delete(1.0,END)
        txtEamil_day.insert(END,row_day[4])
        compGender_day.delete(1.0,END)
        compGender_day.insert(END,row_day[4])
        txtAddress_day.delete(1.0,END)
        txtAddress_day.insert(END,row_day[6])
        txtName_day["state"] = "disabled"
        txtjob_day["state"] = "disabled"
        txtEamil_day["state"] = "disabled"
        compGender_day["state"] = "disabled"
        txtAddress_day["state"] = "disabled"
    
    def displayAll_day():
        def fetch_day():
            cur.execute("SELECT * FROM employees"+ dayStr )
            rows_day = cur.fetchall()
            return rows_day
        tv_day.delete(*tv_day.get_children())
        for row_day in fetch_day():
            tv_day.insert("",END,values=row_day)
    
    def clear_day():
        txtName_day.delete(1.0,END)
        txtAge_day.delete(1.0,END)
        txtjob_day.delete(1.0,END)
        txtEamil_day.delete(1.0,END)
        compGender_day.delete(1.0,END)
        txtAddress_day.delete(1.0,END)
    
    def delete_day():
        def remove_day(id):
            cur_day.execute("delete from employees"+ dayStr +" where id=?",(id,))
            con_day.commit()
        remove_day(row_day[0])
        clear_day()
        displayAll_day()

    def start():
        x = 300
        for x in range(x):
            name_all = cur.execute("SELECT * FROM employees where id = "+str(x))
            for ROW in name_all:
                cur.execute("insert into employees"+ dayStr +"(name , age , job , email , gender , address) values ('%s','%s','%s','%s','%s','%s')"%(ROW[1],ROW[2],ROW[3],ROW[4],ROW[5],ROW[6]))
                con.commit()
        save()
    def save():
        time_day = time.strftime("%d/%M/%Y")
        x_delete = 300
        for x_delete in range(x_delete):
            name_all = cur.execute("SELECT * FROM employees where id = "+str(x_delete))
             
            for ROW in name_all:
                cur.execute("delete from employees where id="+str(x_delete))
                con.commit()
        x_return = 300
        for x_return in range(x_return):
            name_all = cur.execute("SELECT * FROM employees"+ dayStr +" where id = "+str(x_return))
            for ROW in name_all:
                cur.execute("insert into employees(name , age , job , email , gender , address) values ('%s','%s','%s','%s','%s','%s')"%(ROW[1],ROW[2],ROW[3],ROW[4],ROW[5],ROW[6]))
                con.commit()
        cur.execute("insert into employees"+ dayStr +"(id,name , age , job , email , gender , address) values ('%s','%s','%s','%s','%s','%s','%s')"%("9871",time_day,"0","0","0","0","0"))
        con.commit()
        displayAll()
        displayAll_day()

    def update_day():
        name = txtName_day.get(1.0,END)
        age=txtAge_day.get(1.0,END)
        job= txtjob_day.get(1.0,END)
        email=txtEamil_day.get(1.0,END)
        gender= compGender_day.get(1.0,END)
        address = txtAddress_day.get(1.0,END)
        def Update2(id,name,age,job,email,gender,address):
            cur.execute("update employees"+ dayStr +" set name=?,age=?,job=?,email=?,gender=?,address=? where id=?",
                        (name,age,job,email,gender,address, id))
            con.commit()
        Update2(row_day[0],name,age,job,email,gender,address)
        messagebox.showinfo('success','The employee data is ubdate')
        displayAll_day()
        clear_day()
        
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
        for sum4_day in data_day:
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

    btnSave = Button(btn_frame_day,
                    text='Save',
                    width=14,
                    height=1,
                    font=('calibri',16),
                    fg='white',
                    bg='#16a085',
                    bd=0,
                    command= save
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
    btncounting = Button(btn_frame_day,
                text='Counting',
                width=14,
                height=1,
                command=counting,
                font=('calibri',16),
                fg='white',
                bg='green',
                bd=0
                ).place(x=4,y=100)
    #============ [Table Frame] =========

    tree_frame_day = Frame(root_day, bg='white')
    tree_frame_day.place(x=365, y=1, width=875, height=610)
    style_day = ttk.Style()
    style_day.configure("mystyle.Treeview",font=('calibri',13),rowheight=50)
    style_day.configure("mystyle.Treeview.Heding", font=('calibri',13))

    tv_day = ttk.Treeview(tree_frame_day,columns=(1,2,3,4,5,6,7),style="mystyle.Treeview")
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

    start()
    displayAll_day()
    root_day.mainloop()

def counting():
    time_day = time.strftime("%d/%M/%Y")
    file = open("num_counting.txt","r")
    counting = int(file.read())
    countingStr =str(counting + 1 )
    file.close()
    file = open("num_counting.txt","w")
    file.write(countingStr)
    file.close()

    sql_counting = "create table counting"+countingStr+"(id Integer Primary Key,name text,age text,job text,email text,gender text,address text)"
    cur.execute(sql_counting)
    con.commit()
    root_counting = Tk()
    root_counting.title('Employee Managent System Day')
    root_counting.geometry('1240x615+0+0')
    root_counting.resizable(False,False)
    root_counting.configure(bg='#2c3e50')

    #======== Entries Frame =========
    entries_frame_counting = Frame(root_counting, bg='#2c3e50')
    entries_frame_counting.place(x=1,y=1,width=360,height=510)
    title_counting = Label(entries_frame_counting,text='Employee comoany', font=('calibri',18,'bold'), bg='#2c3e50', fg='white')
    title_counting.place(x=10, y=1)

    #======== [Define] ==========

    def hide_day():
        root_counting.geometry("365x515+0+0")
    def show_day ():
        root_counting.geometry('1240x615+0+0')
    def refresh_day():
        displayAll_day()
        clear_day()
    btnRefresh_counting = Button(entries_frame_counting,text='REFRESH',bg='white',bd=1,relief=SOLID,cursor='hand2', command=refresh_day)
    btnRefresh_counting.place(x=210, y=10)
    btnhide_counting= Button(entries_frame_counting,text='HIDE',bg='white',bd=1,relief=SOLID,cursor='hand2', command=hide_day)
    btnhide_counting.place(x=270, y=10)
    btnshow_counting = Button(entries_frame_counting,text='SHOW',bg='white',bd=1,relief=SOLID,cursor='hand2', command=show_day)
    btnshow_counting.place(x=310, y=10)
    
    def counting_start():
        num_Employee = []
        num_Employee2 = []
        num_Employee_counting = []

        v = 300
        for columns in range(v):
            columns_all = cur.execute("SELECT * FROM employees where id = "+str(columns))
            for Row in columns_all:
                num_Employee.append(int(Row[2]))
                g = int(Row[0])
            columns_all1 = cur.execute("SELECT * FROM employees"+countingStr+" where id = "+str(columns))
            for Row in columns_all1:
                num_Employee2.append(int(Row[2]))
        
        for a in range(g):
            print(num_Employee2[a])
            t = num_Employee2[a] - num_Employee[a] 
            num_Employee_counting.append(t)
        print(g)
        x_return = g 
        i = 0
        while i <= x_return:
            name_all = cur.execute("SELECT * FROM employees where id = "+str(i))
            for ROW in name_all:
                cur.execute("insert into counting"+countingStr+"(name , age , job , email , gender , address) values ('%s','%s','%s','%s','%s','%s')"%(ROW[1],num_Employee_counting[i-1],ROW[3],ROW[4],ROW[5],ROW[6]))
                con.commit()
            i+=1
        cur.execute("insert into counting"+ countingStr +"(id,name , age , job , email , gender , address) values ('%s','%s','%s','%s','%s','%s','%s')"%("9871",time_day,"0","0","0","0","0"))
        con.commit()
        print(num_Employee)
        print(num_Employee2)
        print(num_Employee_counting)
        #displayAll_counting()
    counting_start()
    def displayAll_counting():
        def fetch_counting():
            cur.execute("SELECT * FROM counting"+ countingStr )
            rows_counting = cur.fetchall()
            return rows_counting
        tv_counting.delete(*tv_counting.get_children())
        for row_counting in fetch_counting():
            tv_counting.insert("",END,values=row_counting)
    
    def sum1_counting():
        global sumAll_counting
        sumAll_counting = 0
        sumAll1_counting = 0
        sumAll2_counting = 0
        data_counting = cur.execute("SELECT * FROM counting"+ countingStr)

        bv_counting = ttk.Treeview(tree_frame_counting,columns=(1,2,3,4,5,6,7),style="mystyle.Treeview")
        bv_counting.heading("1",text="_")
        bv_counting.column("1",width="40")
        bv_counting.heading("2",text="_")
        bv_counting.column("2",width="140")
        
        for sum2_counting in data_counting:
            sumAll_counting += int(sum2_counting[2])
        
        data_counting = cur.execute("SELECT * FROM counting"+ countingStr )
        for sum3_counting in data_counting:
            sumAll1_counting += int(sum3_counting[3])
        data_counting = cur.execute("SELECT * FROM counting"+ countingStr )
        for sum4_counting in data_counting:
            sumAll2_counting += int(sum4_counting[4])
        bv_counting.heading("3",text=str(sumAll_counting))
        bv_counting.column("3",width="50")
        bv_counting.heading("5",text=str(sumAll2_counting))
        bv_counting.column("5",width="150")
        bv_counting.heading("4",text=str(sumAll1_counting))
        bv_counting.column("4",width="120")
        bv_counting.heading("6",text="_")
        bv_counting.column("6",width="90")
        bv_counting.heading("7",text="_")
        bv_counting.column("7",width="150")
        bv_counting['show'] = 'headings'

        bv_counting.place(x=1,y=409,height= 20, width=875)
    #======== Buttons Frame =========
    btn_frame_counting = Frame(root_counting,bg= '#2c3e50',bd= 1,relief=SOLID)
    btn_frame_counting.place(x=900,y=420, width=335,height=150)

    #============ [Table Frame] =========

    tree_frame_counting = Frame(root_counting, bg='white')
    tree_frame_counting.place(x=535, y=1, width=700, height=410)
    style_counting = ttk.Style()
    style_counting.configure("mystyle.Treeview",font=('calibri',13),rowheight=50)
    style_counting.configure("mystyle.Treeview.Heding", font=('calibri',13))

    tv_counting = ttk.Treeview(tree_frame_counting,columns=(1,2,3,4,5,6,7),style="mystyle.Treeview")
    tv_counting.heading("1",text="ID")
    tv_counting.column("1",width="40")
    tv_counting.heading("2",text="Name")
    tv_counting.column("2",width="140")
    tv_counting.heading("3",text= "Num")
    tv_counting.column("3",width="50")
    tv_counting.heading("4",text="Buy")
    tv_counting.column("4",width="120")
    tv_counting.heading("5",text="sale")
    tv_counting.column("5",width="150")
    tv_counting.heading("6",text="to_set")
    tv_counting.column("6",width="90")
    tv_counting.heading("7",text="Notes")
    tv_counting.column("7",width="100")
    tv_counting['show'] = 'headings'
    tv_counting.place(x=1,y=1,height= 410, width=700)

    btnSum = Button(btn_frame_counting,
                text='SUM',
                width=14,
                height=1,
                command=sum1_counting,
                font=('calibri',16),
                fg='white',
                bg='green',
                bd=0
                ).place(x=170,y=100)
    displayAll_counting()
    root_counting.mainloop()



def hide():
    root.geometry("365x515+0+0")
def show ():
    root.geometry('1240x615+0+0')
def refresh():
    displayAll()
    clear()
btnRefresh = Button(entries_frame,text='REFRESH',bg='white',bd=1,relief=SOLID,cursor='hand2', command=refresh)
btnRefresh.place(x=210, y=10)
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
btn_frame.place(x=10,y=355, width=335,height=500)

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


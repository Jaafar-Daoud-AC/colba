from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import sqlite3
import time
import matplotlib.pyplot as plt
import os

path = os.path.dirname(os.path.abspath(__file__))
path_db = os.path.join(path,"name_DB")
os.makedirs(path_db,exist_ok=True)

#age = num
#job = buy
#email = sale
#gender = to_set
#address = notes

row = None
row_day = None

root = Tk()
root.title('COLABA')
root.geometry('1240x615+0+0')
root.resizable(False,False)
root.configure(bg='#2c3e50')

#======== [Style] ==========
style = ttk.Style()
style.theme_use('clam')
def fixed_map(option):
    return [elm for elm in style.map("Treeview", query_opt=option) if elm[:2] != ("!disabled","!selected")]
style.configure("mystyle.Treeview",font=('calibri',13),rowheight=36,background='#ffffff',fieldbackground='#ffffff',borderwidth=0)
style.configure("mystyle.Treeview.Heading", font=('calibri',13,'bold'),background='#16a085',foreground='white',relief='flat',padding=6)
style.map("mystyle.Treeview",
          foreground=[('selected','white')] + fixed_map("foreground"),
          background=[('selected','#2980b9')] + fixed_map("background"))
style.map("mystyle.Treeview.Heading",background=[('active','#1abc9c')])
style.configure("Vertical.TScrollbar",background='#16a085',troughcolor='#ecf0f1',borderwidth=0,arrowsize=14)
style.configure("TCombobox",padding=4)

#======== [Define] ==========
def to_int(v):
    try:
        return int(float(str(v).strip()))
    except ValueError:
        return 0

def is_num(v):
    try:
        int(str(v).strip())
        return True
    except ValueError:
        return False

def make_tree(parent,height):
    tv = ttk.Treeview(parent,columns=(1,2,3,4,5,6,7),style="mystyle.Treeview")
    tv.heading("1",text="ID")
    tv.column("1",width=50,anchor="center")
    tv.heading("2",text="Name")
    tv.column("2",width=190)
    tv.heading("3",text= "Num")
    tv.column("3",width=70,anchor="center")
    tv.heading("4",text="Buy")
    tv.column("4",width=120,anchor="center")
    tv.heading("5",text="sale")
    tv.column("5",width=130,anchor="center")
    tv.heading("6",text="to_set")
    tv.column("6",width=90,anchor="center")
    tv.heading("7",text="Notes")
    tv.column("7",width=215)
    tv['show'] = 'headings'
    tv.tag_configure('odd',background='#f2f4f4')
    tv.tag_configure('even',background='#ffffff')
    tv.tag_configure('date',background='#f9e79f')
    sb = ttk.Scrollbar(parent,orient=VERTICAL,command=tv.yview)
    tv.configure(yscrollcommand=sb.set)
    tv.place(x=1,y=1,height=height,width=845)
    sb.place(x=848,y=1,height=height,width=24)
    return tv

def fill_tree(tv,rows):
    tv.delete(*tv.get_children())
    i = 0
    for r in rows:
        tag = 'even'
        if i % 2 == 1:
            tag = 'odd'
        if r[0] == 9871:
            tag = 'date'
        tv.insert("",END,values=r,tags=(tag,))
        i+=1

def make_sum(parent,texts,y):
    bv = ttk.Treeview(parent,columns=(1,2,3,4,5,6,7),style="mystyle.Treeview")
    w = [50,190,70,120,130,90,215]
    for a in range(7):
        bv.heading(str(a+1),text=texts[a])
        bv.column(str(a+1),width=w[a],anchor="center")
    bv['show'] = 'headings'
    bv.place(x=1,y=y,height=34,width=845)
    return bv

db = os.path.join(path_db,"Colba.db")
con = sqlite3.connect(db)
cur = con.cursor()

sql = "create table if not exists employees(id Integer Primary Key,name text,age text,job text,email text,gender text,address text)"
cur.execute(sql)
con.commit()

def close_all():
    con.close()
    root.destroy()
root.protocol("WM_DELETE_WINDOW", close_all)

name = StringVar()
age = StringVar()
job = StringVar()
gender = StringVar()
email = StringVar()

def next_num(prefix):
    cur.execute("select name from sqlite_master where type='table' and name like ?",(prefix+"%",))
    nums = [0]
    for t in cur.fetchall():
        n = t[0][len(prefix):]
        if n.isdigit():
            nums.append(int(n))
    return max(nums)+1
def table_exists(table):
    cur.execute("select name from sqlite_master where type='table' and name=?",(table,))
    return cur.fetchone() is not None

#======== Entries Frame =========
entries_frame = Frame(root, bg='#2c3e50')
entries_frame.place(x=1,y=1,width=370,height=555)
title = Label(entries_frame,text='COLABA', font=('calibri',18,'bold'), bg='#2c3e50', fg='#1abc9c')
title.place(x=10, y=1)

lblName = Label(entries_frame,text="Name", font=('calibri',16), bg='#2c3e50', fg='white')
lblName.place(x=10,y=50)
txtName = Entry(entries_frame,textvariable=name,width=20, font=('calibri',16),relief=FLAT,bd=0,highlightthickness=1,highlightbackground='#1f2d3a',highlightcolor='#1abc9c')
txtName.place(x=120,y=50)

lbljob = Label(entries_frame,text="BUY", font=('calibri',16), bg='#2c3e50', fg='white')
lbljob.place(x=10,y=90)
txtjob = Entry(entries_frame,textvariable=job,width=20, font=('calibri',16),relief=FLAT,bd=0,highlightthickness=1,highlightbackground='#1f2d3a',highlightcolor='#1abc9c')
txtjob.place(x=120,y=90)

lblGender = Label(entries_frame,text="TO_SET", font=('calibri',16), bg='#2c3e50', fg='white')
lblGender.place(x=10,y=130)
compGender = ttk.Combobox(entries_frame,textvariable=gender,state='readonly', width=18, font=('calibri',16))
compGender['values'] = ("Basic", "Side")
compGender.place(x=120,y=130)

lblAge = Label(entries_frame,text="NUM", font=('calibri',16), bg='#2c3e50', fg='white')
lblAge.place(x=10,y=170)
txtAge = Entry(entries_frame,textvariable=age,width=20, font=('calibri',16),relief=FLAT,bd=0,highlightthickness=1,highlightbackground='#1f2d3a',highlightcolor='#1abc9c')
txtAge.place(x=120,y=170)

lblEamil = Label(entries_frame,text="SALE", font=('calibri',16), bg='#2c3e50', fg='white')
lblEamil.place(x=10,y=210)
txtEamil = Entry(entries_frame,textvariable=email,width=20, font=('calibri',16),relief=FLAT,bd=0,highlightthickness=1,highlightbackground='#1f2d3a',highlightcolor='#1abc9c')
txtEamil.place(x=120,y=210)

lblAddress = Label(entries_frame,text="NOTES :", font=('calibri',16), bg='#2c3e50', fg='white')
lblAddress.place(x=10,y=250)
txtAddress = Text(entries_frame,width=30,height=2, font=('calibri',16),relief=FLAT,bd=0,highlightthickness=1,highlightbackground='#1f2d3a',highlightcolor='#1abc9c')
txtAddress.place(x=10,y=290)

#======== [Define] ==========

def day_data():
    dayStr = str(next_num("employees"))
    sql_day = "create table employees"+ dayStr +"(id Integer Primary Key,name text,age text,job text,email text,gender text,address text)"
    cur.execute(sql_day)
    con.commit()
    root_day = Toplevel(root)
    root_day.title('COLABA  -  Day '+dayStr)
    root_day.geometry('1240x615+0+0')
    root_day.resizable(False,False)
    root_day.configure(bg='#2c3e50')

    #age = num
    #job = buy
    #email = sale
    #gender = to_set
    #address = notes

    #======== Entries Frame =========
    entries_frame_day = Frame(root_day, bg='#2c3e50')
    entries_frame_day.place(x=1,y=1,width=360,height=510)
    title_day = Label(entries_frame_day,text='COLABA  -  Day '+dayStr, font=('calibri',18,'bold'), bg='#2c3e50', fg='#1abc9c')
    title_day.place(x=10, y=1)

    lblName_day = Label(entries_frame_day,text="Name", font=('calibri',16), bg='#2c3e50', fg='white')
    lblName_day.place(x=10,y=50)
    txtName_day = Text(entries_frame_day,width=20,height=1, font=('calibri',16),relief=FLAT,bd=0,highlightthickness=1,highlightbackground='#1f2d3a',highlightcolor='#1abc9c')
    txtName_day.place(x=120,y=50)

    lbljob_day = Label(entries_frame_day,text="BUY", font=('calibri',16), bg='#2c3e50', fg='white')
    lbljob_day.place(x=10,y=90)
    txtjob_day = Text(entries_frame_day,width=20,height=1, font=('calibri',16),relief=FLAT,bd=0,highlightthickness=1,highlightbackground='#1f2d3a',highlightcolor='#1abc9c')
    txtjob_day.place(x=120,y=90)

    lblGender_day = Label(entries_frame_day,text="TO_SET", font=('calibri',16), bg='#2c3e50', fg='white')
    lblGender_day.place(x=10,y=130)
    compGender_day = Text(entries_frame_day,width=20,height=1, font=('calibri',16),relief=FLAT,bd=0,highlightthickness=1,highlightbackground='#1f2d3a',highlightcolor='#1abc9c')
    compGender_day.place(x=120,y=130)

    lblAge_day = Label(entries_frame_day,text="NUM", font=('calibri',16), bg='#2c3e50', fg='white')
    lblAge_day.place(x=10,y=170)
    txtAge_day = Text(entries_frame_day,width=20,height=1, font=('calibri',16),relief=FLAT,bd=0,highlightthickness=1,highlightbackground='#1f2d3a',highlightcolor='#1abc9c')
    txtAge_day.place(x=120,y=170)

    lblEamil_day = Label(entries_frame_day,text="SALE", font=('calibri',16), bg='#2c3e50', fg='white')
    lblEamil_day.place(x=10,y=210)
    txtEamil_day = Text(entries_frame_day,width=20,height=1, font=('calibri',16),relief=FLAT,bd=0,highlightthickness=1,highlightbackground='#1f2d3a',highlightcolor='#1abc9c')
    txtEamil_day.place(x=120,y=210)

    lblAddress_day = Label(entries_frame_day,text="NOTES :", font=('calibri',16), bg='#2c3e50', fg='white')
    lblAddress_day.place(x=10,y=250)
    txtAddress_day = Text(entries_frame_day,width=30,height=2, font=('calibri',16),relief=FLAT,bd=0,highlightthickness=1,highlightbackground='#1f2d3a',highlightcolor='#1abc9c')
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
        global row_day
        selected_row_day = tv_day.focus()
        data_day = tv_day.item(selected_row_day)
        if not data_day["values"]:
            return
        row_day = cur.execute("select * from employees"+ dayStr +" where id=?",(data_day["values"][0],)).fetchone()
        if row_day is None:
            return
        txtName_day["state"] = "normal"
        txtjob_day["state"] = "normal"
        txtEamil_day["state"] = "normal"
        compGender_day["state"] = "normal"
        txtAddress_day["state"] = "normal"
        txtName_day.delete(1.0,END)
        txtName_day.insert(END,row_day[1])
        txtAge_day.delete(1.0,END)
        txtAge_day.insert(END,row_day[2])
        txtjob_day.delete(1.0,END)
        txtjob_day.insert(END,row_day[3])
        txtEamil_day.delete(1.0,END)
        txtEamil_day.insert(END,row_day[4])
        compGender_day.delete(1.0,END)
        compGender_day.insert(END,row_day[5])
        txtAddress_day.delete(1.0,END)
        txtAddress_day.insert(END,row_day[6])
        txtName_day["state"] = "disabled"
        txtjob_day["state"] = "disabled"
        txtEamil_day["state"] = "disabled"
        compGender_day["state"] = "disabled"
        txtAddress_day["state"] = "disabled"

    def displayAll_day():
        def fetch_day():
            cur.execute("SELECT * FROM employees"+ dayStr +" order by id")
            rows_day = cur.fetchall()
            return rows_day
        fill_tree(tv_day,fetch_day())

    def clear_day():
        global row_day
        row_day = None
        txtName_day["state"] = "normal"
        txtjob_day["state"] = "normal"
        txtEamil_day["state"] = "normal"
        compGender_day["state"] = "normal"
        txtAddress_day["state"] = "normal"
        txtName_day.delete(1.0,END)
        txtAge_day.delete(1.0,END)
        txtjob_day.delete(1.0,END)
        txtEamil_day.delete(1.0,END)
        compGender_day.delete(1.0,END)
        txtAddress_day.delete(1.0,END)
        txtName_day["state"] = "disabled"
        txtjob_day["state"] = "disabled"
        txtEamil_day["state"] = "disabled"
        compGender_day["state"] = "disabled"
        txtAddress_day["state"] = "disabled"

    def delete_day():
        if row_day is None:
            messagebox.showerror("Error","please choose a row",parent=root_day)
            return
        if not messagebox.askyesno("Delete","Delete this row ?",parent=root_day):
            return
        def remove_day(id):
            cur.execute("delete from employees"+ dayStr +" where id=?",(id,))
            con.commit()
        remove_day(row_day[0])
        clear_day()
        displayAll_day()

    def start():
        time_day = time.strftime("%d/%m/%Y")
        cur.execute("insert into employees"+ dayStr +" select * from employees")
        cur.execute("insert or replace into employees"+ dayStr +"(id,name , age , job , email , gender , address) values (9871,?,'0','0','0','0','0')",(time_day,))
        con.commit()
    def save():
        time_day = time.strftime("%d/%m/%Y")
        if not table_exists("counting"+ dayStr):
            if not messagebox.askyesno("Save","Counting is not done yet for this day.\nSave anyway ?",parent=root_day):
                return
        cur.execute("delete from employees")
        cur.execute("insert into employees select * from employees"+ dayStr +" where id < 9871")
        cur.execute("insert or replace into employees"+ dayStr +"(id,name , age , job , email , gender , address) values (9871,?,'0','0','0','0','0')",(time_day,))
        con.commit()
        displayAll()
        displayAll_day()

    def update_day():
        if row_day is None:
            messagebox.showerror("Error","please choose a row",parent=root_day)
            return
        age = txtAge_day.get(1.0,"end-1c").strip()
        if not is_num(age):
            messagebox.showerror("Error","NUM must be a number",parent=root_day)
            return
        def Update2(id,age):
            cur.execute("update employees"+ dayStr +" set age=? where id=?",
                        (age, id))
            con.commit()
        Update2(row_day[0],age)
        displayAll_day()
        clear_day()

    def sum1_day():
        global sumAll_day
        sumAll_day = 0
        sumAll1_day = 0
        sumAll2_day = 0
        data_day = cur.execute("SELECT * FROM employees"+ dayStr +" where id < 9871").fetchall()

        for sum2_day in data_day:
            sumAll_day += to_int(sum2_day[2])
            sumAll1_day += to_int(sum2_day[3])*to_int(sum2_day[2])
            sumAll2_day += to_int(sum2_day[4])*to_int(sum2_day[2])
        for w in tree_frame_day.winfo_children():
            if w.winfo_class() == "Treeview" and w is not tv_day:
                w.destroy()
        bv_day = make_sum(tree_frame_day,["","",str(sumAll_day),str(sumAll1_day),str(sumAll2_day),"",""],574)
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
                    activebackground='#1abc9c',
                    activeforeground='white',
                    bd=0,
                    cursor='hand2',
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
                    activebackground='#3498db',
                    activeforeground='white',
                    bd=0,
                    cursor='hand2'
                    ).place(x=4,y=50)

    btnDelete_day = Button(btn_frame_day,
                    text='Delete Details',
                    width=14,
                    height=1,
                    command=delete_day,
                    font=('calibri',16),
                    fg='white',
                    bg='#c0392b',
                    activebackground='#e74c3c',
                    activeforeground='white',
                    bd=0,
                    cursor='hand2'
                    ).place(x=170,y=5)

    btnClear_day = Button(btn_frame_day,
                    text='Clear Details',
                    width=14,
                    height=1,
                    command= clear_day,
                    font=('calibri',16),
                    fg='white',
                    bg='#f39c12',
                    activebackground='#f1c40f',
                    activeforeground='white',
                    bd=0,
                    cursor='hand2'
                    ).place(x=170,y=50)
    btnSumv_day = Button(btn_frame_day,
                    text='SUM',
                    width=14,
                    height=1,
                    command=sum1_day,
                    font=('calibri',16),
                    fg='white',
                    bg='green',
                    activebackground='#2ecc71',
                    activeforeground='white',
                    bd=0,
                    cursor='hand2'
                    ).place(x=170,y=100)
    btncounting = Button(btn_frame_day,
                text='Counting',
                width=14,
                height=1,
                command=lambda: counting(dayStr),
                font=('calibri',16),
                fg='white',
                bg='green',
                activebackground='#2ecc71',
                activeforeground='white',
                bd=0,
                cursor='hand2'
                ).place(x=4,y=100)
    #============ [Table Frame] =========

    tree_frame_day = Frame(root_day, bg='white')
    tree_frame_day.place(x=365, y=1, width=875, height=610)

    tv_day = make_tree(tree_frame_day,570)
    tv_day.bind("<ButtonRelease-1>", getData_day)

    for w in (txtName_day,txtjob_day,compGender_day,txtEamil_day,txtAddress_day):
        w["state"] = "disabled"
    start()
    displayAll_day()

def counting(dayStr):
    countingStr = dayStr
    time_day = time.strftime("%d/%m/%Y")
    if not table_exists("counting"+countingStr):
        sql_counting = "create table counting"+countingStr+"(id Integer Primary Key,name text,age text,job text,email text,gender text,address text)"
        cur.execute(sql_counting)
        con.commit()
        counting_start(countingStr,time_day)
    root_counting = Toplevel(root)
    root_counting.title('COLABA  -  Counting '+countingStr)
    root_counting.geometry('1240x615+0+0')
    root_counting.resizable(False,False)
    root_counting.configure(bg='#2c3e50')

    #======== Entries Frame =========
    entries_frame_counting = Frame(root_counting, bg='#2c3e50')
    entries_frame_counting.place(x=1,y=1,width=400,height=50)
    title_counting = Label(entries_frame_counting,text='COLABA  -  Counting '+countingStr, font=('calibri',18,'bold'), bg='#2c3e50', fg='#1abc9c')
    title_counting.place(x=10, y=1)

    #======== [Define] ==========

    def hide_day():
        root_counting.geometry("365x515+0+0")
    def show_day ():
        root_counting.geometry('1240x615+0+0')
    def refresh_day():
        displayAll_counting()
    btnRefresh_counting = Button(root_counting,text='REFRESH',bg='white',bd=1,relief=SOLID,cursor='hand2', command=refresh_day)
    btnRefresh_counting.place(x=210, y=10)
    btnhide_counting= Button(root_counting,text='HIDE',bg='white',bd=1,relief=SOLID,cursor='hand2', command=hide_day)
    btnhide_counting.place(x=270, y=10)
    btnshow_counting = Button(root_counting,text='SHOW',bg='white',bd=1,relief=SOLID,cursor='hand2', command=show_day)
    btnshow_counting.place(x=310, y=10)

    def displayAll_counting():
        def fetch_counting():
            cur.execute("SELECT * FROM counting"+ countingStr +" order by id")
            rows_counting = cur.fetchall()
            return rows_counting
        fill_tree(tv_counting,fetch_counting())
    def matplotlib ():
        buy_Employee_counting = []
        num_Employee_counting = []
        y = []
        labels = []
        cur.execute("select name from sqlite_master where type='table' and name like 'counting%'")
        nums = []
        for t in cur.fetchall():
            n = t[0][len("counting"):]
            if n.isdigit():
                nums.append(int(n))
        nums.sort()
        for x in nums:
            n = 0
            m = 0
            o = 0
            for Row in cur.execute("SELECT * FROM counting"+str(x)+" where id < 9871").fetchall():
                m += to_int(Row[3]) * to_int(Row[2])
                o += to_int(Row[4]) * to_int(Row[2])
            n = o - m
            buy_Employee_counting.append(m)
            num_Employee_counting.append(n)
            y.append(len(y)+1)
            d = cur.execute("SELECT name FROM counting"+str(x)+" where id = 9871").fetchone()
            if d is None:
                labels.append(str(x))
            else:
                labels.append(d[0])
        if len(y) == 0:
            messagebox.showinfo("Chart","there is no data yet",parent=root_counting)
            return
        plt.figure(figsize=(9,5))
        plt.plot(y,num_Employee_counting,'g-',markersize=12,label='AV',marker='o',markerfacecolor='yellow')
        plt.plot(y,buy_Employee_counting,'b-',markersize=12,label='buy',marker='o',markerfacecolor='yellow')
        plt.xticks(y,labels,rotation=30)
        plt.xlabel("Day")
        plt.ylabel("Mony")
        plt.grid(alpha=.4,linestyle='--')
        plt.legend()
        plt.tight_layout()
        plt.show()
    def sum1_counting():
        global sumAll_counting
        sumAll_counting = 0
        sumAll1_counting = 0
        sumAll2_counting = 0
        data_counting = cur.execute("SELECT * FROM counting"+ countingStr +" where id < 9871").fetchall()

        for sum2_counting in data_counting:
            sumAll_counting += to_int(sum2_counting[2])
            sumAll1_counting += to_int(sum2_counting[3])*to_int(sum2_counting[2])
            sumAll2_counting += to_int(sum2_counting[4])*to_int(sum2_counting[2])
        for w in tree_frame_counting.winfo_children():
            if w.winfo_class() == "Treeview" and w is not tv_counting:
                w.destroy()
        bv_counting = make_sum(tree_frame_counting,["","","قطعة: "+str(sumAll_counting),"شراء: "+str(sumAll1_counting),"مبيع: "+str(sumAll2_counting),"المربح: "+str(sumAll2_counting - sumAll1_counting),""],374)
    #======== Buttons Frame =========
    btn_frame_counting = Frame(root_counting,bg= '#2c3e50',bd= 1,relief=SOLID)
    btn_frame_counting.place(x=900,y=450, width=335,height=100)

    #============ [Table Frame] =========

    tree_frame_counting = Frame(root_counting, bg='white')
    tree_frame_counting.place(x=335, y=60, width=875, height=410)

    tv_counting = make_tree(tree_frame_counting,370)

    btnSum = Button(btn_frame_counting,
                text='SUM',
                width=14,
                height=1,
                command=sum1_counting,
                font=('calibri',16),
                fg='white',
                bg='green',
                activebackground='#2ecc71',
                activeforeground='white',
                bd=0,
                cursor='hand2'
                ).place(x=170,y=30)
    btnmatplotlib = Button(btn_frame_counting,
                text='Chart',
                width=14,
                height=1,
                font=('calibri',16),
                fg='white',
                bg='#16a085',
                activebackground='#1abc9c',
                activeforeground='white',
                bd=0,
                cursor='hand2',
                command= matplotlib
                ).place(x=4,y=30)
    displayAll_counting()

def counting_start(countingStr,time_day):
    num_Employee = {}
    for Row in cur.execute("SELECT * FROM employees"+countingStr+" where id < 9871").fetchall():
        num_Employee[Row[0]] = to_int(Row[2])

    for ROW in cur.execute("SELECT * FROM employees where id < 9871 order by id").fetchall():
        t = 0
        if ROW[0] in num_Employee:
            t = to_int(ROW[2]) - num_Employee[ROW[0]]
        cur.execute("insert into counting"+countingStr+"(id,name , age , job , email , gender , address) values (?,?,?,?,?,?,?)",(ROW[0],ROW[1],str(t),ROW[3],ROW[4],ROW[5],ROW[6]))
    cur.execute("insert or replace into counting"+ countingStr +"(id,name , age , job , email , gender , address) values (9871,?,'0','0','0','0','0')",(time_day,))
    con.commit()

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
    global row
    selected_row = tv.focus()
    data = tv.item(selected_row)
    if not data["values"]:
        return
    row = cur.execute("select * from employees where id=?",(data["values"][0],)).fetchone()
    if row is None:
        return
    name.set(row[1])
    age.set(row[2])
    job.set(row[3])
    email.set(row[4])
    gender.set(row[5])
    txtAddress.delete(1.0,END)
    txtAddress.insert(END,row[6])

def displayAll():
    def fetch():
        cur.execute("SELECT * FROM employees order by id")
        rows = cur.fetchall()
        return rows
    fill_tree(tv,fetch())
def clear():
    global row
    row = None
    name.set("")
    age.set("")
    job.set("")
    email.set("")
    gender.set("")
    txtAddress.delete(1.0,END)

def delete():
    if row is None:
        messagebox.showerror("Error","please choose a row")
        return
    if not messagebox.askyesno("Delete","Delete this row ?"):
        return
    def remove(id):
        cur.execute("delete from employees where id=?",(id,))
        con.commit()
    remove(row[0])
    clear()
    displayAll()

def check(name,age,job,email,gender):
    if name == "" or age == "" or job == "" or email == "" or gender == "":
        messagebox.showerror("Error","please Fill all the Entry")
        return False
    if not (is_num(age) and is_num(job) and is_num(email)):
        messagebox.showerror("Error","NUM , BUY and SALE must be numbers")
        return False
    return True

def add_employee():
    name = txtName.get().strip()
    age=txtAge.get().strip()
    job= txtjob.get().strip()
    email=txtEamil.get().strip()
    gender= compGender.get()
    address = txtAddress.get(1.0,"end-1c").strip()
    if not check(name,age,job,email,gender):
        return
    cur.execute("insert into employees(name, age,job ,email ,gender , address ) values (?,?,?,?,?,?)",(name,age,job,email,gender,address))
    con.commit()
    messagebox.showinfo("success","Added new item")
    clear()
    displayAll()
def update():
    if row is None:
        messagebox.showerror("Error","please choose a row")
        return
    name = txtName.get().strip()
    age=txtAge.get().strip()
    job= txtjob.get().strip()
    email=txtEamil.get().strip()
    gender= compGender.get()
    address = txtAddress.get(1.0,"end-1c").strip()
    if not check(name,age,job,email,gender):
        return

    def Update2(id,name,age,job,email,gender,address):
        cur.execute("update employees set name=?,age=?,job=?,email=?,gender=?,address=? where id=?",
                    (name,age,job,email,gender,address, id))
        con.commit()
    Update2(row[0],name,age,job,email,gender,address)
    messagebox.showinfo('success','The item data is updated')
    clear()
    displayAll()
def sum1():
    global sumAll
    sumAll = 0
    sumAll1 = 0
    sumAll2 = 0
    data = cur.execute("SELECT * FROM employees").fetchall()

    for sum2 in data:
        sumAll += to_int(sum2[2])
        sumAll1 += to_int(sum2[3])*to_int(sum2[2])
        sumAll2 += to_int(sum2[4])*to_int(sum2[2])
    for w in tree_frame.winfo_children():
        if w.winfo_class() == "Treeview" and w is not tv:
            w.destroy()
    bv = make_sum(tree_frame,["","",str(sumAll),str(sumAll1),str(sumAll2),"",""],574)

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
                activebackground='#1abc9c',
                activeforeground='white',
                bd=0,
                cursor='hand2',
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
                activebackground='#3498db',
                activeforeground='white',
                bd=0,
                cursor='hand2'
                ).place(x=4,y=50)

btnDelete = Button(btn_frame,
                text='Delete Details',
                width=14,
                height=1,
                command=delete,
                font=('calibri',16),
                fg='white',
                bg='#c0392b',
                activebackground='#e74c3c',
                activeforeground='white',
                bd=0,
                cursor='hand2'
                ).place(x=170,y=5)

btnClear = Button(btn_frame,
                text='Clear Details',
                width=14,
                height=1,
                command= clear,
                font=('calibri',16),
                fg='white',
                bg='#f39c12',
                activebackground='#f1c40f',
                activeforeground='white',
                bd=0,
                cursor='hand2'
                ).place(x=170,y=50)
btnSum = Button(btn_frame,
                text='SUM',
                width=14,
                height=1,
                command=sum1,
                font=('calibri',16),
                fg='white',
                bg='green',
                activebackground='#2ecc71',
                activeforeground='white',
                bd=0,
                cursor='hand2'
                ).place(x=170,y=100)
btnday = Button(btn_frame,
                text='DAY',
                width=14,
                height=1,
                command=day_data,
                font=('calibri',16),
                fg='white',
                bg='#2980b9',
                activebackground='#3498db',
                activeforeground='white',
                bd=0,
                cursor='hand2'
                ).place(x=4,y=100)
#============ [Table Frame] =========

tree_frame = Frame(root, bg='white')
tree_frame.place(x=365, y=1, width=875, height=610)

tv = make_tree(tree_frame,570)
tv.bind("<ButtonRelease-1>", getData)

displayAll()

root.mainloop()

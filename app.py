from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import psycopg2

app = Flask(__name__)

# Database connection
DBConnector = psycopg2.connect(user='GlovesStock_owner', password='9Z5esOASaQRU', host='ep-fancy-river-a2a7k2u7.eu-central-1.aws.neon.tech', database='GlovesStock', port=5432)
DBCursor = DBConnector.cursor()
def SaveInfoToDB(Sort, GloveCount):
    global CountInfo
    if '1' in Sort:
        CountInfo['FirstSortGloveCount']+=int(GloveCount)
        if CountInfo['FirstSortGloveCount']-int(GloveCount)==0:
            DBCursor.execute(f"SELECT MAX(Id) FROM workers_gloves_quantity")
            Id=DBCursor.fetchone()[0]
            Id=Id+1 if Id != None else 0

            DBCursor.execute(f"""SELECT Id FROM workers WHERE Name='{CountInfo['Worker']}' AND STAGE='{CountInfo['Stage'].replace("'", "''")}'""")
            WorkerId=DBCursor.fetchone()[0]

            DBCursor.execute(f"""INSERT INTO workers_gloves_quantity VALUES ({Id}, {WorkerId}, '{CountInfo['Product']}', 1, {CountInfo['FirstSortGloveCount']}, '{CountInfo['ShiftStart']}', '{str(datetime.now().strftime("%d.%m.%Y %H:%M"))}')""")
        else:
            DBCursor.execute(f"""SELECT Id FROM workers WHERE Name='{CountInfo['Worker']}' AND STAGE='{CountInfo['Stage'].replace("'", "''")}'""")
            WorkerId=DBCursor.fetchone()[0]

            DBCursor.execute(f"""UPDATE workers_gloves_quantity SET Quantity={CountInfo['FirstSortGloveCount']}, ShiftEnd='{datetime.now().strftime("%d.%m.%Y %H:%M")}' WHERE WorkerId={WorkerId} AND Product='{CountInfo['Product']}' AND Sort=1 AND ShiftStart='{CountInfo['ShiftStart']}'""")


        DBCursor.execute(f"""SELECT Id FROM products WHERE FullName='{CountInfo['Product']}' AND Exist=True""")
        ProductId=DBCursor.fetchone()[0]
        DBCursor.execute(f"""SELECT Id FROM products_gloves_quantity WHERE Stage='{CountInfo['Stage'].replace("'", "''")}' AND ProductId={ProductId} AND Sort=1""")
        Id=DBCursor.fetchone()

        if Id != None:
            if 'Machine' in CountInfo: DBCursor.execute(f"""SELECT Id FROM plans WHERE Machine='{CountInfo['Machine']}' AND Product='{CountInfo['Product']}' AND STAGE='{CountInfo['Stage'].replace("'", "''")}' AND Exist=True""")
            else: DBCursor.execute(f"""SELECT Id FROM plans WHERE Product='{CountInfo['Product']}' AND STAGE='{CountInfo['Stage'].replace("'", "''")}' AND Exist=True""")
            PlanId=DBCursor.fetchone()[0]

            DBCursor.execute(f"""SELECT Quantity FROM plans_gloves_quantity WHERE PlanId={PlanId} AND Sort=1""")
            PlanCount=DBCursor.fetchone()[0]+int(GloveCount)

            DBCursor.execute(f"""UPDATE plans_gloves_quantity SET Quantity={PlanCount} WHERE PlanId={PlanId} AND Sort=1""")


            DBCursor.execute(f"""SELECT Quantity FROM products_gloves_quantity WHERE ProductId={ProductId} AND STAGE='{CountInfo['Stage'].replace("'", "''")}' AND Sort=1""")
            ProductCount=DBCursor.fetchone()[0]+int(GloveCount)

            DBCursor.execute(f"""UPDATE products_gloves_quantity SET Quantity={ProductCount} WHERE ProductId={ProductId} AND STAGE='{CountInfo['Stage'].replace("'", "''")}' AND Sort=1""")
        else:
            DBCursor.execute(f"SELECT MAX(Id) FROM plans_gloves_quantity")
            Id=DBCursor.fetchone()[0]
            Id=Id+1 if Id != None else 0

            if 'Machine' in CountInfo: DBCursor.execute(f"""SELECT Id FROM plans WHERE Machine='{CountInfo['Machine']}' AND Product='{CountInfo['Product']}' AND STAGE='{CountInfo['Stage'].replace("'", "''")}' AND Exist=True""")
            else: DBCursor.execute(f"""SELECT Id FROM plans WHERE Product='{CountInfo['Product']}' AND STAGE='{CountInfo['Stage'].replace("'", "''")}' AND Exist=True""")
            PlanId=DBCursor.fetchone()[0]

            DBCursor.execute(f"""INSERT INTO plans_gloves_quantity VALUES ({Id}, {PlanId}, 1, {CountInfo['FirstSortGloveCount']})""")


            DBCursor.execute(f"SELECT MAX(Id) FROM products_gloves_quantity")
            Id=DBCursor.fetchone()[0]
            Id=Id+1 if Id != None else 0

            DBCursor.execute(f"""INSERT INTO products_gloves_quantity VALUES ({Id}, {ProductId}, '{CountInfo['Stage'].replace("'", "''")}', 1, {CountInfo['FirstSortGloveCount']})""")


    if '2' in Sort:
        CountInfo['SecondSortGloveCount']+=int(GloveCount)
        if CountInfo['SecondSortGloveCount']-int(GloveCount)==0:
            DBCursor.execute(f"SELECT MAX(Id) FROM workers_gloves_quantity")
            Id=DBCursor.fetchone()[0]
            Id=Id+1 if Id != None else 0

            DBCursor.execute(f"""SELECT Id FROM workers WHERE Name='{CountInfo['Worker']}' AND STAGE='{CountInfo['Stage'].replace("'", "''")}'""")
            WorkerId=DBCursor.fetchone()[0]

            DBCursor.execute(f"""INSERT INTO workers_gloves_quantity VALUES ({Id}, {WorkerId}, '{CountInfo['Product']}', 2, {CountInfo['SecondSortGloveCount']}, '{CountInfo['ShiftStart']}', '{str(datetime.now().strftime("%d.%m.%Y %H:%M"))}')""")
        else:
            DBCursor.execute(f"""SELECT Id FROM workers WHERE Name='{CountInfo['Worker']}' AND STAGE='{CountInfo['Stage'].replace("'", "''")}'""")
            WorkerId=DBCursor.fetchone()[0]

            DBCursor.execute(f"""UPDATE workers_gloves_quantity SET Quantity={CountInfo['SecondSortGloveCount']}, ShiftEnd='{datetime.now().strftime("%d.%m.%Y %H:%M")}' WHERE WorkerId={WorkerId} AND Product='{CountInfo['Product']}' AND Sort=2 AND ShiftStart='{CountInfo['ShiftStart']}'""")


        DBCursor.execute(f"""SELECT Id FROM products WHERE FullName='{CountInfo['Product']}' AND Exist=True""")
        ProductId=DBCursor.fetchone()[0]
        DBCursor.execute(f"""SELECT Id FROM products_gloves_quantity WHERE ProductId={ProductId} AND STAGE='{CountInfo['Stage'].replace("'", "''")}' AND Sort=2""")
        Id=DBCursor.fetchone()

        if Id != None:
            if 'Machine' in CountInfo: DBCursor.execute(f"""SELECT Id FROM plans WHERE Machine='{CountInfo['Machine']}' AND Product='{CountInfo['Product']}' AND STAGE='{CountInfo['Stage'].replace("'", "''")}' AND Exist=True""")
            else: DBCursor.execute(f"""SELECT Id FROM plans WHERE Product='{CountInfo['Product']}' AND STAGE='{CountInfo['Stage'].replace("'", "''")}' AND Exist=True""")
            PlanId=DBCursor.fetchone()[0]

            DBCursor.execute(f"""SELECT Quantity FROM plans_gloves_quantity WHERE PlanId={PlanId} AND Sort=2""")
            PlanCount=DBCursor.fetchone()[0]+int(GloveCount)

            DBCursor.execute(f"""UPDATE plans_gloves_quantity SET Quantity={PlanCount} WHERE PlanId={PlanId} AND Sort=2""")


            DBCursor.execute(f"""SELECT Quantity FROM products_gloves_quantity WHERE ProductId={ProductId} AND STAGE='{CountInfo['Stage'].replace("'", "''")}' AND Sort=2""")
            ProductCount=DBCursor.fetchone()[0]+int(GloveCount)

            DBCursor.execute(f"""UPDATE products_gloves_quantity SET Quantity={ProductCount} WHERE ProductId={ProductId} AND STAGE='{CountInfo['Stage'].replace("'", "''")}' AND Sort=2""")
        else:
            DBCursor.execute(f"SELECT MAX(Id) FROM plans_gloves_quantity")
            Id=DBCursor.fetchone()[0]
            Id=Id+1 if Id != None else 0

            if 'Machine' in CountInfo: DBCursor.execute(f"""SELECT Id FROM plans WHERE Machine='{CountInfo['Machine']}' AND Product='{CountInfo['Product']}' AND STAGE='{CountInfo['Stage'].replace("'", "''")}' AND Exist=True""")
            else: DBCursor.execute(f"""SELECT Id FROM plans WHERE Product='{CountInfo['Product']}' AND STAGE='{CountInfo['Stage'].replace("'", "''")}' AND Exist=True""")
            PlanId=DBCursor.fetchone()[0]

            DBCursor.execute(f"""INSERT INTO plans_gloves_quantity VALUES ({Id}, {PlanId}, 2, {CountInfo['SecondSortGloveCount']})""")


            DBCursor.execute(f"SELECT MAX(Id) FROM products_gloves_quantity")
            Id=DBCursor.fetchone()[0]
            Id=Id+1 if Id != None else 0

            DBCursor.execute(f"""INSERT INTO products_gloves_quantity VALUES ({Id}, {ProductId}, '{CountInfo['Stage'].replace("'", "''")}', 2, {CountInfo['SecondSortGloveCount']})""")


    if '3' in Sort:
        CountInfo['DefectSortGloveCount']+=int(GloveCount)
        if CountInfo['DefectSortGloveCount']-int(GloveCount)==0:
            DBCursor.execute(f"SELECT MAX(Id) FROM workers_gloves_quantity")
            Id=DBCursor.fetchone()[0]
            Id=Id+1 if Id != None else 0

            DBCursor.execute(f"""SELECT Id FROM workers WHERE Name='{CountInfo['Worker']}' AND STAGE='{CountInfo['Stage'].replace("'", "''")}'""")
            WorkerId=DBCursor.fetchone()[0]

            DBCursor.execute(f"""INSERT INTO workers_gloves_quantity VALUES ({Id}, {WorkerId}, '{CountInfo['Product']}', 3, {CountInfo['DefectSortGloveCount']}, '{CountInfo['ShiftStart']}', '{str(datetime.now().strftime("%d.%m.%Y %H:%M"))}')""")
        else:
            DBCursor.execute(f"""SELECT Id FROM workers WHERE Name='{CountInfo['Worker']}' AND STAGE='{CountInfo['Stage'].replace("'", "''")}'""")
            WorkerId=DBCursor.fetchone()[0]

            DBCursor.execute(f"""UPDATE workers_gloves_quantity SET Quantity={CountInfo['DefectSortGloveCount']}, ShiftEnd='{datetime.now().strftime("%d.%m.%Y %H:%M")}' WHERE WorkerId={WorkerId} AND Product='{CountInfo['Product']}' AND Sort=3 AND ShiftStart='{CountInfo['ShiftStart']}'""")


        DBCursor.execute(f"""SELECT Id FROM products WHERE FullName='{CountInfo['Product']}' AND Exist=True""")
        ProductId=DBCursor.fetchone()[0]
        DBCursor.execute(f"""SELECT Id FROM products_gloves_quantity WHERE ProductId={ProductId} AND STAGE='{CountInfo['Stage'].replace("'", "''")}' AND Sort=3""")
        Id=DBCursor.fetchone()

        if Id != None:
            if 'Machine' in CountInfo: DBCursor.execute(f"""SELECT Id FROM plans WHERE Machine='{CountInfo['Machine']}' AND Product='{CountInfo['Product']}' AND STAGE='{CountInfo['Stage'].replace("'", "''")}' AND Exist=True""")
            else: DBCursor.execute(f"""SELECT Id FROM plans WHERE Product='{CountInfo['Product']}' AND STAGE='{CountInfo['Stage'].replace("'", "''")}' AND Exist=True""")
            PlanId=DBCursor.fetchone()[0]

            DBCursor.execute(f"""SELECT Quantity FROM plans_gloves_quantity WHERE PlanId={PlanId} AND Sort=3""")
            PlanCount=DBCursor.fetchone()[0]+int(GloveCount)

            DBCursor.execute(f"""UPDATE plans_gloves_quantity SET Quantity={PlanCount} WHERE PlanId={PlanId} AND Sort=3""")


            DBCursor.execute(f"""SELECT Quantity FROM products_gloves_quantity WHERE ProductId={ProductId} AND STAGE='{CountInfo['Stage'].replace("'", "''")}' AND Sort=3""")
            ProductCount=DBCursor.fetchone()[0]+int(GloveCount)

            DBCursor.execute(f"""UPDATE products_gloves_quantity SET Quantity={ProductCount} WHERE ProductId={ProductId} AND STAGE='{CountInfo['Stage'].replace("'", "''")}' AND Sort=3""")
        else:
            DBCursor.execute(f"SELECT MAX(Id) FROM plans_gloves_quantity")
            Id=DBCursor.fetchone()[0]
            Id=Id+1 if Id != None else 0

            if 'Machine' in CountInfo: DBCursor.execute(f"""SELECT Id FROM plans WHERE Machine='{CountInfo['Machine']}' AND Product='{CountInfo['Product']}' AND STAGE='{CountInfo['Stage'].replace("'", "''")}' AND Exist=True""")
            else: DBCursor.execute(f"""SELECT Id FROM plans WHERE Product='{CountInfo['Product']}' AND STAGE='{CountInfo['Stage'].replace("'", "''")}' AND Exist=True""")
            PlanId=DBCursor.fetchone()[0]

            DBCursor.execute(f"""INSERT INTO plans_gloves_quantity VALUES ({Id}, {PlanId}, 3, {CountInfo['DefectSortGloveCount']})""")


            DBCursor.execute(f"SELECT MAX(Id) FROM products_gloves_quantity")
            Id=DBCursor.fetchone()[0]
            Id=Id+1 if Id != None else 0


            DBCursor.execute(f"""INSERT INTO products_gloves_quantity VALUES ({Id}, {ProductId}, '{CountInfo['Stage'].replace("'", "''")}', 3, {CountInfo['DefectSortGloveCount']})""")



    DBConnector.commit()



@app.route('/', methods=['GET', 'POST'])
def WorkerSelect():
    global CountInfo, AvailableStages
    if request.method == "POST":
        Worker=request.form['Worker']
        CountInfo['Worker'] = Worker
        DBCursor.execute(f"SELECT Stage FROM workers WHERE Name='{CountInfo['Worker']}'")
        AvailableStages=[Stage[0] for Stage in DBCursor.fetchall()]
        if len(AvailableStages)>1:
            return redirect(f'/stage_select')
        elif AvailableStages[0] in ["В'язання", "Оверлок"]:
            CountInfo['Stage'] = AvailableStages[0]
            return redirect(f'/machine_select')
        else:
            CountInfo['Stage'] = AvailableStages[0]
            DBCursor.execute(f"""SELECT Product FROM plans WHERE STAGE='{CountInfo['Stage'].replace("'", "''")}' AND Exist=True""")
            CountInfo['Product'] = DBCursor.fetchone()
            CountInfo['FirstSortGloveCount']=0
            CountInfo['SecondSortGloveCount']=0
            CountInfo['DefectSortGloveCount']=0
            CountInfo['ShiftStart']=datetime.now().strftime("%d.%m.%Y %H:%M")
            if CountInfo['Product'] != None:
                CountInfo['Product'] = CountInfo['Product'][0]
                return redirect(f'/shift')
    else:
        CountInfo={}
        DBCursor.execute("SELECT Name FROM workers WHERE Exist=True")
        Workers = list(set([row[0] for row in DBCursor.fetchall()]))
        return render_template('WorkerSelect.html', Workers=Workers)

@app.route('/stage_select', methods=['GET', 'POST'])
def StageSelect():
    global CountInfo
    if request.method == 'POST':
        Stage=request.form['Stage']
        CountInfo['Stage'] = Stage
        if Stage in ["В'язання", "Оверлок"]:
            return redirect(f'/machine_select')
        else:
            DBCursor.execute(f"""SELECT Product FROM plans WHERE STAGE='{CountInfo['Stage'].replace("'", "''")}' AND Exist=True""")
            CountInfo['Product'] = DBCursor.fetchone()
            CountInfo['FirstSortGloveCount']=0
            CountInfo['SecondSortGloveCount']=0
            CountInfo['DefectSortGloveCount']=0
            CountInfo['ShiftStart']=datetime.now().strftime("%d.%m.%Y %H:%M")
            if CountInfo['Product'] != None:
                CountInfo['Product'] = CountInfo['Product'][0]
                return redirect('/shift')
            else:
                return redirect('/')
    else:
        return render_template('StageSelect.html', AvailableStages=AvailableStages)

@app.route('/machine_select', methods=['GET', 'POST'])
def MachineSelect():
    global CountInfo
    if request.method == 'POST':
        Machine=request.form['Machine']
        print(Machine)
        CountInfo['Machine'] = Machine
        CountInfo['FirstSortGloveCount']=0
        CountInfo['SecondSortGloveCount']=0
        CountInfo['DefectSortGloveCount']=0
        CountInfo['ShiftStart']=datetime.now().strftime("%d.%m.%Y %H:%M")

        DBCursor.execute(f"""SELECT Product FROM plans WHERE Machine='{CountInfo['Machine']}' AND STAGE='{CountInfo['Stage'].replace("'", "''")}' AND Exist=True""")
        CountInfo['Product'] = DBCursor.fetchone()[0]

        return redirect('/shift')
    else:
        DBCursor.execute(f"""SELECT Machine FROM plans WHERE Stage='{CountInfo['Stage'].replace("'", "''")}'""")

        Machines=sorted(list(set([Machine[0] for Machine in DBCursor.fetchall()])))

        return render_template('MachineSelect.html', Machines=Machines, BackUrl='stage_select' if len(AvailableStages)>1 else '/')

@app.route('/shift', methods=['GET', 'POST'])
def Shift():
    if request.method == 'POST':
         Stop=request.form['Stop']
         if Stop=='0':
            Sort=request.form['Sort']
            GloveCount=request.form['CountInput']
            SaveInfoToDB(Sort, GloveCount)
            if len(AvailableStages)>1 and CountInfo['Stage'] in ["В'язання", "Оверлок"]:
                BackUrl='/machine_select'
            elif len(AvailableStages)>1 and CountInfo['Stage'] not in ["В'язання", "Оверлок"]:
                BackUrl='/stage_select'
            else:
                BackUrl='/'

            if CountInfo['Stage'] not in ["В'язання", "Оверлок"]:
                ShiftName=f"Зміна ({CountInfo['Worker']}, {CountInfo['Stage']}, {CountInfo['Product']})"
            else:
                ShiftName=f"Зміна ({CountInfo['Worker']}, {CountInfo['Stage']}, {CountInfo['Machine']} машина, {CountInfo['Product']})"

            return render_template('Shift.html', BackUrl=BackUrl, ShiftName=ShiftName, FirstSortGloveCount=CountInfo['FirstSortGloveCount'], SecondSortGloveCount=CountInfo['SecondSortGloveCount'], DefectSortGloveCount=CountInfo['DefectSortGloveCount'], ShiftStart=CountInfo['ShiftStart'])
         else:
             SaveInfoToDB('123', '0')
             return redirect('/')
    else:
        if len(AvailableStages)>1 and CountInfo['Stage'] in ["В'язання", "Оверлок"]:
            BackUrl='/machine_select'
        elif len(AvailableStages)>1 and CountInfo['Stage'] not in ["В'язання", "Оверлок"]:
            BackUrl='/stage_select'
        else:
            BackUrl='/'

        if CountInfo['Stage'] not in ["В'язання", "Оверлок"]:
            ShiftName=f"Зміна ({CountInfo['Worker']}, {CountInfo['Stage']}, {CountInfo['Product']})"
        else:
            ShiftName=f"Зміна ({CountInfo['Worker']}, {CountInfo['Stage']}, {CountInfo['Machine']} машина, {CountInfo['Product']})"

        return render_template('Shift.html', BackUrl=BackUrl, ShiftName=ShiftName, FirstSortGloveCount=CountInfo['FirstSortGloveCount'], SecondSortGloveCount=CountInfo['SecondSortGloveCount'], DefectSortGloveCount=CountInfo['DefectSortGloveCount'], ShiftStart=CountInfo['ShiftStart'])

if __name__ == '__main__':
    app.run(debug=True)

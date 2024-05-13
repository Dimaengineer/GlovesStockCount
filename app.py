from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import psycopg2

app = Flask(__name__)

# Database connection
DBConnector = psycopg2.connect(user='GlovesStock_owner', password='9Z5esOASaQRU', host='ep-fancy-river-a2a7k2u7.eu-central-1.aws.neon.tech', database='GlovesStock', port=5432)
DBCursor = DBConnector.cursor()
UsersInfo = {}
def SaveInfoToDB(UserId, Sort, GloveCount):
    global UsersInfo
    if '1' in Sort:
        UsersInfo[UserId]['FirstSortGloveCount']+=int(GloveCount)
        if UsersInfo[UserId]['FirstSortGloveCount']-int(GloveCount)==0:
            DBCursor.execute(f"SELECT MAX(Id) FROM workers_gloves_quantity")
            Id=DBCursor.fetchone()[0]
            Id=Id+1 if Id != None else 0

            DBCursor.execute(f"""SELECT Id FROM workers WHERE Name='{UsersInfo[UserId]['Worker']}' AND STAGE='{UsersInfo[UserId]['Stage'].replace("'", "''")}'""")
            WorkerId=DBCursor.fetchone()[0]

            DBCursor.execute(f"""INSERT INTO workers_gloves_quantity VALUES ({Id}, {WorkerId}, '{UsersInfo[UserId]['Product']}', 1, {UsersInfo[UserId]['FirstSortGloveCount']}, '{UsersInfo[UserId]['ShiftStart']}', '{str(datetime.now().strftime("%d.%m.%Y %H:%M"))}')""")
        else:
            DBCursor.execute(f"""SELECT Id FROM workers WHERE Name='{UsersInfo[UserId]['Worker']}' AND STAGE='{UsersInfo[UserId]['Stage'].replace("'", "''")}'""")
            WorkerId=DBCursor.fetchone()[0]

            DBCursor.execute(f"""UPDATE workers_gloves_quantity SET Quantity={UsersInfo[UserId]['FirstSortGloveCount']}, ShiftEnd='{datetime.now().strftime("%d.%m.%Y %H:%M")}' WHERE WorkerId={WorkerId} AND Product='{UsersInfo[UserId]['Product']}' AND Sort=1 AND ShiftStart='{UsersInfo[UserId]['ShiftStart']}'""")


        DBCursor.execute(f"""SELECT Id FROM products WHERE FullName='{UsersInfo[UserId]['Product']}' AND Exist=True""")
        ProductId=DBCursor.fetchone()[0]
        DBCursor.execute(f"""SELECT Id FROM products_gloves_quantity WHERE Stage='{UsersInfo[UserId]['Stage'].replace("'", "''")}' AND ProductId={ProductId} AND Sort=1""")
        Id=DBCursor.fetchone()

        if Id != None:
            if 'Machine' in UsersInfo[UserId]: DBCursor.execute(f"""SELECT Id FROM plans WHERE Machine='{UsersInfo[UserId]['Machine']}' AND Product='{UsersInfo[UserId]['Product']}' AND STAGE='{UsersInfo[UserId]['Stage'].replace("'", "''")}' AND Exist=True""")
            else: DBCursor.execute(f"""SELECT Id FROM plans WHERE Product='{UsersInfo[UserId]['Product']}' AND STAGE='{UsersInfo[UserId]['Stage'].replace("'", "''")}' AND Exist=True""")
            PlanId=DBCursor.fetchone()[0]

            DBCursor.execute(f"""SELECT Quantity FROM plans_gloves_quantity WHERE PlanId={PlanId} AND Sort=1""")
            PlanCount=DBCursor.fetchone()[0]+int(GloveCount)

            DBCursor.execute(f"""UPDATE plans_gloves_quantity SET Quantity={PlanCount} WHERE PlanId={PlanId} AND Sort=1""")


            DBCursor.execute(f"""SELECT Quantity FROM products_gloves_quantity WHERE ProductId={ProductId} AND STAGE='{UsersInfo[UserId]['Stage'].replace("'", "''")}' AND Sort=1""")
            ProductCount=DBCursor.fetchone()[0]+int(GloveCount)

            DBCursor.execute(f"""UPDATE products_gloves_quantity SET Quantity={ProductCount} WHERE ProductId={ProductId} AND STAGE='{UsersInfo[UserId]['Stage'].replace("'", "''")}' AND Sort=1""")
        else:
            DBCursor.execute(f"SELECT MAX(Id) FROM plans_gloves_quantity")
            Id=DBCursor.fetchone()[0]
            Id=Id+1 if Id != None else 0

            if 'Machine' in UsersInfo[UserId]: DBCursor.execute(f"""SELECT Id FROM plans WHERE Machine='{UsersInfo[UserId]['Machine']}' AND Product='{UsersInfo[UserId]['Product']}' AND STAGE='{UsersInfo[UserId]['Stage'].replace("'", "''")}' AND Exist=True""")
            else: DBCursor.execute(f"""SELECT Id FROM plans WHERE Product='{UsersInfo[UserId]['Product']}' AND STAGE='{UsersInfo[UserId]['Stage'].replace("'", "''")}' AND Exist=True""")
            PlanId=DBCursor.fetchone()[0]

            DBCursor.execute(f"""INSERT INTO plans_gloves_quantity VALUES ({Id}, {PlanId}, 1, {UsersInfo[UserId]['FirstSortGloveCount']})""")


            DBCursor.execute(f"SELECT MAX(Id) FROM products_gloves_quantity")
            Id=DBCursor.fetchone()[0]
            Id=Id+1 if Id != None else 0

            DBCursor.execute(f"""INSERT INTO products_gloves_quantity VALUES ({Id}, {ProductId}, '{UsersInfo[UserId]['Stage'].replace("'", "''")}', 1, {UsersInfo[UserId]['FirstSortGloveCount']})""")


    if '2' in Sort:
        UsersInfo[UserId]['SecondSortGloveCount']+=int(GloveCount)
        if UsersInfo[UserId]['SecondSortGloveCount']-int(GloveCount)==0:
            DBCursor.execute(f"SELECT MAX(Id) FROM workers_gloves_quantity")
            Id=DBCursor.fetchone()[0]
            Id=Id+1 if Id != None else 0

            DBCursor.execute(f"""SELECT Id FROM workers WHERE Name='{UsersInfo[UserId]['Worker']}' AND STAGE='{UsersInfo[UserId]['Stage'].replace("'", "''")}'""")
            WorkerId=DBCursor.fetchone()[0]

            DBCursor.execute(f"""INSERT INTO workers_gloves_quantity VALUES ({Id}, {WorkerId}, '{UsersInfo[UserId]['Product']}', 2, {UsersInfo[UserId]['SecondSortGloveCount']}, '{UsersInfo[UserId]['ShiftStart']}', '{str(datetime.now().strftime("%d.%m.%Y %H:%M"))}')""")
        else:
            DBCursor.execute(f"""SELECT Id FROM workers WHERE Name='{UsersInfo[UserId]['Worker']}' AND STAGE='{UsersInfo[UserId]['Stage'].replace("'", "''")}'""")
            WorkerId=DBCursor.fetchone()[0]

            DBCursor.execute(f"""UPDATE workers_gloves_quantity SET Quantity={UsersInfo[UserId]['SecondSortGloveCount']}, ShiftEnd='{datetime.now().strftime("%d.%m.%Y %H:%M")}' WHERE WorkerId={WorkerId} AND Product='{UsersInfo[UserId]['Product']}' AND Sort=2 AND ShiftStart='{UsersInfo[UserId]['ShiftStart']}'""")


        DBCursor.execute(f"""SELECT Id FROM products WHERE FullName='{UsersInfo[UserId]['Product']}' AND Exist=True""")
        ProductId=DBCursor.fetchone()[0]
        DBCursor.execute(f"""SELECT Id FROM products_gloves_quantity WHERE ProductId={ProductId} AND STAGE='{UsersInfo[UserId]['Stage'].replace("'", "''")}' AND Sort=2""")
        Id=DBCursor.fetchone()

        if Id != None:
            if 'Machine' in UsersInfo[UserId]: DBCursor.execute(f"""SELECT Id FROM plans WHERE Machine='{UsersInfo[UserId]['Machine']}' AND Product='{UsersInfo[UserId]['Product']}' AND STAGE='{UsersInfo[UserId]['Stage'].replace("'", "''")}' AND Exist=True""")
            else: DBCursor.execute(f"""SELECT Id FROM plans WHERE Product='{UsersInfo[UserId]['Product']}' AND STAGE='{UsersInfo[UserId]['Stage'].replace("'", "''")}' AND Exist=True""")
            PlanId=DBCursor.fetchone()[0]

            DBCursor.execute(f"""SELECT Quantity FROM plans_gloves_quantity WHERE PlanId={PlanId} AND Sort=2""")
            PlanCount=DBCursor.fetchone()[0]+int(GloveCount)

            DBCursor.execute(f"""UPDATE plans_gloves_quantity SET Quantity={PlanCount} WHERE PlanId={PlanId} AND Sort=2""")


            DBCursor.execute(f"""SELECT Quantity FROM products_gloves_quantity WHERE ProductId={ProductId} AND STAGE='{UsersInfo[UserId]['Stage'].replace("'", "''")}' AND Sort=2""")
            ProductCount=DBCursor.fetchone()[0]+int(GloveCount)

            DBCursor.execute(f"""UPDATE products_gloves_quantity SET Quantity={ProductCount} WHERE ProductId={ProductId} AND STAGE='{UsersInfo[UserId]['Stage'].replace("'", "''")}' AND Sort=2""")
        else:
            DBCursor.execute(f"SELECT MAX(Id) FROM plans_gloves_quantity")
            Id=DBCursor.fetchone()[0]
            Id=Id+1 if Id != None else 0

            if 'Machine' in UsersInfo[UserId]: DBCursor.execute(f"""SELECT Id FROM plans WHERE Machine='{UsersInfo[UserId]['Machine']}' AND Product='{UsersInfo[UserId]['Product']}' AND STAGE='{UsersInfo[UserId]['Stage'].replace("'", "''")}' AND Exist=True""")
            else: DBCursor.execute(f"""SELECT Id FROM plans WHERE Product='{UsersInfo[UserId]['Product']}' AND STAGE='{UsersInfo[UserId]['Stage'].replace("'", "''")}' AND Exist=True""")
            PlanId=DBCursor.fetchone()[0]

            DBCursor.execute(f"""INSERT INTO plans_gloves_quantity VALUES ({Id}, {PlanId}, 2, {UsersInfo[UserId]['SecondSortGloveCount']})""")


            DBCursor.execute(f"SELECT MAX(Id) FROM products_gloves_quantity")
            Id=DBCursor.fetchone()[0]
            Id=Id+1 if Id != None else 0

            DBCursor.execute(f"""INSERT INTO products_gloves_quantity VALUES ({Id}, {ProductId}, '{UsersInfo[UserId]['Stage'].replace("'", "''")}', 2, {UsersInfo[UserId]['SecondSortGloveCount']})""")


    if '3' in Sort:
        UsersInfo[UserId]['DefectSortGloveCount']+=int(GloveCount)
        if UsersInfo[UserId]['DefectSortGloveCount']-int(GloveCount)==0:
            DBCursor.execute(f"SELECT MAX(Id) FROM workers_gloves_quantity")
            Id=DBCursor.fetchone()[0]
            Id=Id+1 if Id != None else 0

            DBCursor.execute(f"""SELECT Id FROM workers WHERE Name='{UsersInfo[UserId]['Worker']}' AND STAGE='{UsersInfo[UserId]['Stage'].replace("'", "''")}'""")
            WorkerId=DBCursor.fetchone()[0]

            DBCursor.execute(f"""INSERT INTO workers_gloves_quantity VALUES ({Id}, {WorkerId}, '{UsersInfo[UserId]['Product']}', 3, {UsersInfo[UserId]['DefectSortGloveCount']}, '{UsersInfo[UserId]['ShiftStart']}', '{str(datetime.now().strftime("%d.%m.%Y %H:%M"))}')""")
        else:
            DBCursor.execute(f"""SELECT Id FROM workers WHERE Name='{UsersInfo[UserId]['Worker']}' AND STAGE='{UsersInfo[UserId]['Stage'].replace("'", "''")}'""")
            WorkerId=DBCursor.fetchone()[0]

            DBCursor.execute(f"""UPDATE workers_gloves_quantity SET Quantity={UsersInfo[UserId]['DefectSortGloveCount']}, ShiftEnd='{datetime.now().strftime("%d.%m.%Y %H:%M")}' WHERE WorkerId={WorkerId} AND Product='{UsersInfo[UserId]['Product']}' AND Sort=3 AND ShiftStart='{UsersInfo[UserId]['ShiftStart']}'""")


        DBCursor.execute(f"""SELECT Id FROM products WHERE FullName='{UsersInfo[UserId]['Product']}' AND Exist=True""")
        ProductId=DBCursor.fetchone()[0]
        DBCursor.execute(f"""SELECT Id FROM products_gloves_quantity WHERE ProductId={ProductId} AND STAGE='{UsersInfo[UserId]['Stage'].replace("'", "''")}' AND Sort=3""")
        Id=DBCursor.fetchone()

        if Id != None:
            if 'Machine' in UsersInfo[UserId]: DBCursor.execute(f"""SELECT Id FROM plans WHERE Machine='{UsersInfo[UserId]['Machine']}' AND Product='{UsersInfo[UserId]['Product']}' AND STAGE='{UsersInfo[UserId]['Stage'].replace("'", "''")}' AND Exist=True""")
            else: DBCursor.execute(f"""SELECT Id FROM plans WHERE Product='{UsersInfo[UserId]['Product']}' AND STAGE='{UsersInfo[UserId]['Stage'].replace("'", "''")}' AND Exist=True""")
            PlanId=DBCursor.fetchone()[0]

            DBCursor.execute(f"""SELECT Quantity FROM plans_gloves_quantity WHERE PlanId={PlanId} AND Sort=3""")
            PlanCount=DBCursor.fetchone()[0]+int(GloveCount)

            DBCursor.execute(f"""UPDATE plans_gloves_quantity SET Quantity={PlanCount} WHERE PlanId={PlanId} AND Sort=3""")


            DBCursor.execute(f"""SELECT Quantity FROM products_gloves_quantity WHERE ProductId={ProductId} AND STAGE='{UsersInfo[UserId]['Stage'].replace("'", "''")}' AND Sort=3""")
            ProductCount=DBCursor.fetchone()[0]+int(GloveCount)

            DBCursor.execute(f"""UPDATE products_gloves_quantity SET Quantity={ProductCount} WHERE ProductId={ProductId} AND STAGE='{UsersInfo[UserId]['Stage'].replace("'", "''")}' AND Sort=3""")
        else:
            DBCursor.execute(f"SELECT MAX(Id) FROM plans_gloves_quantity")
            Id=DBCursor.fetchone()[0]
            Id=Id+1 if Id != None else 0

            if 'Machine' in UsersInfo[UserId]: DBCursor.execute(f"""SELECT Id FROM plans WHERE Machine='{UsersInfo[UserId]['Machine']}' AND Product='{UsersInfo[UserId]['Product']}' AND STAGE='{UsersInfo[UserId]['Stage'].replace("'", "''")}' AND Exist=True""")
            else: DBCursor.execute(f"""SELECT Id FROM plans WHERE Product='{UsersInfo[UserId]['Product']}' AND STAGE='{UsersInfo[UserId]['Stage'].replace("'", "''")}' AND Exist=True""")
            PlanId=DBCursor.fetchone()[0]

            DBCursor.execute(f"""INSERT INTO plans_gloves_quantity VALUES ({Id}, {PlanId}, 3, {UsersInfo[UserId]['DefectSortGloveCount']})""")


            DBCursor.execute(f"SELECT MAX(Id) FROM products_gloves_quantity")
            Id=DBCursor.fetchone()[0]
            Id=Id+1 if Id != None else 0


            DBCursor.execute(f"""INSERT INTO products_gloves_quantity VALUES ({Id}, {ProductId}, '{UsersInfo[UserId]['Stage'].replace("'", "''")}', 3, {UsersInfo[UserId]['DefectSortGloveCount']})""")



    DBConnector.commit()



@app.route('/', methods=['GET', 'POST'])
def StartApp():
    UserId=1 if UsersInfo == {} else max(UsersInfo.keys())+1
    return redirect(f'/{UserId}/')

@app.route('/<int:UserId>/', methods=['GET', 'POST'])
def WorkerSelect(UserId):
    global UsersInfo, AvailableStages
    if request.method == "POST":
        Worker=request.form['Worker']
        UsersInfo[UserId]['Worker'] = Worker
        DBCursor.execute(f"SELECT Stage FROM workers WHERE Name='{UsersInfo[UserId]['Worker']}'")
        AvailableStages=[Stage[0] for Stage in DBCursor.fetchall()]
        if len(AvailableStages)>1:
            return redirect(f'/{UserId}/stage_select')
        elif AvailableStages[0] in ["В'язання", "Оверлок"]:
            UsersInfo[UserId]['Stage'] = AvailableStages[0]
            return redirect(f'/{UserId}/machine_select')
        else:
            UsersInfo[UserId]['Stage'] = AvailableStages[0]
            DBCursor.execute(f"""SELECT Product FROM plans WHERE STAGE='{UsersInfo[UserId]['Stage'].replace("'", "''")}' AND Exist=True""")
            UsersInfo[UserId]['Product'] = DBCursor.fetchone()
            UsersInfo[UserId]['FirstSortGloveCount']=0
            UsersInfo[UserId]['SecondSortGloveCount']=0
            UsersInfo[UserId]['DefectSortGloveCount']=0
            UsersInfo[UserId]['ShiftStart']=datetime.now().strftime("%d.%m.%Y %H:%M")
            if UsersInfo[UserId]['Product'] != None:
                UsersInfo[UserId]['Product'] = UsersInfo[UserId]['Product'][0]
                return redirect(f'/{UserId}/shift')
    else:
        UsersInfo[UserId]={}
        DBCursor.execute("SELECT Name FROM workers WHERE Exist=True")
        Workers = list(set([row[0] for row in DBCursor.fetchall()]))
        return render_template('WorkerSelect.html', Workers=Workers)

@app.route('/<int:UserId>/stage_select', methods=['GET', 'POST'])
def StageSelect(UserId):
    global UsersInfo
    if request.method == 'POST':
        Stage=request.form['Stage']
        UsersInfo[UserId]['Stage'] = Stage
        if Stage in ["В'язання", "Оверлок"]:
            return redirect(f'/{UserId}/machine_select')
        else:
            DBCursor.execute(f"""SELECT Product FROM plans WHERE STAGE='{UsersInfo[UserId]['Stage'].replace("'", "''")}' AND Exist=True""")
            UsersInfo[UserId]['Product'] = DBCursor.fetchone()
            UsersInfo[UserId]['FirstSortGloveCount']=0
            UsersInfo[UserId]['SecondSortGloveCount']=0
            UsersInfo[UserId]['DefectSortGloveCount']=0
            UsersInfo[UserId]['ShiftStart']=datetime.now().strftime("%d.%m.%Y %H:%M")
            if UsersInfo[UserId]['Product'] != None:
                UsersInfo[UserId]['Product'] = UsersInfo[UserId]['Product'][0]
                return redirect(f'/{UserId}/shift')
            else:
                return redirect(f'/{UserId}/')
    else:
        return render_template('StageSelect.html', AvailableStages=AvailableStages)

@app.route('/<int:UserId>/machine_select', methods=['GET', 'POST'])
def MachineSelect(UserId):
    global UsersInfo
    if request.method == 'POST':
        Machine=request.form['Machine']
        print(Machine)
        UsersInfo[UserId]['Machine'] = Machine
        UsersInfo[UserId]['FirstSortGloveCount']=0
        UsersInfo[UserId]['SecondSortGloveCount']=0
        UsersInfo[UserId]['DefectSortGloveCount']=0
        UsersInfo[UserId]['ShiftStart']=datetime.now().strftime("%d.%m.%Y %H:%M")

        DBCursor.execute(f"""SELECT Product FROM plans WHERE Machine='{UsersInfo[UserId]['Machine']}' AND STAGE='{UsersInfo[UserId]['Stage'].replace("'", "''")}' AND Exist=True""")
        UsersInfo[UserId]['Product'] = DBCursor.fetchone()[0]

        return redirect(f'/{UserId}/shift')
    else:
        DBCursor.execute(f"""SELECT Machine FROM plans WHERE Stage='{UsersInfo[UserId]['Stage'].replace("'", "''")}'""")

        Machines=sorted(list(set([Machine[0] for Machine in DBCursor.fetchall()])))

        return render_template('MachineSelect.html', Machines=Machines, BackUrl=f'/{UserId}/stage_select' if len(AvailableStages)>1 else f'/{UserId}/')

@app.route('/<int:UserId>/shift', methods=['GET', 'POST'])
def Shift(UserId):
    global UsersInfo
    if request.method == 'POST':
         Stop=request.form['Stop']
         if Stop=='0':
            Sort=request.form['Sort']
            GloveCount=request.form['CountInput']
            SaveInfoToDB(UserId, Sort, GloveCount)
            if len(AvailableStages)>1 and UsersInfo[UserId]['Stage'] in ["В'язання", "Оверлок"]:
                BackUrl=f'/{UserId}/machine_select'
            elif len(AvailableStages)>1 and UsersInfo[UserId]['Stage'] not in ["В'язання", "Оверлок"]:
                BackUrl=f'/{UserId}/stage_select'
            else:
                BackUrl=f'/{UserId}/'

            if UsersInfo[UserId]['Stage'] not in ["В'язання", "Оверлок"]:
                ShiftName=f"Зміна ({UsersInfo[UserId]['Worker']}, {UsersInfo[UserId]['Stage']}, {UsersInfo[UserId]['Product']})"
            else:
                ShiftName=f"Зміна ({UsersInfo[UserId]['Worker']}, {UsersInfo[UserId]['Stage']}, {UsersInfo[UserId]['Machine']} машина, {UsersInfo[UserId]['Product']})"

            return render_template('Shift.html', BackUrl=BackUrl, ShiftName=ShiftName, FirstSortGloveCount=UsersInfo[UserId]['FirstSortGloveCount'], SecondSortGloveCount=UsersInfo[UserId]['SecondSortGloveCount'], DefectSortGloveCount=UsersInfo[UserId]['DefectSortGloveCount'], ShiftStart=UsersInfo[UserId]['ShiftStart'])
         else:
             SaveInfoToDB(UserId, '123', '0')
             return redirect(f'/{UserId}/')
    else:
        if len(AvailableStages)>1 and UsersInfo[UserId]['Stage'] in ["В'язання", "Оверлок"]:
            BackUrl=f'/{UserId}/machine_select'
        elif len(AvailableStages)>1 and UsersInfo[UserId]['Stage'] not in ["В'язання", "Оверлок"]:
            BackUrl=f'/{UserId}/stage_select'
        else:
            BackUrl=f'/{UserId}/'

        if UsersInfo[UserId]['Stage'] not in ["В'язання", "Оверлок"]:
            ShiftName=f"Зміна ({UsersInfo[UserId]['Worker']}, {UsersInfo[UserId]['Stage']}, {UsersInfo[UserId]['Product']})"
        else:
            ShiftName=f"Зміна ({UsersInfo[UserId]['Worker']}, {UsersInfo[UserId]['Stage']}, {UsersInfo[UserId]['Machine']} машина, {UsersInfo[UserId]['Product']})"

        return render_template('Shift.html', BackUrl=BackUrl, ShiftName=ShiftName, FirstSortGloveCount=UsersInfo[UserId]['FirstSortGloveCount'], SecondSortGloveCount=UsersInfo[UserId]['SecondSortGloveCount'], DefectSortGloveCount=UsersInfo[UserId]['DefectSortGloveCount'], ShiftStart=UsersInfo[UserId]['ShiftStart'])

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask,render_template,redirect,url_for,flash,request
import psycopg2
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,BooleanField
from wtforms.fields.html5 import DateField,IntegerField
from wtforms.validators import Length,DataRequired,NumberRange
from random import randint
from datetime import date




app=Flask(__name__)
format_string = "%B %d, %Y"
def connect_db():
    conn=psycopg2.connect(user='postgres',host='127.0.0.1',database='postgres',port='5432',password='Sivapt@64')
    return conn

def cityty():
    conn=connect_db()
    cur=conn.cursor()
    curr=cur.callproc('rto_loc',[])
    rea=cur.fetchone()
    res=rea[0].split(',')
    res.pop(0)
    if conn:
        cur.close()
        conn.close()
    return res
    

app.config['SECRET_KEY']='mysecretkey'

class vehForm(FlaskForm):
    o_name=StringField("Enter Your Name:",validators=[DataRequired()])
    city=StringField("Enter youy City:",validators=[DataRequired()])
    l_id=StringField("Enter Your License ID:",validators=[DataRequired()])
    phn=StringField("Enter Your Phone Number:",validators=[DataRequired()])
    submit=SubmitField("Submit")

class llrForm(FlaskForm):
    name=StringField("Enter Your Name:",validators=[DataRequired()])
    f_name=StringField("Enter Your Father's Name:",validators=[DataRequired()])
    city=StringField("Enter youy City:",validators=[DataRequired()])
    dob=DateField("Enter Your DOB:",default=date.today(),validators=[DataRequired()])
    submit=SubmitField("Submit")

class FitForm(FlaskForm):
    v_no=StringField("Enter Your Vehicle Number:",validators=[DataRequired()])
    doe=DateField("Enter The Expiry Date:",default=date.today(),validators=[DataRequired()])
    ac=BooleanField("Check If Accepted",default=False)
    submit=SubmitField("Submit")

class licForm(FlaskForm):
    llr_id=StringField("Enter Your LLR ID:",validators=[DataRequired()])
    e_id=StringField("Enter the Employee ID:",validators=[DataRequired()])
    test=BooleanField("Check If Passed The Test",default=False)
    submit=SubmitField("Submit")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/error')
def error():
    return render_template('error.html')


@app.route('/search',methods=['POST'])
def search():
    v_no=request.form['vno']
    v_no=v_no.upper()
    conn=connect_db()
    cur=conn.cursor()
    sql=f'''select * from search where v_no='{v_no}' '''
    cur.execute(sql)
    curr=cur.fetchone()
    if curr:
        return render_template('search.html',data=curr)
    else:
        flash("Search A Valid Vehicle!")
        return render_template('index.html')
    


@app.route('/emp')
def emp():
    conn=connect_db()
    cur=conn.cursor()
    sql=f'''select rto_id,name,tests_cond from rto_emp order by tests_cond desc'''
    cur.execute(sql)
    curr=cur.fetchall()
    rto=[]
    for i in curr:
        rto.append(i)
    rto_first=rto[0][1]
    flash("BEST EMPLOYEE OF THE YEAR:")
    return render_template('emp.html',first=rto_first,rto_emp=rto,j=0)

@app.route('/licensetest',methods=['GET','POST'])
def lictest():
    form = licForm()
    if form.validate_on_submit():
        conn=connect_db()
        cur=conn.cursor()
        llr_id=form.llr_id.data.upper()
        llr=[]
        sql=f'''select llr_id from llr_reg '''
        cur.execute(sql)
        curr=cur.fetchall()
        for i in curr:
            llr.append(i[0])

        if llr_id not in llr:
            flash("Enter a valid LLR ID")
            form.llr_id.data=''
            return render_template('ltest.html',form=form)

        e_id=form.e_id.data.upper()
        llr=[]
        sql=f'''select e_id from rto_emp '''
        cur.execute(sql)
        curr=cur.fetchall()
        for i in curr:
            llr.append(i[0])

        sql=f'''select city from rto_emp where e_id='{e_id}' ''' 
        cur.execute(sql)
        emp_city=cur.fetchone()

        sql=f'''select city from llr_reg where llr_id='{llr_id}' '''
        cur.execute(sql)
        app_city=cur.fetchone()


        if e_id not in llr:
            flash("Enter a valid Employee ID")
            form.e_id.data=''
            return render_template('ltest.html',form=form)
        
        if emp_city[0] != app_city[0]:
            flash("Enter a Employee ID Working In Your City!")
            return render_template('ltest.html',form=form)


        test=form.test.data
        dot=date.today()
        dot=dot.strftime("%d-%m-%Y")
        sql=f''' select * from lic_gra where llr_id='{llr_id}' '''
        cur.execute(sql)
        curr=cur.fetchone()
        print(curr)
        if curr:
            sql=f'''delete from lic_gra where llr_id='{llr_id}' '''
            cur.execute(sql)
            conn.commit()
        
        sql=f'''insert into lic_gra values('{llr_id}','{test}','{e_id}','{dot}') '''
        cur.execute(sql)
        
        conn.commit()
        if conn:
            cur.close()
            conn.close()
        return render_template('thankyoulic.html',llr_id=llr_id,e_id=e_id,test=test)
    return render_template('ltest.html',form=form)
        

@app.route('/ex_fit',methods=['GET','POST'])
def fit_ex():
    form=FitForm()
    if form.validate_on_submit():
        conn=connect_db()
        cur=conn.cursor()
        
        v_no=form.v_no.data.upper()
        sql=f'''select v_no from veh_reg '''
        cur.execute(sql)
        curr=cur.fetchall()
        vno=[]
        for i in curr:
            vno.append(i[0])
        print(vno)
        print(v_no)
        if v_no not in vno:
            flash("Enter a valid Vehicle Number")
            form.v_no.data=''
            return render_template('fit.html',form=form)
        sql=f'''select o_name from veh_reg where v_no='{v_no}' '''
        cur.execute(sql)
        curr=cur.fetchone()
        name=curr[0]
        print(name)
        doe=form.doe.data
        ac=form.ac.data
        sql=f'''select f_id from fit_cert'''
        cur.execute(sql)
        curr=cur.fetchall()
        fid=[]
        for i in curr:
            fid.append(i[0])
        f_id=name[:2:1].upper()+str(randint(0,9))
        while(f_id in fid):
           f_id=name[:2:1].upper()+str(randint(0,9))
        
        sql=f'''delete from fit_cert where v_no='{v_no}' '''
        cur.execute(sql)
        sql=f'''insert into fit_cert values('{v_no}','{ac}','{f_id}','{doe}')'''
        cur.execute(sql)
        conn.commit()
        print("Inserted successfully")
        
        #print(ac)
        #print(ex_date)
        
        #if ac:
        #    sql=f'''update veh_reg set ex_date='{ex_date}' where v_no='{v_no}' '''
        #    cur.execute(sql)
        #else:
         #   sql=f'''delete from veh_reg where v_no='{v_no}' '''
        #    cur.execute(sql)
        
        conn.commit()
        if conn:
            cur.close()
            conn.close()
        return render_template('thankyou_fit.html',v_no=v_no,noy=doe,ac=ac,fid=f_id)
    return render_template('fit.html',form=form)



@app.route('/llr_reg',methods=['GET','POST'])
def llr():
    form=llrForm()
    cities=cityty()
    if form.validate_on_submit():
        conn=connect_db()
        cur=conn.cursor()
        name=form.name.data.upper()
        f_name=form.f_name.data.upper()
        dob=form.dob.data.strftime('%d-%m-%Y')
        #dob1=dob.split('-')
        #dob1[-1]=int(dob1[-1])+3
        #print(dob1)
        #dob=str(dob1[0])+'-'+str(dob1[1])+'-'+str(dob1[2])
        #print(dob)
        city=form.city.data.upper()
        #city=city.lower()
        sql=f'''select rto_id from rto_loc where city='{city}' '''
        cur.execute(sql)
        curr=cur.fetchone()
        print(curr)
    
        if not curr:
          flash("Enter A Valid City!")
          form.city.data=''
          return render_template('llr.html',form=form,cities=cities)
        else:
            rto_id=curr[0]

        sql='''select llr_id from llr_reg'''
        cur.execute(sql)
        llrid=[]
        for i in cur.fetchall():
            llrid.append(i[0])
        llr_id=name[:3:1].upper()+str(randint(1000,9999))
        while(llr_id in llrid):
           llr_id=name[:3:1].upper()+str(randint(1000,9999))

        sql=f'''insert into llr_reg values('{llr_id}','{name}','{dob}','{f_name}','{city}' )'''

        cur.execute(sql)
        conn.commit()
        if conn:
            cur.close()
            conn.close()  
        return render_template('thankyou_llr.html',name=name,f_name=f_name,dob=dob,city=city,llr_id=llr_id)

    return render_template('llr.html',form=form,cities=cities)

@app.route('/vehicle',methods=['GET','POST'])
def vehreg():
    form=vehForm()
    cities=cityty()
    if form.validate_on_submit():
        conn=connect_db()
        cur=conn.cursor()
        o_name=form.o_name.data.upper()
        
        sql='''select v_no from veh_reg'''
        cur.execute(sql)
        veh_no=[]
        for i in cur.fetchall():
            veh_no.append(i[0])
    
        v_no=o_name[:4:1]+str(randint(1000,9999))
        print (v_no)
        print(veh_no)
        phn=form.phn.data
        dor=date.today()
        dor=dor.strftime("%d-%m-%Y")
        dob1=dor.split('-')
        dob1[-1]=int(dob1[-1])+7
        #print(dob1)
        ex_date=str(dob1[0])+'-'+str(dob1[1])+'-'+str(dob1[2])
        #print(dob)
        while(v_no in veh_no):
           v_no=o_name[:4:1]+str(randint(1000,9999))

        city=form.city.data.upper()
        sql=f'''select rto_id from rto_loc where city='{city}' '''
        cur.execute(sql)
        curr=cur.fetchone()
        print(curr)
    
        if not curr:
          flash("Enter A Valid City!")
          form.city.data=''
          return render_template('vehreg.html',form=form,cities=cities)
        else:
            rto_id=curr[0]
        print(rto_id)
        l_id=form.l_id.data.upper()
        sql=f'''select l_id from lic_reg'''
        cur.execute(sql)
        curr=cur.fetchall()
        le_id=[]
        for i in curr:
            le_id.append(i[0])
        print(le_id)
        if not (l_id in le_id):
            flash("Enter A Valid License ID!")
            form.l_id.data=''
            return render_template('vehreg.html',form=form)
        print(le_id)
        
        sql=f'''insert into veh_reg values('{v_no}','{o_name}','{city}','{rto_id}','{dor}','{phn}','{ex_date}','{l_id}')'''

        cur.execute(sql)
        conn.commit()
        print("Executed Successfully")
        if conn:
            cur.close()
            conn.close()
        return render_template('thankyou.html',name=o_name,v_no=v_no,date=dor,exp=ex_date)
    return render_template('vehreg.html',form=form,cities=cities)

if __name__=='__main__':
    app.run()
    
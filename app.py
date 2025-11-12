from flask import Flask ,render_template , redirect , flash ,request ,url_for
import secrets 
from webforms import UserForm , LoginForm , BookingForm
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash , check_password_hash
from datetime import datetime ,timedelta ,date
from flask_migrate import Migrate
import csv , os
from flask_login import  LoginManager, UserMixin , current_user ,login_required , login_user, logout_user


app = Flask(__name__)
# configure
secret_key = secrets.token_hex(16)
app.config['SECRET_KEY'] = secret_key

# database setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db  = SQLAlchemy(app)  #initialization 
migrate = Migrate(app,db)

CSV_FOLDER = os.path.join(app.root_path, 'csv')
def load_places_from_csv(filename, country=None , place = None):
    places = []
    filepath = os.path.join(CSV_FOLDER, filename)
    with open(filepath, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            row['country_name'] = row['country_name'].lower()
            # Check if both country and place are provided
            if country and place:
                row['place_name'] = row['place_name'].lower()
                if row['country_name'] == country.lower() and row['place_name'] == place.lower():
                    places.append(row)
                    break 
            # If only country is provided
            elif country:
                if row['country_name'] == country.lower():
                    places.append(row)
            else:
                places.append(row)
    return places


@app.route('/<country>')
def country_wise(country):
    places = load_places_from_csv('places.csv',country)
    return render_template('places.html',places = places)

@app.route('/<country>/<place>')
def place(country, place):
    info = load_places_from_csv('places.csv', country , place)
    print(info)
    if info:
        place_info = info[0]  
    else:
        place_info = None 
    return render_template('place.html', place = place_info )

@app.route('/<country>/<place>/book_trip',methods = ['GET','POST'])
def book_trip(country , place):
    form = BookingForm()
    info = load_places_from_csv('places.csv', country , place)
    if info:
        place_info = info[0]  
        form.country.data = place_info['country_name'].title()
        form.place.data = place_info['place_name'].title()
    else:
        place_info = None
        
    print(place_info)
    if form.validate_on_submit():
        print(form.date_of_trip.data)
        trip = UserTrips(country = form.country.data , place = form.place.data , date_of_trip = form.date_of_trip.data)
        # print(trip)
        print(form.date_of_trip.data)
        db.session.add(trip)
        db.session.commit()
        flash(f"Happy Journey To !!{ form.place.data }")

        return redirect(url_for('mytrips'))
    else:
        print("Form validation failed:", form.errors)
    return render_template('book_trip.html',form = form ,country = country , place = place)


@app.route('/mytrips/cancel_trip/<int:trip_id>')
def cancel_trip(trip_id):
    trip_to_cancel = UserTrips.query.get_or_404(trip_id)
    print(trip_to_cancel)
    if trip_to_cancel:
        db.session.delete(trip_to_cancel)
        db.session.commit()  
        flash("cancelled Trip..!")
        return redirect(url_for('mytrips'))
    return render_template('500.html')
@app.route('/mytrips')
@login_required
def mytrips():
    our_users = Users.query.order_by(Users.date_added)
    trips = UserTrips.query.order_by(UserTrips.date_of_booking).all()
    current_date = date.today()
    return render_template('mytrips.html',our_users = our_users , trips = trips ,current_date = current_date)

@app.route('/')
def home():
    places = load_places_from_csv('country.csv')
    print(places)
    return render_template("index.html" , places = places )

# flask log in stufff
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


@app.route("/admin")
@login_required
def admin():
    id = current_user.id
    if id == 3 :
        our_users = Users.query.order_by(Users.date_added)
        trips = UserTrips.query.order_by(UserTrips.date_of_booking).all()
        current_date = date.today()

        return render_template("admin.html",our_users = our_users , trips = trips , current_date = current_date)
    else :
        flash("Sorry u must be a admin.....")
        return redirect(url_for("dashboard"))


@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username = form.username.data).first()
        if user :
            if check_password_hash(user.password_hash,form.password.data):
                login_user(user)
                form.username.data = ''
                form.password.data = ''
                return redirect(url_for('dashboard'))
            else:
                flash("wrong password !")
        else:
            flash("user doesnt exist ")            
    return render_template('login.html',form = form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('logout')
    return redirect(url_for('login'))

@app.route('/dashboard' , methods = ['GET','POST'])
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/register' , methods= ['GET','POST']) 
def register():
    form = UserForm()
    name = None
    username = None
    email = None
    password = None
    if form.validate_on_submit():
        user = Users.query.filter_by(email = form.email.data).first()
        if user is None:
            password_hash = generate_password_hash(form.password.data)
            user = Users(name = form.name.data,email = form.email.data ,username = form.username.data , password_hash = password_hash)
            db.session.add(user)
            db.session.commit()
    form.name.data = ''
    form.email.data = ''
    form.password.data = ''
    form.username.data = ''
    flash("Registration successful..!!")
    our_users = Users.query.order_by(Users.date_added)
    return render_template('register.html' , form = form ,name= name ,username = username, email= email ,password = password , our_users = our_users)

@app.route('/update/<int:id>',methods=["GET","POST"])
@login_required
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.username = request.form['username']
        try:
            db.session.commit()
            flash("User Updated Succesfully")
            return render_template("update.html" , form = form ,name_to_update = name_to_update )
        except:
            flash("Error..!! looks like there was a problem ... Try again later...")
            return render_template("update.html" , form = form ,name_to_update = name_to_update ,id = id)
    else:
        return render_template("update.html" , form = form ,name_to_update = name_to_update ,id = id)

@app.route('/delete/<int:id>',methods=["GET","POST"])
def delete(id):
    if id == current_user.id:
        user_to_delete = Users.query.get_or_404(id)
        form = UserForm()
        try:
            db.session.delete(user_to_delete)
            db.session.commit()
            flash("User deleted successfully")
            our_users = Users.query.order_by(Users.date_added)
            return render_template("register.html" , form = form ,our_users = our_users)
        except:
            flash("whoops there was a problem in deleting user ... Try Again...!!")
            our_users = Users.query.order_by(Users.date_added)
            return render_template("register.html" , form = form , our_users = our_users)
    else :
        flash("whoops You kiddy Dont delete other users  ... Try Again...!!")
        return redirect(url_for('dashboard'))

# custom error messages 
# invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"),404

# internal server error 
@app.errorhandler(500)
def page_not_found(e):
    return render_template("404.html"),500


# users db
class Users(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key = True )
    username = db.Column(db.String(200),nullable=True,unique = True)
    name = db.Column(db.String(200),nullable = False)
    email = db.Column(db.String(100),nullable = False , unique =True)
    password_hash = db.Column(db.String(128))
    date_added = db.Column(db.DateTime , default = datetime.utcnow)
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self,password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)
    
    #create string
    def __repr__(self):
        return '<Name %r>' % self.name

class UserTrips(db.Model):
    trip_id = db.Column(db.Integer,primary_key = True)
    country = db.Column(db.String(200),nullable = False)
    place = db.Column(db.String(255),nullable=False)
    date_of_trip = db.Column(db.Date)
    date_of_booking = db.Column(db.DateTime, default = datetime.utcnow)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
    
    
    
    
      # companions = db.Column(db.String(255))
    # cost = db.Column(db.Float , nullable=False) 
    # trip_experience = db.Column(db.Text)
    
    
     # flash(f"Happy Journey To !!{ form.place.data }")
        # form.date_of_trip.data= ''
        # form.guide.data = ''
        # form.place.data = ''
        # form.country.data = ''
        # # return render_template('login.html')
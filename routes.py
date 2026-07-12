from flask import Flask,redirect,render_template,request,url_for,Blueprint,flash,session
from models import db,Admin,Staff,Trek,Trekker,Booking
from flask_login import login_user
from functools import wraps
from sqlalchemy import func,or_
import os
from werkzeug.security import generate_password_hash,check_password_hash
from datetime import datetime,date

main_bp = Blueprint('main',__name__)

@main_bp.route('/')
def index():
    return render_template('index.html')


# admin routes

@main_bp.route('/admin_login')
def admin_login():
    return render_template('admin/admin_login.html')

@main_bp.route('/admin_login',methods=['POST'])
def admin_login_post():
    email = request.form.get('email')
    password = request.form.get('passhash')

    admin = Admin.query.filter_by(email=email).first()

    if admin is None:
        return "Invalid email"

    if admin.passhash != password:
        return "Invalid password"


    session.clear()
    session['role'] = 'admin'
    session['admin_id'] =admin.id
    return redirect(url_for('main.admin_dashboard'))

@main_bp.route('/admin_dashboard')
def admin_dashboard():
    total_treks = Trek.query.count()
    total_trekker = Trekker.query.count()
    total_staff = Staff.query.count()
    total_booking = Booking.query.count()

    return render_template('admin/admin_dashboard.html',total_booking=total_booking,total_staff=total_staff,total_trekker=total_trekker,total_treks=total_treks)


@main_bp.route('/admin_staff_list')
def admin_staff_list():
    if 'admin_id' not in session:
        return redirect(url_for('main.admin_login'))
    staffs = Staff.query.all()
    return render_template('admin/admin_staff_list.html',staffs=staffs)

@main_bp.route('/admin/staff/<int:id>/approve')
def approve_staff(id):
    staff = Staff.query.get_or_404(id)
    staff.approval_status = 'Approved'
    db.session.commit()
    return redirect(url_for('main.admin_staff_list'))

@main_bp.route('/admin/staff/<int:id>/blacklist')
def blacklist_staff(id):
    staff = Staff.query.get_or_404(id)
    staff.approval_status = 'Blacklist'
    db.session.commit()
    return redirect(url_for('main.admin_staff_list'))

@main_bp.route('/admin/staff/<int:id>/reject')
def reject_staff(id):
    staff = Staff.query.get_or_404(id)
    staff.approval_status = 'Rejected'
    db.session.commit()
    return redirect(url_for('main.admin_staff_list'))


@main_bp.route('/admin_trek_list')
def admin_trek_list():
    if 'admin_id' not in session:
        return redirect(url_for('main.admin_login'))

    treks = Trek.query.all()

    return render_template(
        'admin/admin_trek_list.html',
        treks=treks
    )

@main_bp.route('/admin/edit_trek/<int:id>')
def edit_trek(id):
    if 'admin_id' not in session:
        return redirect(url_for('main.admin_login'))

    trek = db.session.get(Trek, id)

    if trek is None:
        flash("Trek not found.", "danger")
        return redirect(url_for('main.admin_trek_list'))

    staff = Staff.query.all()
    return render_template('admin/edit_trek.html', trek=trek, staff=staff)


@main_bp.route('/admin/edit_trek/<int:id>', methods=['POST'])
def edit_trek_post(id):
    if 'admin_id' not in session:
        return redirect(url_for('main.admin_login'))

    trek = db.session.get(Trek, id)

    if trek is None:
        flash("Trek not found.", "danger")
        return redirect(url_for('main.admin_trek_list'))

    trek.trek_name = request.form.get("trek_name")
    trek.location = request.form.get("location")
    trek.difficulty = request.form.get("difficulty")
    trek.duration = request.form.get("duration")
    trek.available_slots = request.form.get("available_slots")
    trek.start_date = datetime.strptime(request.form.get("start_date"),"%Y-%m-%d").date()
    trek.end_date = datetime.strptime(request.form.get("end_date"), "%Y-%m-%d").date()
    trek.staff_id = request.form.get("staff_id")
    

    db.session.commit()

    flash("Trek updated successfully!", "success")
    return redirect(url_for('main.admin_trek_list'))

@main_bp.route('/admin/close_trek/<int:id>',methods=['POST'])
def close_trek(id):
    if 'admin_id' not in session:
        return redirect(url_for('main.admin_login'))

    trek = db.session.get(Trek, id)

    if trek is None:
        flash("Trek not found.", "danger")
        return redirect(url_for('main.admin_trek_list'))

    trek.status = "Closed"
    db.session.commit()

    flash("Trek has been closed.", "success")
    return redirect(url_for('main.admin_trek_list'))

    

@main_bp.route('/admin_trekker_list')
def admin_trekker_list():

    if 'admin_id' not in session:
        return redirect(url_for('main.admin_login'))

    trekkers = Trekker.query.all()

    return render_template(
        'admin/admin_trekker_list.html',
        trekkers=trekkers
    )

@main_bp.route('/admin/trekker/<int:id>/blacklist')
def blacklist_trekker(id):

    if 'admin_id' not in session:
        return redirect(url_for('main.admin_login'))

    trekker = Trekker.query.get_or_404(id)

    trekker.is_active = False

    db.session.commit()

    flash("Trekker has been blacklisted.", "success")

    return redirect(url_for('main.admin_trekker_list'))

@main_bp.route('/admin/trekker/<int:id>/activate')
def activate_trekker(id):

    if 'admin_id' not in session:
        return redirect(url_for('main.admin_login'))

    trekker = Trekker.query.get_or_404(id)

    trekker.is_active = True

    db.session.commit()

    flash("Trekker has been activated.", "success")

    return redirect(url_for('main.admin_trekker_list'))


@main_bp.route('/admin_booking_list')
def admin_booking_list():

    if 'admin_id' not in session:
        return redirect(url_for('main.admin_login'))

    bookings = Booking.query.all()

    return render_template(
        'admin/admin_booking_list.html',
        bookings=bookings
    )

@main_bp.route('/admin_profile')
def admin_profile():
    if 'admin_id' not in session:
        return redirect(url_for('main.admin_login'))

    admin = db.session.get(Admin, session['admin_id'])

    return render_template(
        'admin/admin_profile.html',
        admin=admin
    )
   
@main_bp.route('/admin_profile',methods=["POST"])
def admin_profile_post():
    admin = Admin.query.get(session['admin_id'])
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')
    cpassword = request.form.get('cpassword')
    if email == '' or password== '' or cpassword == '':
        flash('email or password cannot be empty')
        return redirect(url_for('main.admin_profile'))
    admin.email= email
    admin.name=name
    admin.password =password
    db.session.commit()
    flash('Profile upadted successfully')
    return redirect(url_for('main.admin_profile'))

@main_bp.route('/admin/create_trek')
def create_trek():

    staffs = Staff.query.filter_by(approval_status="Approved").all()

    return render_template(
        'admin/create_trek.html',
        staffs=staffs
    )  

@main_bp.route('/admin/create_trek', methods=['POST'])
def create_trek_post():

    trek = Trek(
        trek_name=request.form.get('trek_name'),
        location=request.form.get('location'),
        difficulty=request.form.get('difficulty'),
        duration=int(request.form.get('duration')),
        available_slots=int(request.form.get('available_slots')),
        staff_id=int(request.form.get('staff_id')),
        start_date=datetime.strptime(
            request.form.get('start_date'),
            '%Y-%m-%d'
        ).date(),
        end_date=datetime.strptime(
            request.form.get('end_date'),
            '%Y-%m-%d'
        ).date(),
        description=request.form.get('description'),
        status='Open'
    )

    db.session.add(trek)
    db.session.commit()

    flash("Trek created successfully.", "success")

    return redirect(url_for('main.admin_dashboard'))


@main_bp.route('/admin/search')
def admin_search():

    if 'admin_id' not in session:
        return redirect(url_for('main.admin_login'))

    q = request.args.get('q', '').strip()

    trekkers = Trekker.query.filter(
        or_(
            Trekker.name.ilike(f'%{q}%'),
            Trekker.email.ilike(f'%{q}%')
        )
    ).all()

    staffs = Staff.query.filter(
        or_(
            Staff.name.ilike(f'%{q}%'),
            Staff.email.ilike(f'%{q}%')
        )
    ).all()

    treks = Trek.query.filter(
        or_(
            Trek.trek_name.ilike(f'%{q}%'),
            Trek.location.ilike(f'%{q}%'),
            Trek.difficulty.ilike(f'%{q}%')
        )
    ).all()

    return render_template(
        'admin/admin_search.html',
        query=q,
        trekkers=trekkers,
        staffs=staffs,
        treks=treks
    )
# staff routes

@main_bp.route('/staff_login')
def staff_login():
    return render_template('/staff/staff_login.html')

@main_bp.route('/staff_login',methods=['POST'])
def staff_login_post():
    email = request.form.get('email')
    password = request.form.get('passhash')
    staff = Staff.query.filter_by(email=email).first()

    if not staff:
        flash('please enter valid email..❌')
        return redirect(url_for('main.staff_login'))
    
    if not check_password_hash(staff.passhash,password):
        flash('please enter valid  password..❌')
        return redirect(url_for('main.staff_login'))
    

    if staff.approval_status == "Rejected":
        flash('Your account is rejected by admin contact admin for any clarification...❌')
        return redirect(url_for('main.staff_login'))
    
    elif staff.approval_status == "Blacklisted":
        flash('Your account is blacklisted by admin ...❌')
        return redirect(url_for('main.staff_login'))

    elif staff.approval_status != "Approved":
        flash('Your account is not yet approved by admin ...')
        return redirect(url_for('main.staff_login'))
    
    session.clear()
    session['role'] = 'staff'      
    session['staff_id'] = staff.id
    return redirect(url_for('main.staff_dashboard'))

@main_bp.route('/staff/staff_register')
def staff_register():
    return render_template('/staff/staff_register.html')

@main_bp.route('/staff/staff_register',methods=['POST'])
def staff_register_post():
    name = request.form.get('name')
    email = request.form.get('email')
    contact = request.form.get('contact')
    password = request.form.get("passhash")

    passhash = generate_password_hash(password)

    if email == '' or password == '':
        flash('Required password and email to reigster requred fields cannot be empty.')
        return redirect(url_for('main.staff_register'))
    
    if Staff.query.filter_by(email=email).first():
        flash("Email is being used by another staff.")
        return redirect(url_for('main.staff_register'))
    

    staff = Staff(name=name,email=email,passhash=passhash,contact=contact)

    db.session.add(staff)
    db.session.commit()

    flash('Registerd successfully,Wait for Admins Approval')
    return render_template('/staff/staff_login.html')


from datetime import date

@main_bp.route('/staff/staff_dashboard')
def staff_dashboard():
    if 'staff_id' not in session:
        return redirect(url_for('main.staff_login'))

    staff = Staff.query.get_or_404(session['staff_id'])

    today = date.today()

    assigned_treks = Trek.query.filter(
        Trek.staff_id == staff.id,
        Trek.status != "Completed",
        Trek.end_date >= today
    ).all()

    past_assigned_treks = Trek.query.filter(
        Trek.staff_id == staff.id
    ).filter(
        (Trek.status == "Completed") |
        (Trek.end_date < today)
    ).all()

    total_registered_users = sum(
        len(trek.booking) for trek in assigned_treks
    )

    return render_template(
        'staff/staff_dashboard.html',
        staff=staff,
        assigned_treks=assigned_treks,
        past_assigned_treks=past_assigned_treks,
        total_registered_users=total_registered_users
    )



from datetime import date

@main_bp.route('/staff_assigned_treks')
def staff_assigned_treks():
    if 'staff_id' not in session:
        return redirect(url_for('main.staff_login'))

    staff = Staff.query.get_or_404(session['staff_id'])
    today = date.today()

    treks = Trek.query.filter(
        Trek.staff_id == staff.id,
        Trek.status != "Completed",
        Trek.end_date >= today
    ).all()

    for trek in treks:
        trek.booked_count = Booking.query.filter_by(
            trek_id=trek.id,
            status="Booked"
        ).count()

    return render_template(
        'staff/staff_assigned_treks.html',
        staff=staff,
        treks=treks
    )

@main_bp.route('/staff/past_assigned_treks')
def staff_past_assigned_treks():
    if 'staff_id' not in session:
        return redirect(url_for('main.staff_login'))

    staff = Staff.query.get_or_404(session['staff_id'])
    today = date.today()

    past_assigned_treks = Trek.query.filter(
        Trek.staff_id == staff.id
    ).filter(
        (Trek.status == "Completed") |
        (Trek.end_date < today)
    ).all()

    return render_template(
        'staff/past_assigned_treks.html',
        staff=staff,
        past_assigned_treks=past_assigned_treks
    )

@main_bp.route('/staff_registered_users')
def staff_registered_users():

    if 'staff_id' not in session:
        return redirect(url_for('main.staff_login'))

    bookings = (
        Booking.query
        .join(Trek)
        .join(Trekker)
        .filter(Trek.staff_id == session['staff_id'])
        .all()
    )

    return render_template(
        'staff/staff_registered_users.html',
        bookings=bookings
    )

@main_bp.route('/staff_trek_trekker/<int:trek_id>')
def staff_trek_trekker(trek_id):

    if 'staff_id' not in session:
        return redirect(url_for('main.staff_login'))

    trek = Trek.query.filter_by(
        id=trek_id,
        staff_id=session['staff_id']
    ).first_or_404()

    bookings = (
        Booking.query
        .join(Trekker)
        .filter(Booking.trek_id == trek.id)
        .all()
    )

    return render_template(
        'staff/staff_trek_trekker.html',
        trek=trek,
        bookings=bookings
    )

@main_bp.route('/staff/remove_booking/<int:booking_id>')
def staff_remove_booking(booking_id):

    if 'staff_id' not in session:
        return redirect(url_for('main.staff_login'))

    booking = Booking.query.get_or_404(booking_id)

    trek = Trek.query.filter_by(
        id=booking.trek_id,
        staff_id=session['staff_id']
    ).first_or_404()

    db.session.delete(booking)

    trek.available_slots += 1

    db.session.commit()

    flash("User removed from trek successfully.", "success")

    return redirect(url_for(
        'main.staff_trek_trekker',
        trek_id=trek.id
    ))

@main_bp.route('/staff/profile')
def staff_profile():
    if 'staff_id' not in session:
        return redirect(url_for('main.staff_login'))

    staff = Staff.query.get_or_404(session['staff_id'])

    return render_template(
        'staff/staff_profile.html',
        staff=staff
    )

@main_bp.route('/staff/profile', methods=['POST'])
def staff_profile_post():
    if 'staff_id' not in session:
        return redirect(url_for('main.staff_login'))

    staff = Staff.query.get_or_404(session['staff_id'])

    staff.name = request.form.get('name')
    staff.email = request.form.get('email')
    staff.contact = request.form.get('contact')

    new_password = request.form.get('password')

    if new_password:
        staff.passhash = generate_password_hash(new_password)

    db.session.commit()

    flash("Profile updated successfully!", "success")

    return redirect(url_for('main.staff_profile'))

@main_bp.route('/staff/trek/<int:id>/update_slots', methods=['POST'])
def update_trek_slots(id):

    if 'staff_id' not in session:
        return redirect(url_for('main.staff_login'))

    trek = Trek.query.get_or_404(id)

    trek.available_slots = int(request.form['available_slots'])

    db.session.commit()

    flash('Available slots updated successfully.', 'success')

    return redirect(url_for('main.staff_assigned_treks'))

@main_bp.route('/staff/trek/<int:id>/update_status', methods=['POST'])
def update_trek_status(id):

    if 'staff_id' not in session:
        return redirect(url_for('main.staff_login'))

    trek = Trek.query.get_or_404(id)

    trek.status = request.form['status']

    db.session.commit()

    flash('Trek status updated successfully.', 'success')

    return redirect(url_for('main.staff_assigned_treks'))


# trekker routes

@main_bp.route('/trekker_login')
def trekker_login():
    return render_template('trekker/trekker_login.html')

@main_bp.route('/trekker_login',methods=['POST'])
def trekker_login_post():
    email = request.form.get('email')
    password = request.form.get('passhash')

    trekker  = Trekker.query.filter_by(email=email).first()
    if not trekker:
        flash('please enter valid email..❌')
        return redirect(url_for('main.trekker_login'))

    elif not check_password_hash(trekker.passhash,password):
        flash('please enter valid password..❌')
        return redirect(url_for('main.trekker_login'))
    
    trekker = Trekker.query.filter_by(email=email).first()

    if trekker and check_password_hash(trekker.passhash, password):

        if not trekker.is_active:
            flash("Your account has been blacklisted by the administrator.", "danger")
            return redirect(url_for('main.trekker_login'))

        session['trekker_id'] = trekker.id

        return redirect(url_for('main.trekker_dashboard'))
        
    session.clear()
    session['role'] = 'trekker'
    session['trekker_id'] = trekker.id
    return redirect(url_for('main.trekker_dashboard'))


@main_bp.route('/trekker_register')
def trekker_register():
    return render_template('trekker/trekker_register.html')

@main_bp.route('/trekker_register',methods=['POST'])
def trekker_register_post():
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    password = request.form.get("passhash")

    passhash = generate_password_hash(password)

    if email == '' or password == '':
        flash('Required password and email to reigster requred fields cannot be empty.')
        return redirect(url_for('main.trekker_register'))
    
    if Trekker.query.filter_by(email=email).first():
        flash("Email is being used by another trekker.")
        return redirect(url_for('main.trekker_register'))
    

    trekker = Trekker(name=name,email=email,passhash=passhash,phone=phone)

    db.session.add(trekker)
    db.session.commit()

    flash('Registerd successfully..')
    return redirect(url_for('main.trekker_login'))

from datetime import date

@main_bp.route('/trekker_dashboard')
def trekker_dashboard():

    if 'trekker_id' not in session:
        return redirect(url_for('main.trekker_login'))

    trekker = Trekker.query.get_or_404(session['trekker_id'])

    today = date.today()

    available_treks = Trek.query.filter(
        Trek.status == "Open",
        Trek.end_date >= today
    ).all()

    booked_treks = Booking.query.join(Trek).filter(
        Booking.trekker_id == trekker.id,
        Booking.status == "Booked",
        Trek.status != "Completed",
        Trek.end_date >= today
    ).all()

    trek_history = Booking.query.join(Trek).filter(
        Booking.trekker_id == trekker.id
    ).filter(
        (Booking.status == "Completed") |
        (Trek.status == "Completed") |
        (Trek.end_date < today)
    ).all()

    return render_template(
        "trekker/trekker_dashboard.html",
        trekker=trekker,
        available_treks=available_treks,
        booked_treks=booked_treks,
        trek_history=trek_history
    )

@main_bp.route('/trekker/available_treks')
def available_treks():

    if 'trekker_id' not in session:
        return redirect(url_for('main.trekker_login'))

    today = date.today()

    treks = Trek.query.filter(
        Trek.status == "Open",
        Trek.end_date >= today
    ).all()

    booked_slots = {}

    for trek in treks:
        booked_slots[trek.id] = Booking.query.filter_by(
            trek_id=trek.id,
            status="Booked"
        ).count()

    return render_template(
        'trekker/available_treks.html',
        treks=treks,
        booked_slots=booked_slots
    )

@main_bp.route('/trekker/my_bookings')
def my_bookings():

    if 'trekker_id' not in session:
        return redirect(url_for('main.trekker_login'))

    trekker = Trekker.query.get_or_404(session['trekker_id'])
    today = date.today()

    bookings = Booking.query.join(Trek).filter(
        Booking.trekker_id == trekker.id,
        Booking.status == "Booked",
        Trek.status != "Completed",
        Trek.end_date >= today
    ).order_by(Booking.booking_slot.desc()).all()

    return render_template(
        "trekker/my_bookings.html",
        bookings=bookings
    )

@main_bp.route('/trekker/trek_history')
def trek_history():

    if 'trekker_id' not in session:
        return redirect(url_for('main.trekker_login'))

    trekker = Trekker.query.get_or_404(session['trekker_id'])
    today = date.today()

    history = Booking.query.join(Trek).filter(
        Booking.trekker_id == trekker.id
    ).filter(
        (Booking.status == "Completed") |
        (Trek.status == "Completed") |
        (Trek.end_date < today)
    ).order_by(Trek.end_date.desc()).all()

    return render_template(
        "trekker/trek_history.html",
        history=history
    )

@main_bp.route('/trekker/book_trek/<int:id>')
def book_trek(id):

    if 'trekker_id' not in session:
        return redirect(url_for('main.trekker_login'))

    trekker = Trekker.query.get(session['trekker_id'])
    trek = Trek.query.get_or_404(id)

    return render_template(
        'trekker/book_trek.html',
        trekker=trekker,
        trek=trek
    )
@main_bp.route('/trekker/book_trek/<int:id>', methods=['POST'])
def book_trek_post(id):

    if 'trekker_id' not in session:
        return redirect(url_for('main.trekker_login'))

    trekker = Trekker.query.get_or_404(session['trekker_id'])
    trek = Trek.query.get_or_404(id)

    # Trek must be open for booking
    if trek.status != "Open":
        flash("This trek is not open for booking.", "warning")
        return redirect(url_for('main.available_treks'))

    # Check if slots are available
    if trek.available_slots <= 0:
        flash("No slots available for this trek.", "danger")
        return redirect(url_for('main.available_treks'))

    # Prevent duplicate booking
    booking = Booking.query.filter_by(
        trekker_id=trekker.id,
        trek_id=trek.id
    ).first()

    if booking:
        flash("You have already booked this trek.", "warning")
        return redirect(url_for('main.available_treks'))

    # Create booking
    booking = Booking(
        trekker_id=trekker.id,
        trek_id=trek.id,
        status="Booked"
    )

    db.session.add(booking)

    # Reduce available slots
    trek.available_slots -= 1

    db.session.commit()

    flash("Trek booked successfully!", "success")
    return redirect(url_for('main.my_bookings'))


@main_bp.route('/trekker/trekker_profile')
def trekker_profile():

    if 'trekker_id' not in session:
        return redirect(url_for('main.trekker_login'))

    trekker = Trekker.query.get_or_404(session['trekker_id'])

    return render_template(
        'trekker/trekker_profile.html',
        trekker=trekker
    )
@main_bp.route('/trekker/trekker_profile', methods=['POST'])
def trekker_profile_post():

    if 'trekker_id' not in session:
        return redirect(url_for('main.trekker_login'))

    trekker = Trekker.query.get_or_404(session['trekker_id'])

    email = request.form.get('email')

    existing = Trekker.query.filter(
        Trekker.email == email,
        Trekker.id != trekker.id
    ).first()

    if existing:
        flash("Email already exists.", "danger")
        return redirect(url_for('main.trekker_profile'))

    trekker.name = request.form.get('name')
    trekker.email = email
    trekker.phone = request.form.get('phone')
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    if current_password or new_password or confirm_password:

        if not current_password or not new_password or not confirm_password:
            flash("Please fill all password fields.", "warning")
            return redirect(url_for('main.trekker_profile'))

        if not check_password_hash(trekker.passhash, current_password):
            flash("Current password is incorrect.", "danger")
            return redirect(url_for('main.trekker_profile'))

        if new_password != confirm_password:
            flash("New passwords do not match.", "danger")
            return redirect(url_for('main.trekker_profile'))

        if len(new_password) < 6:
            flash("Password must be at least 6 characters long.", "warning")
            return redirect(url_for('main.trekker_profile'))

        trekker.passhash = generate_password_hash(new_password)

    db.session.commit()

    flash("Profile updated successfully!", "success")
    return redirect(url_for('main.trekker_profile'))

@main_bp.route('/trekker/search')
def trekker_search():

    if 'trekker_id' not in session:
        return redirect(url_for('main.trekker_login'))

    q = request.args.get('q', '')

    treks = Trek.query.filter(
        or_(
            Trek.trek_name.ilike(f'%{q}%'),
            Trek.location.ilike(f'%{q}%'),
            Trek.difficulty.ilike(f'%{q}%')
        )
    ).all()

    return render_template(
        'trekker/trekker_search.html',
        query=q,
        treks=treks
    )


@main_bp.route('/treks')
def treks():

    today = date.today()

    treks = Trek.query.filter(
        Trek.status == "Open",
        Trek.end_date >= today
    ).all()

    return render_template(
        "treks.html",
        treks=treks
    )


#  logout

@main_bp.route('/logout')
def logout():
    role = session.get('role')
    session.clear()

    if role == 'admin':
        return redirect(url_for('main.admin_login'))
    elif role == 'trekker':
        return redirect(url_for('main.trekker_login'))
    elif role == 'staff':
        return redirect(url_for('main.staff_login'))
    return redirect(url_for('main.index'))
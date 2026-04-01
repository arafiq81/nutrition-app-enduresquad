"""
Web routes for Ironman Nutrition Bot
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, TrainingSession, DailyNutrition
from app.calculations import NutritionCalculator
from datetime import date, datetime
from collections import defaultdict

bp = Blueprint('main', __name__)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').lower().strip()
        password = request.form.get('password', '')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            if not user.approved:
                flash('Your account is pending approval. Please wait for admin approval.', 'info')
                return render_template('login.html')
            
            login_user(user, remember=True)
            
            if not user.profile_complete:
                flash('Please complete your athlete profile', 'info')
                return redirect(url_for('main.setup_profile'))
            
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').lower().strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not name or not email or not password:
            flash('All fields are required', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('register.html')
        
        if len(password) < 8:
            flash('Password must be at least 8 characters', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('register.html')
        
        user = User(name=name, email=email, profile_complete=False, approved=False)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash(f'Account created! Please wait for admin approval before you can access the system.', 'info')
        return redirect(url_for('main.login'))
    
    return render_template('register.html')


@bp.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('main.login'))


@bp.route('/setup-profile', methods=['GET', 'POST'])
@login_required
def setup_profile():
    """Complete athlete profile after registration"""
    user = current_user
    
    if request.method == 'POST':
        user.age = int(request.form.get('age'))
        user.sex = request.form.get('sex').lower()
        user.weight_kg = float(request.form.get('weight'))
        user.height_cm = float(request.form.get('height'))
        
        body_fat = request.form.get('body_fat')
        user.body_fat_percentage = float(body_fat) if body_fat else None
        
        user.activity_level = request.form.get('activity_level', 'moderate')
        user.training_phase = request.form.get('training_phase', 'base')
        
        hr_max = request.form.get('hr_max')
        user.hr_max = int(hr_max) if hr_max else None
        
        hr_z1 = request.form.get('hr_zone1')
        user.hr_zone1_max = int(hr_z1) if hr_z1 else None
        
        hr_z2 = request.form.get('hr_zone2')
        user.hr_zone2_max = int(hr_z2) if hr_z2 else None
        
        hr_z3 = request.form.get('hr_zone3')
        user.hr_zone3_max = int(hr_z3) if hr_z3 else None
        
        hr_z4 = request.form.get('hr_zone4')
        user.hr_zone4_max = int(hr_z4) if hr_z4 else None
        
        user.profile_complete = True
        
        db.session.commit()
        
        flash('Profile completed! Ready to start tracking.', 'success')
        return redirect(url_for('main.index'))
    
    return render_template('setup_profile.html', user=user)


@bp.route('/')
@login_required
def index():
    """Home page / Dashboard"""
    user = current_user
    today = date.today()
    
    sessions = TrainingSession.query.filter_by(user_id=user.id, date=today).all()
    daily_nutrition = DailyNutrition.query.filter_by(user_id=user.id, date=today).first()
    
    return render_template('dashboard.html', user=user, today=today, sessions=sessions, daily_nutrition=daily_nutrition)


@bp.route('/profile')
@login_required
def profile():
    """View athlete profile"""
    user = current_user
    return render_template('profile.html', user=user)


@bp.route('/training/log', methods=['GET', 'POST'])
@login_required
def log_training():
    """Log a single training session"""
    user = current_user
    
    if request.method == 'POST':
        session_date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        sport = request.form['sport']
        session_type = request.form['session_type']
        duration = int(request.form['duration'])
        
        z1 = float(request.form.get('zone1', 0))
        z2 = float(request.form.get('zone2', 0))
        z3 = float(request.form.get('zone3', 0))
        z4 = float(request.form.get('zone4', 0))
        z5 = float(request.form.get('zone5', 0))
        
        power = request.form.get('power')
        power = int(power) if power else None
        
        session = TrainingSession(
            user_id=user.id, date=session_date, sport=sport, session_type=session_type,
            duration_minutes=duration, zone1_percent=z1, zone2_percent=z2, zone3_percent=z3,
            zone4_percent=z4, zone5_percent=z5, average_power_watts=power,
            description=request.form.get('description', '')
        )
        
        calc = NutritionCalculator(user)
        zone_dist = {1: z1, 2: z2, 3: z3, 4: z4, 5: z5}
        energy, load = calc.calculate_training_energy(sport=sport, duration_minutes=duration, zone_distribution=zone_dist, average_power_watts=power)
        
        session.energy_expenditure_kcal = energy
        session.training_load_score = load
        
        db.session.add(session)
        db.session.commit()
        
        flash(f'Training session logged: {sport} - {duration} min', 'success')
        return redirect(url_for('main.calculate_nutrition', date=session_date.strftime('%Y-%m-%d')))
    
    return render_template('log_training.html', user=user, today=date.today())


@bp.route('/training/log-multi', methods=['GET', 'POST'])
@login_required
def log_training_multi():
    """Log multiple training sessions for the same day"""
    user = current_user
    
    if request.method == 'POST':
        session_date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        calc = NutritionCalculator(user)
        sessions_logged = 0
        
        session_num = 1
        while f'sport_{session_num}' in request.form:
            sport = request.form[f'sport_{session_num}']
            session_type = request.form[f'session_type_{session_num}']
            duration = int(request.form[f'duration_{session_num}'])
            
            z1 = float(request.form.get(f'zone1_{session_num}', 0))
            z2 = float(request.form.get(f'zone2_{session_num}', 0))
            z3 = float(request.form.get(f'zone3_{session_num}', 0))
            z4 = float(request.form.get(f'zone4_{session_num}', 0))
            z5 = float(request.form.get(f'zone5_{session_num}', 0))
            
            power = request.form.get(f'power_{session_num}')
            power = int(power) if power else None
            
            session = TrainingSession(
                user_id=user.id, date=session_date, sport=sport, session_type=session_type,
                duration_minutes=duration, zone1_percent=z1, zone2_percent=z2, zone3_percent=z3,
                zone4_percent=z4, zone5_percent=z5, average_power_watts=power,
                description=request.form.get(f'description_{session_num}', '')
            )
            
            zone_dist = {1: z1, 2: z2, 3: z3, 4: z4, 5: z5}
            energy, load = calc.calculate_training_energy(sport=sport, duration_minutes=duration, zone_distribution=zone_dist, average_power_watts=power)
            
            session.energy_expenditure_kcal = energy
            session.training_load_score = load
            
            db.session.add(session)
            sessions_logged += 1
            session_num += 1
        
        db.session.commit()
        
        flash(f'{sessions_logged} training session(s) logged successfully!', 'success')
        return redirect(url_for('main.calculate_nutrition', date=session_date.strftime('%Y-%m-%d')))
    
    return render_template('log_training_multi.html', user=user, today=date.today())


@bp.route('/nutrition/calculate')
@login_required
def calculate_nutrition():
    """Calculate nutrition for a specific date"""
    user = current_user
    
    date_str = request.args.get('date', date.today().strftime('%Y-%m-%d'))
    calc_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    
    sessions = TrainingSession.query.filter_by(user_id=user.id, date=calc_date).all()
    
    calc = NutritionCalculator(user)
    
    rmr = calc.calculate_rmr()
    neat = calc.calculate_neat(rmr)
    baseline = rmr + neat
    
    total_training_energy = sum(s.energy_expenditure_kcal or 0 for s in sessions)
    total_training_load = sum(s.training_load_score or 0 for s in sessions)
    
    tdee_before_tef = baseline + total_training_energy
    tef = calc.calculate_tef(tdee_before_tef)
    total_tdee = baseline + total_training_energy + tef
    
    macros = calc.calculate_daily_macros(total_training_load, total_tdee)
    
    training_data = []
    for s in sessions:
        zone_dist = {1: s.zone1_percent, 2: s.zone2_percent, 3: s.zone3_percent, 4: s.zone4_percent, 5: s.zone5_percent}
        training_data.append({'sport': s.sport, 'duration_minutes': s.duration_minutes, 'zone_distribution': zone_dist})
    
    hydration = calc.calculate_hydration_needs(training_data)
    
    daily = DailyNutrition.query.filter_by(user_id=user.id, date=calc_date).first()
    
    if not daily:
        daily = DailyNutrition(user_id=user.id, date=calc_date, recalculated_count=0)
        db.session.add(daily)
    
    daily.rmr_kcal = rmr
    daily.neat_kcal = neat
    daily.training_kcal = total_training_energy
    daily.tef_kcal = tef
    daily.total_tdee_kcal = total_tdee
    daily.target_carbs_g = macros['carbs_g']
    daily.target_protein_g = macros['protein_g']
    daily.target_fat_g = macros['fat_g']
    daily.target_fluids_ml = hydration['total_ml']
    daily.daily_training_load_score = total_training_load
    
    if daily.recalculated_count is None:
        daily.recalculated_count = 1
    else:
        daily.recalculated_count += 1
    
    db.session.commit()
    
    return render_template('nutrition_results.html', user=user, calc_date=calc_date, sessions=sessions, rmr=rmr, neat=neat, total_tdee=total_tdee, macros=macros, hydration=hydration, training_load=total_training_load)


@bp.route('/history/training')
@login_required
def training_history():
    """View all training sessions"""
    user = current_user
    
    sessions = TrainingSession.query.filter_by(user_id=user.id).order_by(TrainingSession.date.desc()).all()
    
    sessions_by_date = defaultdict(list)
    for session in sessions:
        sessions_by_date[session.date].append(session)
    
    return render_template('training_history.html', sessions_by_date=dict(sessions_by_date), user=user)


@bp.route('/history/nutrition')
@login_required
def nutrition_history():
    """View daily nutrition summary"""
    user = current_user
    
    daily_records = DailyNutrition.query.filter_by(user_id=user.id).order_by(DailyNutrition.date.desc()).all()
    
    return render_template('nutrition_history.html', daily_records=daily_records, user=user)


@bp.route('/admin/pending-users')
@login_required
def admin_pending_users():
    """View and approve pending users (admin only)"""
    user = current_user
    
    if not user.is_admin:
        flash('Access denied. Admin only.', 'error')
        return redirect(url_for('main.index'))

    pending = User.query.filter_by(approved=False).all()
    approved = User.query.filter_by(approved=True).order_by(User.created_at.desc()).all()
    
    return render_template('admin_users.html', pending=pending, approved=approved, user=user)


@bp.route('/admin/approve-user/<int:user_id>')
@login_required
def admin_approve_user(user_id):
    """Approve a pending user"""
    admin = current_user
    
    if not admin.is_admin:
        flash('Access denied', 'error')
        return redirect(url_for('main.index'))

    user = User.query.get(user_id)
    if user:
        user.approved = True
        user.approved_at = datetime.utcnow()
        user.approved_by = admin.id
        db.session.commit()
        flash(f'User {user.name} ({user.email}) approved!', 'success')
    
    return redirect(url_for('main.admin_pending_users'))


@bp.route('/admin/reject-user/<int:user_id>')
@login_required
def admin_reject_user(user_id):
    """Reject and delete a pending user"""
    admin = current_user
    
    if not admin.is_admin:
        flash('Access denied', 'error')
        return redirect(url_for('main.index'))

    user = User.query.get(user_id)
    if user and user.id != admin.id:
        name = user.name
        email = user.email
        db.session.delete(user)
        db.session.commit()
        flash(f'User {name} ({email}) rejected and deleted.', 'info')
    
    return redirect(url_for('main.admin_pending_users'))




@bp.route('/chat', methods=['GET', 'POST'])
@login_required
def chat():
    """AI Chat Interface"""
    from app.chat import NutritionChatBot
    from app.models import ChatMessage
    
    user = current_user
    today = date.today()
    
    # Get today's data for context
    sessions = TrainingSession.query.filter_by(user_id=user.id, date=today).all()
    daily_nutrition = DailyNutrition.query.filter_by(user_id=user.id, date=today).first()
    
    # Initialize bot
    bot = NutritionChatBot(user, daily_nutrition, sessions)
    
    # Check rate limit
    can_send, messages_remaining = bot.check_rate_limit()
    
    # Handle POST (send message)
    if request.method == 'POST':
        user_message = request.form.get('message', '').strip()
        
        if user_message:
            success, bot_response, error_msg = bot.send_message(user_message)
            
            if not success:
                flash(error_msg, 'error')
            else:
                # Recalculate remaining messages
                can_send, messages_remaining = bot.check_rate_limit()
        
        return redirect(url_for('main.chat'))
    
    # Get recent chat history
    recent_messages = bot.get_recent_messages(limit=10)
    recent_messages.reverse()  # Oldest first for display
    
    return render_template('chat.html', 
                          user=user, 
                          recent_messages=recent_messages,
                          can_send=can_send,
                          messages_remaining=messages_remaining)


@bp.route('/health')
def health():
    """Health check endpoint"""
    return {'status': 'healthy', 'message': 'App is running'}

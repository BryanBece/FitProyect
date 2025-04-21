from flask import render_template, request, redirect, url_for, flash, session, jsonify
from app import app, db
from models import User, Exercise, Routine, RoutineExercise, CompletedWorkout, FavoriteRoutine, UserProgress
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

# Rutas principales
@app.route('/')
def index():
    user_level = session.get('user_level', 'principiante')
    days_of_week = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    today = datetime.datetime.now().weekday()
    
    # Obtener rutinas recomendadas según el nivel del usuario
    routines = Routine.query.filter_by(level=user_level).order_by(Routine.day_of_week).all()
    
    # Obtener rutina del día (si existe)
    today_routine = Routine.query.filter_by(level=user_level, day_of_week=today).first()
    
    return render_template('index.html', 
                          routines=routines, 
                          today_routine=today_routine,
                          days_of_week=days_of_week,
                          user_level=user_level)

@app.route('/set_level', methods=['POST'])
def set_level():
    level = request.form.get('level')
    if level in ['principiante', 'amateur', 'medio', 'avanzado']:
        session['user_level'] = level
        if 'user_id' in session:
            user = User.query.get(session['user_id'])
            if user:
                user.level = level
                db.session.commit()
    return redirect(url_for('index'))

@app.route('/exercises')
def exercises():
    level = request.args.get('level', session.get('user_level', 'principiante'))
    muscle_group = request.args.get('muscle_group', None)
    
    query = Exercise.query.filter_by(level=level)
    
    if muscle_group:
        query = query.filter_by(muscle_group=muscle_group)
    
    exercises = query.all()
    
    # Obtener grupos musculares únicos para filtros
    muscle_groups = db.session.query(Exercise.muscle_group).distinct().all()
    muscle_groups = [group[0] for group in muscle_groups]
    
    return render_template('exercises.html', 
                          exercises=exercises, 
                          level=level,
                          muscle_groups=muscle_groups,
                          selected_muscle_group=muscle_group)

@app.route('/weekly_plan')
def weekly_plan():
    level = request.args.get('level', session.get('user_level', 'principiante'))
    days_of_week = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    
    routines_by_day = {}
    for day in range(7):
        routines_by_day[day] = Routine.query.filter_by(level=level, day_of_week=day).all()
    
    # Obtener el día actual de la semana (0-6, donde 0 es lunes)
    current_weekday = datetime.datetime.now().weekday()
    
    return render_template('weekly_plan.html', 
                          routines_by_day=routines_by_day, 
                          days_of_week=days_of_week,
                          level=level,
                          current_weekday=current_weekday)

@app.route('/routine/<int:routine_id>')
def routine_detail(routine_id):
    routine = Routine.query.get_or_404(routine_id)
    
    routine_exercises = (RoutineExercise.query
                        .filter_by(routine_id=routine_id)
                        .order_by(RoutineExercise.order)
                        .all())
    
    exercises = []
    for re in routine_exercises:
        exercise = Exercise.query.get(re.exercise_id)
        exercises.append({
            'exercise': exercise,
            'sets': re.sets,
            'reps': re.reps,
            'order': re.order
        })
    
    # Verificar si la rutina está en favoritos del usuario
    is_favorite = False
    if 'user_id' in session:
        favorite = FavoriteRoutine.query.filter_by(
            user_id=session['user_id'], 
            routine_id=routine_id
        ).first()
        is_favorite = favorite is not None
    
    return render_template('daily_routine.html', 
                          routine=routine, 
                          exercises=exercises,
                          is_favorite=is_favorite)

@app.route('/mark_completed/<int:routine_id>', methods=['POST'])
def mark_completed(routine_id):
    if 'user_id' not in session:
        flash('Debes iniciar sesión para registrar tu progreso', 'warning')
        return redirect(url_for('routine_detail', routine_id=routine_id))
    
    user_id = session['user_id']
    completed = CompletedWorkout(user_id=user_id, routine_id=routine_id)
    db.session.add(completed)
    db.session.commit()
    
    # Obtener información de la rutina para el correo
    routine = Routine.query.get(routine_id)
    user = User.query.get(user_id)
    
    # Intentar enviar correo de felicitación
    try:
        from sendgrid import send_workout_completed_email
        email_sent = send_workout_completed_email(
            user.email, 
            user.username, 
            routine.name, 
            routine.calories_estimate
        )
        if email_sent:
            flash('¡Entrenamiento completado! Te hemos enviado un resumen por correo.', 'success')
        else:
            flash('¡Entrenamiento completado! Sigue así.', 'success')
    except Exception as e:
        # En caso de error con el envío, mostrar mensaje estándar
        flash('¡Entrenamiento completado! Sigue así.', 'success')
        print(f"Error al enviar el correo de entrenamiento completado: {e}")
        
    return redirect(url_for('profile'))

@app.route('/toggle_favorite/<int:routine_id>', methods=['POST'])
def toggle_favorite(routine_id):
    if 'user_id' not in session:
        flash('Debes iniciar sesión para añadir favoritos', 'warning')
        return redirect(url_for('routine_detail', routine_id=routine_id))
    
    user_id = session['user_id']
    favorite = FavoriteRoutine.query.filter_by(
        user_id=user_id, 
        routine_id=routine_id
    ).first()
    
    if favorite:
        db.session.delete(favorite)
        message = '¡Rutina eliminada de favoritos!'
    else:
        new_favorite = FavoriteRoutine(user_id=user_id, routine_id=routine_id)
        db.session.add(new_favorite)
        message = '¡Rutina añadida a favoritos!'
    
    db.session.commit()
    flash(message, 'success')
    return redirect(url_for('routine_detail', routine_id=routine_id))

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para ver tu perfil', 'warning')
        return redirect(url_for('index'))
    
    user = User.query.get(session['user_id'])
    
    # Obtener últimos entrenamientos completados
    completed_workouts = (CompletedWorkout.query
                         .filter_by(user_id=user.id)
                         .order_by(CompletedWorkout.completed_at.desc())
                         .limit(10)
                         .all())
    
    # Obtener rutinas favoritas
    favorites = (FavoriteRoutine.query
                .filter_by(user_id=user.id)
                .order_by(FavoriteRoutine.added_at.desc())
                .all())
    
    # Obtener el último registro de progreso
    latest_progress = (UserProgress.query
                      .filter_by(user_id=user.id)
                      .order_by(UserProgress.date.desc())
                      .first())
    
    # Obtener el día actual de la semana (0-6, donde 0 es lunes)
    current_weekday = datetime.datetime.now().weekday()
    current_date = datetime.datetime.now().date()
    
    # Función auxiliar para obtener la rutina por día y nivel
    def get_routine_by_day_and_level(day_num, level):
        routine = Routine.query.filter_by(day_of_week=day_num, level=level).first()
        return routine
    
    return render_template('profile.html', 
                          user=user, 
                          completed_workouts=completed_workouts,
                          favorites=favorites,
                          current_weekday=current_weekday,
                          current_date=current_date,
                          latest_progress=latest_progress,
                          get_routine_by_day_and_level=get_routine_by_day_and_level)

@app.route('/reports')
def reports():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para ver tus reportes', 'warning')
        return redirect(url_for('index'))
    
    user = User.query.get(session['user_id'])
    
    # Obtener datos para reportes
    # 1. Entrenamientos completados por mes (últimos 6 meses)
    six_months_ago = datetime.datetime.now() - datetime.timedelta(days=180)
    workouts_by_month = (db.session.query(
        db.func.strftime('%Y-%m', CompletedWorkout.completed_at).label('month'),
        db.func.count().label('count'))
        .filter(CompletedWorkout.user_id == user.id, 
                CompletedWorkout.completed_at >= six_months_ago)
        .group_by('month')
        .order_by('month')
        .all())
    
    # 2. Progreso de peso si está disponible
    weight_progress = (UserProgress.query
                       .filter_by(user_id=user.id)
                       .order_by(UserProgress.date)
                       .all())
    
    # 3. Calorías quemadas por semana (últimas 4 semanas)
    four_weeks_ago = datetime.datetime.now() - datetime.timedelta(days=28)
    calories_by_week = (db.session.query(
        db.func.strftime('%W', CompletedWorkout.completed_at).label('week'),
        db.func.sum(Routine.calories_estimate).label('calories'))
        .join(Routine, CompletedWorkout.routine_id == Routine.id)
        .filter(CompletedWorkout.user_id == user.id,
                CompletedWorkout.completed_at >= four_weeks_ago)
        .group_by('week')
        .order_by('week')
        .all())
    
    # 4. Distribución de entrenamiento por grupo muscular
    muscle_distribution = (db.session.query(
        Exercise.muscle_group, 
        db.func.count().label('count'))
        .join(RoutineExercise, Exercise.id == RoutineExercise.exercise_id)
        .join(Routine, RoutineExercise.routine_id == Routine.id)
        .join(CompletedWorkout, Routine.id == CompletedWorkout.routine_id)
        .filter(CompletedWorkout.user_id == user.id)
        .group_by(Exercise.muscle_group)
        .order_by(db.desc('count'))
        .all())
    
    # 5. Tiempo total de entrenamiento (en minutos) por mes
    training_time_by_month = (db.session.query(
        db.func.strftime('%Y-%m', CompletedWorkout.completed_at).label('month'),
        db.func.sum(Routine.duration_minutes).label('total_minutes'))
        .join(Routine, CompletedWorkout.routine_id == Routine.id)
        .filter(CompletedWorkout.user_id == user.id,
                CompletedWorkout.completed_at >= six_months_ago)
        .group_by('month')
        .order_by('month')
        .all())
    
    # Calcular datos para cards
    # Total de entrenamientos completados
    completed_workouts_count = CompletedWorkout.query.filter_by(user_id=user.id).count()
    
    # Total de calorías quemadas en los últimos 30 días
    last_month = datetime.datetime.now() - datetime.timedelta(days=30)
    total_calories_query = (db.session.query(
        db.func.sum(Routine.calories_estimate))
        .join(CompletedWorkout, Routine.id == CompletedWorkout.routine_id)
        .filter(CompletedWorkout.user_id == user.id,
                CompletedWorkout.completed_at >= last_month)
        .first())
    total_calories = total_calories_query[0] if total_calories_query[0] else 0
    
    # Total de minutos de entrenamiento en los últimos 30 días
    total_minutes_query = (db.session.query(
        db.func.sum(Routine.duration_minutes))
        .join(CompletedWorkout, Routine.id == CompletedWorkout.routine_id)
        .filter(CompletedWorkout.user_id == user.id,
                CompletedWorkout.completed_at >= last_month)
        .first())
    total_minutes = total_minutes_query[0] if total_minutes_query[0] else 0
    
    return render_template('reports.html',
                          user=user,
                          workouts_by_month=workouts_by_month,
                          weight_progress=weight_progress,
                          calories_by_week=calories_by_week,
                          muscle_distribution=muscle_distribution,
                          training_time_by_month=training_time_by_month,
                          completed_workouts_count=completed_workouts_count,
                          total_calories=total_calories,
                          total_minutes=total_minutes)

@app.route('/add_progress', methods=['GET', 'POST'])
def add_progress():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para registrar tu progreso', 'warning')
        return redirect(url_for('index'))
    
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        date = datetime.datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
        weight = request.form.get('weight')
        weight = float(weight) if weight else None
        note = request.form.get('note')
        
        # Calcular calorías y minutos de entrenamiento del último mes
        one_month_ago = datetime.datetime.now() - datetime.timedelta(days=30)
        
        # Calorías quemadas
        calories_query = (db.session.query(
            db.func.sum(Routine.calories_estimate).label('total_calories'))
            .join(CompletedWorkout, Routine.id == CompletedWorkout.routine_id)
            .filter(CompletedWorkout.user_id == user.id,
                    CompletedWorkout.completed_at >= one_month_ago)
            .first())
        
        calories_burned = calories_query.total_calories if calories_query and calories_query.total_calories else 0
        
        # Minutos de entrenamiento
        time_query = (db.session.query(
            db.func.sum(Routine.duration_minutes).label('total_minutes'))
            .join(CompletedWorkout, Routine.id == CompletedWorkout.routine_id)
            .filter(CompletedWorkout.user_id == user.id,
                    CompletedWorkout.completed_at >= one_month_ago)
            .first())
        
        workout_minutes = time_query.total_minutes if time_query and time_query.total_minutes else 0
        
        # Crear nuevo registro de progreso
        progress = UserProgress(
            user_id=user.id,
            date=date,
            weight=weight,
            calories_burned=calories_burned,
            workout_minutes=workout_minutes,
            note=note
        )
        
        db.session.add(progress)
        db.session.commit()
        
        flash('¡Progreso registrado correctamente!', 'success')
        return redirect(url_for('reports'))
    
    today_date = datetime.datetime.now().strftime('%Y-%m-%d')
    return render_template('add_progress.html', user=user, today_date=today_date)

# Rutas de Autenticación
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        level = request.form.get('level', 'principiante')
        
        # Validaciones
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('El nombre de usuario o correo electrónico ya está en uso', 'danger')
            return redirect(url_for('register'))
        
        if password != confirm_password:
            flash('Las contraseñas no coinciden', 'danger')
            return redirect(url_for('register'))
        
        # Crear nuevo usuario
        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            level=level
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        # Iniciar sesión automáticamente
        session['user_id'] = new_user.id
        session['username'] = new_user.username
        session['user_level'] = new_user.level
        
        # Intentar enviar correo de bienvenida
        try:
            from sendgrid import send_welcome_email
            email_sent = send_welcome_email(new_user.email, new_user.username)
            if email_sent:
                flash('¡Registro exitoso! Te hemos enviado un correo de bienvenida', 'success')
            else:
                flash('¡Registro exitoso! Bienvenido a FitPesas', 'success')
        except Exception as e:
            # En caso de error con el envío del correo, mostrar mensaje estándar
            flash('¡Registro exitoso! Bienvenido a FitPesas', 'success')
            print(f"Error al enviar el correo de bienvenida: {e}")
            
        return redirect(url_for('profile'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['user_level'] = user.level
            
            flash('¡Has iniciado sesión correctamente!', 'success')
            return redirect(url_for('profile'))
        else:
            flash('Nombre de usuario o contraseña incorrectos', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    # No quitamos user_level para mantener las preferencias del usuario no logueado
    
    flash('Has cerrado sesión correctamente', 'success')
    return redirect(url_for('index'))

# API para el temporizador
@app.route('/api/exercise/<int:exercise_id>')
def get_exercise(exercise_id):
    exercise = Exercise.query.get_or_404(exercise_id)
    return jsonify({
        'id': exercise.id,
        'name': exercise.name,
        'default_duration': exercise.default_duration,
        'rest_time': exercise.rest_time
    })

# Función para actualizar estimaciones de calorías quemadas y duración
@app.route('/update_calories')
def update_calories():
    # Esta ruta es solo para uso administrativo inicial
    # Actualiza las rutinas existentes con estimaciones de calorías y duración
    
    # Diccionario de estimaciones por nivel y tipo
    routine_data = {
        'principiante': {
            'full_body': {'calories': 250, 'duration': 30},
            'tren_superior': {'calories': 180, 'duration': 25},
            'tren_inferior': {'calories': 220, 'duration': 25}
        },
        'amateur': {
            'empuje': {'calories': 320, 'duration': 35},
            'tiron': {'calories': 300, 'duration': 35},
            'piernas': {'calories': 380, 'duration': 40}
        },
        'medio': {
            'pecho_triceps': {'calories': 420, 'duration': 45},
            'espalda_biceps': {'calories': 400, 'duration': 45},
            'hombros_abdominales': {'calories': 350, 'duration': 40},
            'piernas': {'calories': 480, 'duration': 50}
        },
        'avanzado': {
            'pecho_espalda': {'calories': 520, 'duration': 60},
            'piernas': {'calories': 600, 'duration': 65},
            'hombros_brazos': {'calories': 450, 'duration': 55},
            'full_body': {'calories': 650, 'duration': 70}
        }
    }
    
    # Actualizar rutinas de nivel principiante
    r1 = Routine.query.filter_by(name="Entrenamiento Full Body - Principiante").first()
    if r1: 
        r1.calories_estimate = routine_data['principiante']['full_body']['calories']
        r1.duration_minutes = routine_data['principiante']['full_body']['duration']
    
    r2 = Routine.query.filter_by(name="Entrenamiento de Tren Superior - Principiante").first()
    if r2: 
        r2.calories_estimate = routine_data['principiante']['tren_superior']['calories']
        r2.duration_minutes = routine_data['principiante']['tren_superior']['duration']
    
    r3 = Routine.query.filter_by(name="Entrenamiento de Tren Inferior - Principiante").first()
    if r3: 
        r3.calories_estimate = routine_data['principiante']['tren_inferior']['calories']
        r3.duration_minutes = routine_data['principiante']['tren_inferior']['duration']
    
    # Actualizar rutinas de nivel amateur
    r4 = Routine.query.filter_by(name="Entrenamiento de Empuje - Amateur").first()
    if r4: 
        r4.calories_estimate = routine_data['amateur']['empuje']['calories']
        r4.duration_minutes = routine_data['amateur']['empuje']['duration']
    
    r5 = Routine.query.filter_by(name="Entrenamiento de Tirón - Amateur").first()
    if r5: 
        r5.calories_estimate = routine_data['amateur']['tiron']['calories']
        r5.duration_minutes = routine_data['amateur']['tiron']['duration']
    
    r6 = Routine.query.filter_by(name="Entrenamiento de Piernas - Amateur").first()
    if r6: 
        r6.calories_estimate = routine_data['amateur']['piernas']['calories']
        r6.duration_minutes = routine_data['amateur']['piernas']['duration']
    
    # Actualizar rutinas de nivel medio
    r7 = Routine.query.filter_by(name="Pecho y Tríceps - Nivel Medio").first()
    if r7: 
        r7.calories_estimate = routine_data['medio']['pecho_triceps']['calories']
        r7.duration_minutes = routine_data['medio']['pecho_triceps']['duration']
    
    r8 = Routine.query.filter_by(name="Espalda y Bíceps - Nivel Medio").first()
    if r8: 
        r8.calories_estimate = routine_data['medio']['espalda_biceps']['calories']
        r8.duration_minutes = routine_data['medio']['espalda_biceps']['duration']
    
    r9 = Routine.query.filter_by(name="Hombros y Abdominales - Nivel Medio").first()
    if r9: 
        r9.calories_estimate = routine_data['medio']['hombros_abdominales']['calories']
        r9.duration_minutes = routine_data['medio']['hombros_abdominales']['duration']
    
    r10 = Routine.query.filter_by(name="Piernas - Nivel Medio").first()
    if r10: 
        r10.calories_estimate = routine_data['medio']['piernas']['calories']
        r10.duration_minutes = routine_data['medio']['piernas']['duration']
    
    # Actualizar rutinas de nivel avanzado
    r11 = Routine.query.filter_by(name="Pecho y Espalda - Avanzado").first()
    if r11: 
        r11.calories_estimate = routine_data['avanzado']['pecho_espalda']['calories']
        r11.duration_minutes = routine_data['avanzado']['pecho_espalda']['duration']
    
    r12 = Routine.query.filter_by(name="Piernas Intenso - Avanzado").first()
    if r12: 
        r12.calories_estimate = routine_data['avanzado']['piernas']['calories']
        r12.duration_minutes = routine_data['avanzado']['piernas']['duration']
    
    r13 = Routine.query.filter_by(name="Hombros y Brazos - Avanzado").first()
    if r13: 
        r13.calories_estimate = routine_data['avanzado']['hombros_brazos']['calories']
        r13.duration_minutes = routine_data['avanzado']['hombros_brazos']['duration']
    
    r14 = Routine.query.filter_by(name="Full Body Intenso - Avanzado").first()
    if r14: 
        r14.calories_estimate = routine_data['avanzado']['full_body']['calories']
        r14.duration_minutes = routine_data['avanzado']['full_body']['duration']
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Calorías y duración actualizadas correctamente'})

from app import db
from datetime import datetime
from flask_login import UserMixin

# Define models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    level = db.Column(db.String(20), default="principiante")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    completed_workouts = db.relationship('CompletedWorkout', backref='user', lazy=True)
    favorites = db.relationship('FavoriteRoutine', backref='user', lazy=True)
    progress = db.relationship('UserProgress', backref='user_profile', lazy=True)

class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    muscle_group = db.Column(db.String(50), nullable=False)
    level = db.Column(db.String(20), nullable=False)  # principiante, amateur, medio, avanzado
    equipment = db.Column(db.String(100), nullable=False)  # tipo de pesas
    weight_recommendation = db.Column(db.String(200))
    default_duration = db.Column(db.Integer, default=45)  # segundos
    rest_time = db.Column(db.Integer, default=30)  # segundos de descanso
    
    # Relationships
    routines = db.relationship('RoutineExercise', backref='exercise', lazy=True)

class Routine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    level = db.Column(db.String(20), nullable=False)  # principiante, amateur, medio, avanzado
    day_of_week = db.Column(db.Integer, nullable=False)  # 0-6 (lunes-domingo)
    description = db.Column(db.Text)
    calories_estimate = db.Column(db.Integer, default=0)  # Estimación de calorías quemadas
    duration_minutes = db.Column(db.Integer, default=0)  # Duración estimada en minutos
    
    # Relationships
    exercises = db.relationship('RoutineExercise', backref='routine', lazy=True)
    favorites = db.relationship('FavoriteRoutine', backref='routine', lazy=True)

class RoutineExercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    routine_id = db.Column(db.Integer, db.ForeignKey('routine.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.id'), nullable=False)
    sets = db.Column(db.Integer, default=3)
    reps = db.Column(db.Integer, default=12)
    order = db.Column(db.Integer, nullable=False)

class CompletedWorkout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    routine_id = db.Column(db.Integer, db.ForeignKey('routine.id'), nullable=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    routine = db.relationship('Routine')

class FavoriteRoutine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    routine_id = db.Column(db.Integer, db.ForeignKey('routine.id'), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
class UserProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    weight = db.Column(db.Float)  # Peso en kg
    calories_burned = db.Column(db.Integer)  # Calorías quemadas estimadas
    workout_minutes = db.Column(db.Integer)  # Minutos de entrenamiento
    note = db.Column(db.Text)  # Nota opcional del usuario
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación con usuario (overlaps evita advertencias de relaciones superpuestas)
    user = db.relationship('User', overlaps="progress,user_profile")

def init_db():
    """Inicializa la base de datos con ejercicios y rutinas predeterminadas"""
    
    # Crear ejercicios
    exercises = [
        # Ejercicios de nivel principiante
        Exercise(
            name="Curl de Bíceps con Mancuernas",
            description="Párate derecho con una mancuerna en cada mano. Dobla los codos y levanta las mancuernas hacia los hombros, manteniendo los codos cerca del cuerpo.",
            muscle_group="Bíceps",
            level="principiante",
            equipment="Mancuernas",
            weight_recommendation="Mujeres: 2-4kg / Hombres: 4-8kg",
            default_duration=40,
            rest_time=20
        ),
        Exercise(
            name="Press de Hombros con Mancuernas",
            description="Siéntate en un banco con respaldo o de pie. Sostén una mancuerna en cada mano a la altura de los hombros. Empuja las mancuernas hacia arriba hasta que tus brazos estén completamente extendidos.",
            muscle_group="Hombros",
            level="principiante",
            equipment="Mancuernas",
            weight_recommendation="Mujeres: 2-5kg / Hombres: 5-10kg",
            default_duration=40,
            rest_time=20
        ),
        Exercise(
            name="Sentadillas con Mancuernas",
            description="Párate con los pies separados al ancho de los hombros, sosteniendo mancuernas a los lados. Flexiona las rodillas y baja las caderas como si fueras a sentarte, manteniendo el pecho erguido.",
            muscle_group="Piernas",
            level="principiante",
            equipment="Mancuernas",
            weight_recommendation="Mujeres: 4-8kg / Hombres: 8-12kg",
            default_duration=45,
            rest_time=30
        ),
        Exercise(
            name="Press de Pecho con Mancuernas",
            description="Acuéstate en un banco plano sosteniendo una mancuerna en cada mano a nivel del pecho. Empuja las mancuernas hacia arriba hasta que tus brazos estén extendidos, luego bájalas lentamente.",
            muscle_group="Pecho",
            level="principiante",
            equipment="Mancuernas, Banco",
            weight_recommendation="Mujeres: 3-6kg / Hombres: 8-12kg",
            default_duration=40,
            rest_time=30
        ),
        Exercise(
            name="Peso Muerto Rumano con Mancuernas",
            description="De pie, sosteniendo mancuernas frente a tus muslos. Con las rodillas ligeramente flexionadas, inclina el torso hacia adelante bajando las mancuernas a lo largo de tus piernas.",
            muscle_group="Espalda baja, Isquiotibiales",
            level="principiante",
            equipment="Mancuernas",
            weight_recommendation="Mujeres: 4-8kg / Hombres: 8-14kg",
            default_duration=45,
            rest_time=30
        ),
        
        # Ejercicios de nivel amateur
        Exercise(
            name="Remo con Mancuerna",
            description="Apoya la rodilla y mano izquierda en un banco. Con la mancuerna en la mano derecha, tira hacia arriba llevando el codo hacia atrás. Alterna los lados.",
            muscle_group="Espalda",
            level="amateur",
            equipment="Mancuernas, Banco",
            weight_recommendation="Mujeres: 6-10kg / Hombres: 12-16kg",
            default_duration=45,
            rest_time=30
        ),
        Exercise(
            name="Zancadas con Mancuernas",
            description="De pie sosteniendo mancuernas a los lados. Da un paso adelante con una pierna y baja la rodilla trasera hacia el suelo, luego regresa a la posición inicial. Alterna las piernas.",
            muscle_group="Piernas, Glúteos",
            level="amateur",
            equipment="Mancuernas",
            weight_recommendation="Mujeres: 6-10kg / Hombres: 10-16kg",
            default_duration=50,
            rest_time=30
        ),
        Exercise(
            name="Press de Banca Inclinado con Mancuernas",
            description="Acuéstate en un banco inclinado sosteniendo mancuernas a nivel del pecho. Empuja las mancuernas hacia arriba hasta extender los brazos, luego bájalas lentamente.",
            muscle_group="Pecho Superior",
            level="amateur",
            equipment="Mancuernas, Banco Inclinado",
            weight_recommendation="Mujeres: 5-8kg / Hombres: 10-18kg",
            default_duration=45,
            rest_time=40
        ),
        Exercise(
            name="Elevaciones Laterales",
            description="De pie con mancuernas a los lados. Levanta los brazos hacia los lados hasta que estén paralelos al suelo, manteniendo los codos ligeramente flexionados.",
            muscle_group="Hombros",
            level="amateur",
            equipment="Mancuernas",
            weight_recommendation="Mujeres: 2-5kg / Hombres: 5-8kg",
            default_duration=40,
            rest_time=30
        ),
        Exercise(
            name="Curl Martillo",
            description="De pie con mancuernas a los lados, palmas hacia adentro. Flexiona los codos levantando las mancuernas hacia los hombros, manteniendo las palmas hacia adentro.",
            muscle_group="Bíceps, Antebrazos",
            level="amateur",
            equipment="Mancuernas",
            weight_recommendation="Mujeres: 4-8kg / Hombres: 8-12kg",
            default_duration=40,
            rest_time=30
        ),
        
        # Ejercicios de nivel medio
        Exercise(
            name="Press Militar con Barra",
            description="De pie sosteniendo una barra a nivel de los hombros. Empuja la barra hacia arriba hasta extender los brazos, luego bájala controladamente.",
            muscle_group="Hombros",
            level="medio",
            equipment="Barra, Discos",
            weight_recommendation="Mujeres: 15-25kg / Hombres: 30-50kg",
            default_duration=45,
            rest_time=45
        ),
        Exercise(
            name="Peso Muerto",
            description="De pie frente a una barra en el suelo. Flexiona las rodillas y caderas para agarrar la barra. Levanta la barra manteniendo la espalda recta, extendiendo caderas y rodillas.",
            muscle_group="Espalda, Piernas",
            level="medio",
            equipment="Barra, Discos",
            weight_recommendation="Mujeres: 30-50kg / Hombres: 60-100kg",
            default_duration=50,
            rest_time=60
        ),
        Exercise(
            name="Hip Thrust con Barra",
            description="Siéntate en el suelo con la espalda contra un banco, barra sobre las caderas. Eleva las caderas hasta que el torso quede paralelo al suelo, luego baja controladamente.",
            muscle_group="Glúteos",
            level="medio",
            equipment="Barra, Discos, Banco",
            weight_recommendation="Mujeres: 20-40kg / Hombres: 40-70kg",
            default_duration=45,
            rest_time=45
        ),
        Exercise(
            name="Fondos en Paralelas",
            description="Soporta tu peso en barras paralelas. Baja tu cuerpo flexionando los codos hasta que formen un ángulo de 90 grados, luego empuja hacia arriba.",
            muscle_group="Tríceps, Pecho",
            level="medio",
            equipment="Barras Paralelas",
            weight_recommendation="Peso corporal o con peso adicional",
            default_duration=40,
            rest_time=45
        ),
        Exercise(
            name="Remo con Barra T",
            description="Inclínate sobre una barra T, agarrándola con ambas manos. Tira de la barra hacia el abdomen manteniendo la espalda recta, luego baja controladamente.",
            muscle_group="Espalda",
            level="medio",
            equipment="Barra T, Discos",
            weight_recommendation="Mujeres: 15-30kg / Hombres: 30-60kg",
            default_duration=45,
            rest_time=45
        ),
        
        # Ejercicios de nivel avanzado
        Exercise(
            name="Sentadilla con Barra",
            description="Coloca una barra sobre los trapecios, pies a la anchura de los hombros. Flexiona rodillas y caderas para bajar, manteniendo la espalda recta, luego sube.",
            muscle_group="Piernas, Glúteos",
            level="avanzado",
            equipment="Barra, Discos",
            weight_recommendation="Mujeres: 40-60kg / Hombres: 80-120kg",
            default_duration=50,
            rest_time=60
        ),
        Exercise(
            name="Press de Banca",
            description="Acuéstate en un banco plano sosteniendo una barra sobre el pecho. Baja la barra hasta tocar el pecho y luego empuja hacia arriba hasta extender los brazos.",
            muscle_group="Pecho, Tríceps",
            level="avanzado",
            equipment="Barra, Discos, Banco",
            weight_recommendation="Mujeres: 30-45kg / Hombres: 60-100kg",
            default_duration=45,
            rest_time=60
        ),
        Exercise(
            name="Dominadas Lastradas",
            description="Cuelga un peso adicional en un cinturón alrededor de tu cintura. Agarra una barra con las palmas hacia afuera y levanta tu cuerpo hasta que la barbilla supere la barra.",
            muscle_group="Espalda, Bíceps",
            level="avanzado",
            equipment="Barra de dominadas, Peso adicional",
            weight_recommendation="Mujeres: 5-15kg / Hombres: 10-25kg adicionales",
            default_duration=40,
            rest_time=60
        ),
        Exercise(
            name="Clean & Jerk (Arrancada y Envión)",
            description="Levanta una barra desde el suelo hasta por encima de la cabeza en un movimiento fluido, combinando potencia y técnica.",
            muscle_group="Cuerpo completo",
            level="avanzado",
            equipment="Barra olímpica, Discos",
            weight_recommendation="Mujeres: 30-50kg / Hombres: 60-100kg",
            default_duration=60,
            rest_time=90
        ),
        Exercise(
            name="Zancadas Búlgaras con Mancuernas",
            description="Coloca un pie en un banco detrás de ti, sosteniendo mancuernas. Baja la rodilla trasera hacia el suelo flexionando la pierna delantera, luego sube.",
            muscle_group="Piernas, Glúteos",
            level="avanzado",
            equipment="Mancuernas, Banco",
            weight_recommendation="Mujeres: 8-16kg / Hombres: 16-24kg",
            default_duration=50,
            rest_time=45
        )
    ]
    
    # Añadir ejercicios a la base de datos
    for exercise in exercises:
        db.session.add(exercise)
    
    # Crear rutinas
    routines = [
        # Rutinas para principiantes
        Routine(name="Entrenamiento Full Body - Principiante", level="principiante", day_of_week=0, 
                description="Rutina de cuerpo completo ideal para comenzar con el entrenamiento con pesas"),
        Routine(name="Entrenamiento de Tren Superior - Principiante", level="principiante", day_of_week=2, 
                description="Enfocado en fortalecer brazos, pecho y espalda"),
        Routine(name="Entrenamiento de Tren Inferior - Principiante", level="principiante", day_of_week=4, 
                description="Enfocado en piernas y glúteos para principiantes"),
        
        # Rutinas para amateur
        Routine(name="Entrenamiento de Empuje - Amateur", level="amateur", day_of_week=0, 
                description="Trabaja pecho, hombros y tríceps"),
        Routine(name="Entrenamiento de Tirón - Amateur", level="amateur", day_of_week=2, 
                description="Enfocado en espalda y bíceps"),
        Routine(name="Entrenamiento de Piernas - Amateur", level="amateur", day_of_week=4, 
                description="Rutina completa para piernas y glúteos"),
        
        # Rutinas para nivel medio
        Routine(name="Pecho y Tríceps - Nivel Medio", level="medio", day_of_week=0, 
                description="Entrenamiento intenso de pecho y tríceps"),
        Routine(name="Espalda y Bíceps - Nivel Medio", level="medio", day_of_week=1, 
                description="Entrenamiento completo para espalda y brazos"),
        Routine(name="Hombros y Abdominales - Nivel Medio", level="medio", day_of_week=2, 
                description="Desarrollo de hombros y core"),
        Routine(name="Piernas - Nivel Medio", level="medio", day_of_week=4, 
                description="Rutina intensiva para el desarrollo de piernas"),
        
        # Rutinas para nivel avanzado
        Routine(name="Pecho y Espalda - Avanzado", level="avanzado", day_of_week=0, 
                description="Entrenamiento de alta intensidad para pecho y espalda"),
        Routine(name="Piernas Intenso - Avanzado", level="avanzado", day_of_week=1, 
                description="Rutina avanzada para máximo desarrollo de piernas"),
        Routine(name="Hombros y Brazos - Avanzado", level="avanzado", day_of_week=3, 
                description="Entrenamiento de definición para hombros y brazos"),
        Routine(name="Full Body Intenso - Avanzado", level="avanzado", day_of_week=5, 
                description="Rutina completa de alta intensidad")
    ]
    
    # Añadir rutinas a la base de datos
    for routine in routines:
        db.session.add(routine)
    
    db.session.commit()
    
    # Asociar ejercicios con rutinas
    routine_exercises = [
        # Principiante - Full Body
        RoutineExercise(routine_id=1, exercise_id=1, sets=3, reps=12, order=1),
        RoutineExercise(routine_id=1, exercise_id=2, sets=3, reps=10, order=2),
        RoutineExercise(routine_id=1, exercise_id=3, sets=3, reps=15, order=3),
        RoutineExercise(routine_id=1, exercise_id=4, sets=3, reps=10, order=4),
        
        # Principiante - Tren Superior
        RoutineExercise(routine_id=2, exercise_id=1, sets=3, reps=12, order=1),
        RoutineExercise(routine_id=2, exercise_id=2, sets=3, reps=12, order=2),
        RoutineExercise(routine_id=2, exercise_id=4, sets=3, reps=10, order=3),
        
        # Principiante - Tren Inferior
        RoutineExercise(routine_id=3, exercise_id=3, sets=3, reps=15, order=1),
        RoutineExercise(routine_id=3, exercise_id=5, sets=3, reps=12, order=2),
        
        # Amateur - Empuje
        RoutineExercise(routine_id=4, exercise_id=2, sets=4, reps=10, order=1),
        RoutineExercise(routine_id=4, exercise_id=4, sets=4, reps=10, order=2),
        RoutineExercise(routine_id=4, exercise_id=8, sets=3, reps=12, order=3),
        
        # Amateur - Tirón
        RoutineExercise(routine_id=5, exercise_id=6, sets=4, reps=12, order=1),
        RoutineExercise(routine_id=5, exercise_id=9, sets=3, reps=15, order=2),
        RoutineExercise(routine_id=5, exercise_id=1, sets=3, reps=12, order=3),
        
        # Amateur - Piernas
        RoutineExercise(routine_id=6, exercise_id=3, sets=4, reps=12, order=1),
        RoutineExercise(routine_id=6, exercise_id=7, sets=3, reps=12, order=2),
        RoutineExercise(routine_id=6, exercise_id=5, sets=3, reps=12, order=3),
        
        # Medio - Pecho y Tríceps
        RoutineExercise(routine_id=7, exercise_id=4, sets=4, reps=10, order=1),
        RoutineExercise(routine_id=7, exercise_id=8, sets=4, reps=10, order=2),
        RoutineExercise(routine_id=7, exercise_id=14, sets=3, reps=12, order=3),
        
        # Medio - Espalda y Bíceps
        RoutineExercise(routine_id=8, exercise_id=6, sets=4, reps=10, order=1),
        RoutineExercise(routine_id=8, exercise_id=15, sets=4, reps=10, order=2),
        RoutineExercise(routine_id=8, exercise_id=1, sets=3, reps=12, order=3),
        RoutineExercise(routine_id=8, exercise_id=9, sets=3, reps=12, order=4),
        
        # Medio - Hombros y Abdominales
        RoutineExercise(routine_id=9, exercise_id=11, sets=4, reps=10, order=1),
        RoutineExercise(routine_id=9, exercise_id=8, sets=3, reps=12, order=2),
        RoutineExercise(routine_id=9, exercise_id=2, sets=3, reps=12, order=3),
        
        # Medio - Piernas
        RoutineExercise(routine_id=10, exercise_id=12, sets=4, reps=10, order=1),
        RoutineExercise(routine_id=10, exercise_id=13, sets=4, reps=12, order=2),
        RoutineExercise(routine_id=10, exercise_id=7, sets=3, reps=12, order=3),
        
        # Avanzado - Pecho y Espalda
        RoutineExercise(routine_id=11, exercise_id=17, sets=5, reps=8, order=1),
        RoutineExercise(routine_id=11, exercise_id=18, sets=5, reps=8, order=2),
        RoutineExercise(routine_id=11, exercise_id=15, sets=4, reps=10, order=3),
        
        # Avanzado - Piernas Intenso
        RoutineExercise(routine_id=12, exercise_id=16, sets=5, reps=8, order=1),
        RoutineExercise(routine_id=12, exercise_id=20, sets=4, reps=10, order=2),
        RoutineExercise(routine_id=12, exercise_id=13, sets=4, reps=12, order=3),
        
        # Avanzado - Hombros y Brazos
        RoutineExercise(routine_id=13, exercise_id=11, sets=4, reps=8, order=1),
        RoutineExercise(routine_id=13, exercise_id=14, sets=4, reps=10, order=2),
        RoutineExercise(routine_id=13, exercise_id=9, sets=4, reps=10, order=3),
        
        # Avanzado - Full Body Intenso
        RoutineExercise(routine_id=14, exercise_id=16, sets=4, reps=8, order=1),
        RoutineExercise(routine_id=14, exercise_id=17, sets=4, reps=8, order=2),
        RoutineExercise(routine_id=14, exercise_id=18, sets=4, reps=8, order=3),
        RoutineExercise(routine_id=14, exercise_id=19, sets=3, reps=6, order=4)
    ]
    
    # Añadir asociaciones de ejercicios y rutinas
    for routine_exercise in routine_exercises:
        db.session.add(routine_exercise)
    
    db.session.commit()

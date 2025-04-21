import os
import sys
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content

sendgrid_key = os.environ.get('SENDGRID_API_KEY')

def send_email(
    to_email,
    from_email,
    subject,
    text_content=None,
    html_content=None
):
    """
    Envía un correo electrónico usando SendGrid
    
    Args:
        to_email (str): Correo electrónico del destinatario
        from_email (str): Correo electrónico del remitente
        subject (str): Asunto del correo
        text_content (str, optional): Contenido en texto plano. Default: None
        html_content (str, optional): Contenido en HTML. Default: None
        
    Returns:
        bool: True si el correo se envió correctamente, False en caso contrario
    """
    if not sendgrid_key:
        print("ERROR: No se ha configurado SENDGRID_API_KEY")
        return False
        
    message = Mail(
        from_email=Email(from_email),
        to_emails=To(to_email),
        subject=subject
    )

    if html_content:
        message.content = Content("text/html", html_content)
    elif text_content:
        message.content = Content("text/plain", text_content)
    else:
        print("ERROR: Se debe proporcionar contenido en texto o HTML")
        return False

    try:
        sg = SendGridAPIClient(sendgrid_key)
        sg.send(message)
        return True
    except Exception as e:
        print(f"Error al enviar correo: {e}")
        return False

def send_welcome_email(user_email, username):
    """
    Envía un correo de bienvenida al usuario recién registrado
    
    Args:
        user_email (str): Correo electrónico del usuario
        username (str): Nombre de usuario
        
    Returns:
        bool: True si el correo se envió correctamente, False en caso contrario
    """
    subject = "¡Bienvenido a FitPesas!"
    from_email = "fitpesas@example.com"  # Reemplazar con tu correo real
    
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #ff7043; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; }}
            .footer {{ background-color: #f5f5f5; padding: 15px; text-align: center; font-size: 0.8em; }}
            .button {{ display: inline-block; background-color: #ff7043; color: white; text-decoration: none; padding: 10px 20px; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>¡Bienvenido a FitPesas!</h1>
            </div>
            <div class="content">
                <h2>Hola {username},</h2>
                <p>¡Gracias por unirte a nuestra comunidad de entrenamiento con pesas! Estamos emocionados de acompañarte en tu viaje hacia una mejor forma física.</p>
                
                <p>Con FitPesas podrás:</p>
                <ul>
                    <li>Acceder a rutinas personalizadas según tu nivel</li>
                    <li>Hacer seguimiento de tu progreso</li>
                    <li>Aprender técnicas adecuadas para cada ejercicio</li>
                    <li>Maximizar tus resultados con planes estructurados</li>
                </ul>
                
                <p>¡Comienza ahora a explorar tu nuevo plan de entrenamiento!</p>
                
                <p style="text-align: center; margin-top: 30px;">
                    <a href="https://fitpesas.replit.app/weekly_plan" class="button">Ver Mi Plan</a>
                </p>
            </div>
            <div class="footer">
                <p>Este correo fue enviado a {user_email}. Si no te registraste en FitPesas, por favor ignora este mensaje.</p>
                <p>&copy; 2025 FitPesas - Todos los derechos reservados</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(
        to_email=user_email,
        from_email=from_email,
        subject=subject,
        html_content=html_content
    )

def send_workout_completed_email(user_email, username, routine_name, calories_burned):
    """
    Envía un correo de felicitación cuando el usuario completa un entrenamiento
    
    Args:
        user_email (str): Correo electrónico del usuario
        username (str): Nombre de usuario
        routine_name (str): Nombre de la rutina completada
        calories_burned (int): Calorías estimadas quemadas
        
    Returns:
        bool: True si el correo se envió correctamente, False en caso contrario
    """
    subject = "¡Entrenamiento completado con éxito!"
    from_email = "fitpesas@example.com"  # Reemplazar con tu correo real
    
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #4caf50; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; }}
            .footer {{ background-color: #f5f5f5; padding: 15px; text-align: center; font-size: 0.8em; }}
            .stats {{ background-color: #f9f9f9; padding: 15px; margin: 20px 0; border-radius: 5px; }}
            .button {{ display: inline-block; background-color: #4caf50; color: white; text-decoration: none; padding: 10px 20px; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>¡Excelente trabajo!</h1>
            </div>
            <div class="content">
                <h2>Felicitaciones, {username}!</h2>
                <p>Has completado con éxito tu entrenamiento:</p>
                
                <div class="stats">
                    <h3>{routine_name}</h3>
                    <p><strong>Calorías quemadas:</strong> aproximadamente {calories_burned} calorías</p>
                    <p><strong>Fecha:</strong> {{'{{today}}'}}</p>
                </div>
                
                <p>Mantener esta constancia es clave para ver resultados. Recuerda que cada entrenamiento te acerca más a tus objetivos.</p>
                
                <p style="text-align: center; margin-top: 30px;">
                    <a href="https://fitpesas.replit.app/profile" class="button">Ver Mi Progreso</a>
                </p>
            </div>
            <div class="footer">
                <p>Este correo fue enviado a {user_email}.</p>
                <p>&copy; 2025 FitPesas - Todos los derechos reservados</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    html_content = html_content.replace("{{today}}", "{% now 'local', '%d/%m/%Y' %}")
    
    return send_email(
        to_email=user_email,
        from_email=from_email,
        subject=subject,
        html_content=html_content
    )
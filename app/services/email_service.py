import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings


class EmailService:
    
    @staticmethod
    def send_email(to_email: str, subject: str, html_content: str) -> bool:
        """Send email using SMTP"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
            msg['To'] = to_email
            
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Connect to SMTP server
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
            
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    @staticmethod
    def send_password_reset_email(email: str, token: str) -> bool:
        """Send password reset email"""
        reset_link = f"{settings.FRONTEND_URL}/biocalc/reset-password?token={token}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #10b981; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background-color: #f9fafb; padding: 30px; border-radius: 0 0 8px 8px; }}
                .button {{ display: inline-block; padding: 12px 24px; background-color: #10b981; color: white; text-decoration: none; border-radius: 6px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 20px; color: #6b7280; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🌿 BioCalc</h1>
                </div>
                <div class="content">
                    <h2>Recuperação de Senha</h2>
                    <p>Olá,</p>
                    <p>Recebemos uma solicitação para redefinir a senha da sua conta BioCalc.</p>
                    <p>Clique no botão abaixo para criar uma nova senha:</p>
                    <div style="text-align: center;">
                       <a href="{reset_link}" class="button" style="color: #ffffff !important; text-decoration: none;">Redefinir Senha</a>
                    </div>
                    <p><strong>Este link expira em 30 minutos.</strong></p>
                    <p>Se você não solicitou esta alteração, pode ignorar este e-mail com segurança.</p>
                    <hr style="margin: 20px 0; border: none; border-top: 1px solid #e5e7eb;">
                    <p style="font-size: 12px; color: #6b7280;">
                        Se o botão não funcionar, copie e cole este link no seu navegador:<br>
                        <a href="{reset_link}" style="color: #10b981;">{reset_link}</a>
                    </p>
                </div>
                <div class="footer">
                    <p>© 2024 BioCalc - Plataforma de Eficiência Energético-Ambiental</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return EmailService.send_email(
            to_email=email,
            subject="Recuperação de Senha - BioCalc",
            html_content=html_content
        )
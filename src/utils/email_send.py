# import os
# import glob
# from datetime import datetime
# import smtplib
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
# from email.mime.base import MIMEBase
# from email import encoders
# from utils.logger_config import loger_config
# from utils.config import load_config


# def send_email(to_email: str = None, subject: str = None, body: str = None, file_path: str = None) -> bool:
#     print("Loading configuration...")
#     config = load_config()
#     logger = loger_config()
#     smtp_config = config.get("smtp", {})

#     smtp_server = smtp_config.get("smtp_server")
#     smtp_port = smtp_config.get("smtp_port", 465)
#     sender_email = smtp_config.get("sender_email")
#     sender_password = smtp_config.get("sender_password")

#     to_email = to_email or smtp_config.get("to_email")
#     subject = subject or smtp_config.get("subject", "No Subject")
#     body = body or smtp_config.get("body", "")

#     # If file_path is not provided, find the latest CSV in csv_base_path
#     if not file_path:
#         csv_base_path = smtp_config.get("csv_base_path", "csv_output")
#         csv_prefix = smtp_config.get("csv_filename_prefix", "all_headlines")
#         search_pattern = os.path.join(csv_base_path, f"{csv_prefix}_*.csv")

#         csv_files = glob.glob(search_pattern)
#         if csv_files:
#             file_path = max(csv_files, key=os.path.getmtime)
#             logger.info(f"Automatically selected latest CSV: {file_path}")
#         else:
#             logger.error("No CSV files found to attach.")
#             return False

#     if not all([smtp_server, smtp_port, sender_email, sender_password]):
#         logger.error("Missing SMTP configuration in YAML.")
#         return False

#     logger.info(f"Preparing message to: {to_email}, subject: {subject}")

#     message = MIMEMultipart()
#     message["From"] = sender_email
#     message["To"] = to_email
#     message["Subject"] = subject
#     message.attach(MIMEText(body, "plain"))

#     if file_path:
#         logger.info(f"Attaching file: {file_path}")
#         if not os.path.exists(file_path):
#             logger.error(f"Attachment not found: {file_path}")
#             return False

#         try:
#             with open(file_path, "rb") as file:
#                 part = MIMEBase("application", "octet-stream")
#                 part.set_payload(file.read())
#                 encoders.encode_base64(part)
#                 part.add_header(
#                     "Content-Disposition",
#                     f"attachment; filename={os.path.basename(file_path)}"
#                 )
#                 message.attach(part)
#         except Exception as e:
#             logger.error(f"Error attaching file: {e}")
#             return False

#     try:
#         logger.info(f"Connecting to SMTP server: {smtp_server}:{smtp_port}")
#         server = smtplib.SMTP_SSL(smtp_server, smtp_port)

#         logger.info("Logging in...")
#         server.login(sender_email, sender_password)
#         logger.info("Sending email...")
#         server.sendmail(sender_email, to_email, message.as_string())
#         logger.info("Closing connection.")
#         server.quit()
#         logger.info(f"Email sent to {to_email}")
#         return True
#     except Exception as e:
#         logger.error(f"Failed to send email: {e.__class__.__name__}: {e}")
#         return False

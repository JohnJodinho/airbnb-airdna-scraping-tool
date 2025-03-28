from flask import current_app

# Global list to store log messages
log_messages = []

def custom_print(message):

    log_messages.append(message)  
    
    if current_app:
        current_app.logger.info(message)  

    print(message)  

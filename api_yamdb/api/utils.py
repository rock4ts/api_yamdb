from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail


def send_confirmation_code(user, sender_email, recipent_email):
    '''
    Function that generates and sends confirmation code for token request.
    '''
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        subject='confirmation code for get token',
        message=f'Your confirmation code: "{confirmation_code}"',
        from_email=sender_email,
        recipient_list=[recipent_email],
        fail_silently=False,
    )


def get_response_message(value=''):
    response_messages = {
        'successful_registration':
            'Пользователь успешно зарегистрирован, '
            'на указанную вами почту был отправлен код потверждения, '
            'он понадобится для получения токена.',
        'invalid_username':
            f'Пользователя с именем {value} не существует.',
        'invalid_email':
            'Вы ввели неправильный emal',
        'confirmation_code_sent':
            'Запрос успешно выполнен: обновлённый код для получения токена '
            'отправлен на ваш email.',
        'invalid_confirmation_code':
            'Неверный код подтверждения.',
        'user_not_found':
            'Пользователь не найден, проверьте корректность введённых данных.'
    }
    return response_messages

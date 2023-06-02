from django.utils import timezone
from rest_framework.exceptions import ValidationError


def allowed_username_validator(username):
    """
    Check username is not equal to the reserved word "me".
    """
    if username.lower() == 'me':
        raise ValidationError(
            f"Недопустимое имя пользователя: {username}."
        )
    return username


def score_validator(score):
    if not (1 <= score <= 10 and isinstance(score, int)):
        raise ValidationError(
            "Оценкой может быть целое число в диапазоне от 1 до 10."
        )
    return score


def year_validator(pub_year):
    if timezone.now().year < pub_year:
        raise ValidationError(
            "Год публикации не может быть позднее текущего года."
        )
    return pub_year

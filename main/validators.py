import magic
from django.core.validators import ValidationError, RegexValidator
from django.template.defaultfilters import filesizeformat
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _

@deconstructible
class FileValidator:
    error_messages = {
        'max_size': ("Ensure this file size is not greater than %(max_size)s."
                     " Your file size is %(size)s."),
        'min_size': ("Ensure this file size is not less than %(min_size)s. "
                     "Your file size is %(size)s."),
        'content_type': "Files of type %(content_type)s are not supported.",
    }

    def __init__(self, max_size=None, min_size=None, content_types=()):
        self.max_size = max_size
        self.min_size = min_size
        self.content_types = content_types

    def __call__(self, data):
        if self.max_size is not None and data.size > self.max_size:
            params = {
                'max_size': filesizeformat(self.max_size),
                'size': filesizeformat(data.size),
            }
            raise ValidationError(self.error_messages['max_size'],
                                  'max_size', params)

        if self.min_size is not None and data.size < self.min_size:
            params = {
                'min_size': filesizeformat(self.mix_size),
                'size': filesizeformat(data.size)
            }
            raise ValidationError(self.error_messages['min_size'],
                                  'min_size', params)

        content_type = magic.from_buffer(data.read(), mime=True)
        data.seek(0)
        if self.content_types:
            if content_type not in self.content_types:
                params = {'content_type': content_type}
                raise ValidationError(self.error_messages['content_type'],
                                      'content_type', params)
        return {'content_type': content_type}

    def __eq__(self, other):
        return (
                isinstance(other, FileValidator) and
                self.max_size == other.max_size and
                self.min_size == other.min_size and
                self.content_types == other.content_types
        )


class VoteRequestValidator:

    def __call__(self, data: dict):
        if data.get('vote_type') is None:
            raise ValidationError('vote_type not specified')

        if data.get('votable_type') is None:
            raise ValidationError('votable_type not specified')

        if data.get('votable_id') is None:
            raise ValidationError('votable_id not specified')

        if data.get('voter') is None:
            raise ValidationError('voter is not specified')


@deconstructible
class UsernameValidator(RegexValidator):
    regex = r'^[\w-]+$'
    message = _(
        'Enter a valid username. This value may contain only letters, '
        'numbers, and -/_ characters.'
    )
    flags = 0

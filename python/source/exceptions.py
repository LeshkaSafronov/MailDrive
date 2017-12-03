class MailDrive(Exception):
    pass


class UserExists(MailDrive):
    def __str__(self):
        return 'User with supplied email or telephone number already exists'


class FieldRequired(MailDrive):
    def __init__(self, field_name):
        self.field_name = field_name

    def __str__(self):
        return '{} is required'.format(self.field_name)

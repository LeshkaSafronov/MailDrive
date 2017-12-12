class MailDrive(Exception):
    pass


class UserExists(MailDrive):
    def __str__(self):
        return 'User with supplied email or telephone number already exists'


class UserDoesNotExists(MailDrive):
    def __init__(self, user_id):
        self.user_id = user_id

    def __str__(self):
        return 'User with supplied id: {} does not exists'.format(self.user_id)


class FieldRequired(MailDrive):
    def __init__(self, field_name):
        self.field_name = field_name

    def __str__(self):
        return '{} is required'.format(self.field_name)


class MailRecipientNotExist(MailDrive):
    def __str__(self):
        return 'Recipient not setup'


class MailAlreadySended(MailDrive):
    def __str__(self):
        return 'Mail already sended'
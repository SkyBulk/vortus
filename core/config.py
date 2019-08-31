class ServerConfig(object):

    @staticmethod
    def ui_bot_identifier(slave_obj):
        return slave_obj.ip + '@' + slave_obj.username

    UI_BOT_IDENTIFIER = ui_bot_identifier
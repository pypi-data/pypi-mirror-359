# Receive BAP or BPP notifications
# Ensure their format
# Check DjangoLDP ActivityQueue receiver current implementation, may require adaptations
# Consume methods from .inbox: confirm, init, on_confirm, on_init, on_select, select
# confirm, init, select: Send an on_confirm, on_init, on_select to transation's BAP inbox
# Respond 200, 201, 403, 404, 40X
from .__base_viewset import BaseViewset


class InboxViewset(BaseViewset):
    def _handle_activity(self, activity, **kwargs):
        if activity.type == "confirm":
            self.handle_confirm_activity(activity, **kwargs)
        elif activity.type == "init":
            self.handle_init_activity(activity, **kwargs)
        elif activity.type == "select":
            self.handle_select_activity(activity, **kwargs)
        elif activity.type == "on_confirm":
            self.handle_on_confirm_activity(activity, **kwargs)
        elif activity.type == "on_init":
            self.handle_on_init_activity(activity, **kwargs)
        elif activity.type == "on_select":
            self.handle_on_select_activity(activity, **kwargs)

    def handle_confirm_activity(self, activity, **kwargs):
        pass

    def handle_init_activity(self, activity, **kwargs):
        pass

    def handle_select_activity(self, activity, **kwargs):
        pass

    def handle_on_confirm_activity(self, activity, **kwargs):
        pass

    def handle_on_init_activity(self, activity, **kwargs):
        pass

    def handle_on_select_activity(self, activity, **kwargs):
        pass

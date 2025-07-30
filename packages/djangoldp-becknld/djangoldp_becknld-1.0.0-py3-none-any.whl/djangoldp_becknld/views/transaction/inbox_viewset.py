# Receive BAP or BPP notifications
# Ensure their format
# Check DjangoLDP ActivityQueue receiver current implementation, may require adaptations
# Consume methods from .inbox: confirm, init, on_confirm, on_init, on_select, select
# confirm, init, select: Send an on_confirm, on_init, on_select to transation's BAP inbox
# Respond 200, 201, 403, 404, 40X

class InboxViewset:
    pass

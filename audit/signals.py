import json

from django.contrib.auth.models import AnonymousUser
from django.core.serializers import serialize
from django.db import connection, transaction
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from audit.models import AuditLog
from utils.current_user import get_current_ip, get_current_user

# def exclude_models(*excluded_models):
#     def decorator(signal_function):
#         def wrapper(sender, instance, **kwargs):
#             if sender in excluded_models:
#                 return
#             return signal_function(sender, instance, **kwargs)

#         return wrapper

#     return decorator


# @receiver(post_save)
# @exclude_models(AuditLog)
# def track_model_changes(sender, instance, created, **kwargs):
#     action = "CREATE" if created else "UPDATE"

#     instance_data = {
#         k: v for k, v in instance.__dict__.items() if not k.startswith("_")
#     }

#     def log_action():
#         try:
#             AuditLog.objects.create(
#                 user=get_current_user(),
#                 action=action,
#                 ip_address=get_current_ip(),
#                 resource=sender.__name__,
#                 resource_id=str(instance.pk),
#                 additional_info={"fields": instance_data},
#             )
#         except Exception as e:
#             print(f"Audit log creation failed: {e}")

#     transaction.on_commit(log_action)


# @receiver(post_delete)
# @exclude_models(AuditLog)
# def track_model_deletion(sender, instance, **kwargs):
#     try:
#         AuditLog.objects.create(
#             user=get_current_user(),
#             action="DELETE",
#             resource=sender.__name__,
#             ip_address=get_current_ip(),
#             resource_id=str(instance.pk),
#             additional_info={"fields": instance.__dict__},
#         )
#     except Exception as e:
#         print(f"Failed to create delete audit log for {sender.__name__}: {e}")


# To store the previous state before update
pre_save_cache = {}


def serialize_instance(instance):
    """Serialize a model instance to JSON."""
    data = serialize("json", [instance])
    return json.loads(data)[0]["fields"]


def is_migration_running():
    """Check if migrations are currently running."""
    return (
        "migrate" in connection.queries or connection.settings_dict.get("NAME") is None
    )


@receiver(pre_save)
def cache_previous_instance(sender, instance, **kwargs):
    if sender != AuditLog and not is_migration_running():
        if instance.pk:
            try:
                previous_instance = sender.objects.get(pk=instance.pk)
                pre_save_cache[instance.pk] = serialize_instance(previous_instance)
            except sender.DoesNotExist:
                pre_save_cache[instance.pk] = None


@receiver(post_save)
def create_or_update_audit_log(sender, instance, created, **kwargs):
    print(get_current_user(), "user of the current USER in the Audit")

    if not get_current_user() or isinstance(get_current_user(), AnonymousUser):
        return
    if sender != AuditLog and not is_migration_running():
        table_name = sender._meta.db_table

        previous_snapshot = pre_save_cache.get(instance.pk, None)
        updated_snapshot = serialize_instance(instance)
        user = get_current_user()
        print("Currenet USER", user)
        if created:
            AuditLog.objects.create(
                user=user,
                action="create",
                resource=table_name,
                object_id=instance.pk,
                previous_snapshot=None,
                updated_snapshot=updated_snapshot,
                ip_address=get_current_ip(),
            )
        else:
            AuditLog.objects.create(
                user=user,
                action="update",
                resource=table_name,
                object_id=instance.pk,
                previous_snapshot=previous_snapshot,
                updated_snapshot=updated_snapshot,
                ip_address=get_current_ip(),
            )


@receiver(post_delete)
def delete_audit_log(sender, instance, **kwargs):
    # print(kwargs.get("user", None), "currently Login User with the help of others")
    if not get_current_user() or isinstance(get_current_user(), AnonymousUser):
        return
    if sender != AuditLog and not is_migration_running():
        table_name = sender._meta.db_table

        AuditLog.objects.create(
            user=get_current_user(),
            action="delete",
            resource=table_name,
            object_id=instance.pk,
            previous_snapshot=serialize_instance(instance),
            updated_snapshot=None,
            ip_address=get_current_ip(),
        )

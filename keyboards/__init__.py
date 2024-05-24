from .reply.admin_rk import main_menu
from .inline.admin_ik import edit_tenant_data, registration_application, settings, readings_come
from .inline.tenant_ik import readings_send_init, readings_editor, confirm_sending


__all__ = (
    # Админ
    'main_menu',
    'edit_tenant_data',
    'registration_application',
    'settings',
    'readings_come',

    # Квартирант
    'readings_send_init',
    'readings_editor',
    'confirm_sending'
)

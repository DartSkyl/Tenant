from .reply.admin_rk import main_menu
from .inline.admin_ik import (edit_tenant_data, registration_application, confirm_check, ten_rem_conf,
                              settings, readings_come, send_payment_slip, send_ps, viewing_tenant, view_history_checks)
from .inline.tenant_ik import readings_send_init, readings_editor, confirm_sending, send_check, check_ready


__all__ = (
    # Админ
    'main_menu',
    'edit_tenant_data',
    'registration_application',
    'settings',
    'readings_come',
    'send_payment_slip',
    'send_ps',
    'confirm_check',
    'viewing_tenant',
    'ten_rem_conf',
    'view_history_checks',

    # Квартирант
    'readings_send_init',
    'readings_editor',
    'confirm_sending',
    'send_check',
    'check_ready'
)

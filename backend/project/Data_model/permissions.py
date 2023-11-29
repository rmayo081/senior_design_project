from flask_principal import Permission, RoleNeed
from Data_model.models import RoleEnum

superuser_permission = Permission(RoleNeed(RoleEnum.SUPERUSER))
admin_permission = Permission(RoleNeed(RoleEnum.ADMIN))
ccg_permission = Permission(RoleNeed(RoleEnum.CCG))
viewer_permission = Permission(RoleNeed(RoleEnum.VIEWER))
authenticated_permission = Permission(*[RoleNeed(role) for role in RoleEnum if role != RoleEnum.UNAUTHORIZED])
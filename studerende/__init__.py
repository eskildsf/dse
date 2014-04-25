from django.contrib.auth.models import User, Group
import django_auth_ldap.backend

def populate_profile(sender, user=None, ldap_user=None, **kwargs):
    Group.objects.get(name='DSE').user_set.add(user)
    user.is_active = True
    user.is_staff = True
    user.save()

django_auth_ldap.backend.populate_user.connect(populate_profile)

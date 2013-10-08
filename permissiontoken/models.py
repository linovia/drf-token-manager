import uuid
import hmac
from hashlib import sha1
from rest_framework.compat import AUTH_USER_MODEL
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class Token(models.Model):
    """
    The default authorization token model.
    """
    key = models.CharField(_('key'), max_length=40, primary_key=True)
    user = models.ForeignKey(AUTH_USER_MODEL, verbose_name=_('user'),
        related_name='auth_token')
    created = models.DateTimeField(_('creation date'), auto_now_add=True)
    permissions = models.ManyToManyField('auth.Permission',
        verbose_name=_('token permissions'), blank=True,
        help_text='Specific permissions for this token.')

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(Token, self).save(*args, **kwargs)

    def generate_key(self):
        unique = uuid.uuid4()
        return hmac.new(unique.bytes, digestmod=sha1).hexdigest()

    def __str__(self):
        return self.key

    def get_all_permissions(self):
        if not hasattr(self, '_perm_cache'):
            self._perm_cache = set(["%s.%s" % (p.content_type.app_label, p.codename) for p in self.permissions.select_related()])
        return self._perm_cache

    def has_perm(self, perm):
        return perm in self.get_all_permissions()

    def has_perms(self, perm_list):
        for perm in perm_list:
            if not self.has_perm(perm):
                return False
        return True

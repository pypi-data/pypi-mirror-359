from cubicweb import ValidationError
from cubicweb.predicates import is_instance
from cubicweb.sobjects.notification import ContentAddedView
from cubicweb.server.hook import Hook


class LinkAddedView(ContentAddedView):
    """get notified from new links"""

    __select__ = is_instance("Link")
    content_attr = "description"


class NoDuplicateHook(Hook):
    """Before adding/updating a link, check that the URL is not already in the
    database.
    """

    __regid__ = "link_no_duplicate_hook"
    __select_ = Hook.__select__ & is_instance("Link")
    events = ("before_add_entity", "before_update_entity")

    def __call__(self):
        try:
            new_url = self.entity.cw_edited["url"]
        except KeyError:
            return

        if self._cw.find("Link", url=new_url):
            msg = self._cw._("This URL is already existing")
            raise ValidationError(self.entity.eid, {"url": msg})

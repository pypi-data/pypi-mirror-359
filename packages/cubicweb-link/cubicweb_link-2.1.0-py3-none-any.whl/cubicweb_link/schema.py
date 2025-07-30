from yams.buildobjs import EntityType, String, RichString

from cubicweb import _


class Link(EntityType):
    """a link to an external internet resource"""

    title = String(required=True, fulltextindexed=True, maxsize=256)
    url = String(
        required=True, fulltextindexed=True, maxsize=512, description=_("link's url")
    )
    description = RichString(
        fulltextindexed=True, description=_("description of the linked page's content")
    )

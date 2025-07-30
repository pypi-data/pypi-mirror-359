# copyright 2012-2024 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

"""Specific views for SIOC (Semantically-Interlinked Online Communities)

http://sioc-project.org
"""

__docformat__ = "restructuredtext en"
try:
    from cubicweb import _
except ImportError:
    _ = str


from logilab.mtconverter import xml_escape

from cubicweb_web.view import EntityView, EntityAdapter
from cubicweb.predicates import adaptable


class ISIOCItemAdapter(EntityAdapter):
    """interface for entities which may be represented as an ISIOC items"""

    __needs_bw_compat__ = True
    __regid__ = "ISIOCItem"
    __abstract__ = True

    def isioc_content(self):
        """return item's content"""
        raise NotImplementedError

    def isioc_container(self):
        """return container entity"""
        raise NotImplementedError

    def isioc_type(self):
        """return container type (post, BlogPost, MailMessage)"""
        raise NotImplementedError

    def isioc_replies(self):
        """return replies items"""
        raise NotImplementedError

    def isioc_topics(self):
        """return topics items"""
        raise NotImplementedError


class ISIOCContainerAdapter(EntityAdapter):
    """interface for entities which may be represented as an ISIOC container"""

    __needs_bw_compat__ = True
    __regid__ = "ISIOCContainer"
    __abstract__ = True

    def isioc_type(self):
        """return container type (forum, Weblog, MailingList)"""
        raise NotImplementedError

    def isioc_items(self):
        """return contained items"""
        raise NotImplementedError


class SIOCView(EntityView):
    __regid__ = "sioc"
    __select__ = adaptable("ISIOCItem", "ISIOCContainer")
    title = _("sioc")
    templatable = False
    content_type = "text/xml"

    def call(self):
        self.w(f'<?xml version="1.0" encoding="{self._cw.encoding}"?>\n')
        self.w(
            """<rdf:RDF
             xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
             xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
             xmlns:owl="http://www.w3.org/2002/07/owl#"
             xmlns:foaf="http://xmlns.com/foaf/0.1/"
             xmlns:sioc="http://rdfs.org/sioc/ns#"
             xmlns:sioctype="http://rdfs.org/sioc/types#"
             xmlns:dcterms="http://purl.org/dc/terms/">\n"""
        )
        for i in range(self.cw_rset.rowcount):
            self.cell_call(i, 0)
        self.w("</rdf:RDF>\n")

    def cell_call(self, row, col):
        self.wview("sioc_element", self.cw_rset, row=row, col=col)


class SIOCContainerView(EntityView):
    __regid__ = "sioc_element"
    __select__ = adaptable("ISIOCContainer")
    templatable = False
    content_type = "text/xml"

    def cell_call(self, row, col):
        entity = self.cw_rset.complete_entity(row, col)
        isioc = entity.cw_adapt_to("ISIOCContainer")
        isioct = isioc.isioc_type()
        self.w(f'<sioc:{isioct} rdf:about="{xml_escape(entity.absolute_url())}">\n')
        self.w(f"<dcterms:title>{xml_escape(entity.dc_title())}</dcterms:title>")
        self.w(f"<dcterms:created>{entity.creation_date.isoformat()}</dcterms:created>")
        self.w(
            "<dcterms:modified>%s</dcterms:modified>"
            % entity.modification_date.isoformat()
        )
        self.w("<!-- FIXME : here be items -->")  # entity.isioc_items()
        self.w(f"</sioc:{isioct}>\n")


class SIOCItemView(EntityView):
    __regid__ = "sioc_element"
    __select__ = adaptable("ISIOCItem")
    templatable = False
    content_type = "text/xml"

    def cell_call(self, row, col):
        entity = self.cw_rset.complete_entity(row, col)
        isioc = entity.cw_adapt_to("ISIOCItem")
        isioct = isioc.isioc_type()
        self.w(f'<sioc:{isioct} rdf:about="{xml_escape(entity.absolute_url())}">\n')
        self.w(f"<dcterms:title>{xml_escape(entity.dc_title())}</dcterms:title>")
        self.w(f"<dcterms:created>{entity.creation_date.isoformat()}</dcterms:created>")
        self.w(
            "<dcterms:modified>%s</dcterms:modified>"
            % entity.modification_date.isoformat()
        )
        content = isioc.isioc_content()
        if content:
            self.w(f"<sioc:content>{xml_escape(content)}</sioc:content>")
        container = isioc.isioc_container()
        if container:
            self.w(
                '<sioc:has_container rdf:resource="%s"/>\n'
                % xml_escape(container.absolute_url())
            )
        if entity.creator:
            self.w("<sioc:has_creator>\n")
            self.w(
                f'<sioc:User rdf:about="{xml_escape(entity.creator.absolute_url())}">\n'
            )
            self.w(entity.creator.view("foaf"))
            self.w("</sioc:User>\n")
            self.w("</sioc:has_creator>\n")
        self.w("<!-- FIXME : here be topics -->")  # entity.isioc_topics()
        self.w("<!-- FIXME : here be replies -->")  # entity.isioc_replies()
        self.w(f" </sioc:{isioct}>\n")

"""bootstrap implementation of base templates

:organization: Logilab
:copyright: 2013 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

__docformat__ = "restructuredtext en"

from logilab.common.decorators import monkeypatch

from logilab.mtconverter import xml_escape

from cubicweb.schema import display_name
from cubicweb.utils import UStringIO

from cubicweb_web.views import basetemplates, basecomponents, actions

from cubicweb_web.views.boxes import SearchBox

HTML5 = "<!DOCTYPE html>"

basetemplates.TheMainTemplate.doctype = HTML5

# options which can be changed freely
basetemplates.TheMainTemplate.twbs_container_cls = "container-fluid"
basetemplates.TheMainTemplate.twbs_col_cls = "col-xs-"
basetemplates.TheMainTemplate.twbs_col_size = 2

# options which require recompiling bootstrap.css from source
basetemplates.TheMainTemplate.twbs_grid_columns = 12


@monkeypatch(basetemplates.TheMainTemplate)  # noqa: F811
def call(self, view):
    self.set_request_content_type()
    self.template_header(self.content_type, view)
    self.template_page_content(view)


@monkeypatch(basetemplates.TheMainTemplate)
def template_header(
    self, content_type, view=None, page_title="", additional_headers=()
):
    page_title = page_title or view.page_title()
    additional_headers = additional_headers or view.html_headers()
    self.template_html_header(content_type, page_title, additional_headers)


@monkeypatch(basetemplates.TheMainTemplate)
def template_html_header(self, content_type, page_title, additional_headers=()):
    w = self.whead
    self.write_doctype()
    self._cw.html_headers.define_var("BASE_URL", self._cw.base_url())
    self._cw.html_headers.define_var("DATA_URL", self._cw.datadir_url)
    w(
        '<meta http-equiv="content-type" content="%s; charset=%s"/>\n'
        % (content_type, self._cw.encoding)
    )
    w(
        '<meta name="viewport" content="initial-scale=1.0, '
        'maximum-scale=1.0, width=device-width"/>'
    )
    w("\n".join(additional_headers) + "\n")
    self.wview("htmlheader", rset=self.cw_rset)
    if page_title:
        w(f"<title>{xml_escape(page_title)}</title>\n")


@monkeypatch(basetemplates.TheMainTemplate)
def template_page_content(self, view):
    w = self.w
    self.w("<body>\n")
    self.wview("header", rset=self.cw_rset, view=view)
    w(f'<div id="page" class="{self.twbs_container_cls}">\n')
    w('<div class="row">\n')
    left_boxes = list(
        self._cw.vreg["ctxcomponents"].poss_visible_objects(
            self._cw, rset=self.cw_rset, view=view, context="left"
        )
    )
    right_boxes = list(
        self._cw.vreg["ctxcomponents"].poss_visible_objects(
            self._cw, rset=self.cw_rset, view=view, context="right"
        )
    )
    nb_boxes = int(bool(left_boxes)) + int(bool(right_boxes))
    content_cols = self.twbs_grid_columns
    if nb_boxes:
        content_cols = self.twbs_grid_columns - self.twbs_col_size * nb_boxes
    self.nav_column(view, left_boxes, "left")
    self.content_column(view, content_cols)
    self.nav_column(view, right_boxes, "right")
    self.w("</div>\n")  # closes class=row
    self.w("</div>\n")  # closes id="page" from template_page_content
    self.template_footer(view)
    self.w("</body>\n")


@monkeypatch(basetemplates.TheMainTemplate)  # noqa: F811
def get_components(self, view, context):
    ctxcomponents = self._cw.vreg["ctxcomponents"]
    return ctxcomponents.poss_visible_objects(
        self._cw, rset=self.cw_rset, view=view, context=context
    )


@monkeypatch(basetemplates.TheMainTemplate)
def state_header(self):
    state = self._cw.search_state
    if state[0] == "normal":
        return
    _ = self._cw._
    value = self._cw.view("oneline", self._cw.eid_rset(state[1][1]))
    target, eid, r_type, searched_type = self._cw.search_state[1]
    cancel_link = """<a href="{url}" role="button"
    class="btn btn-default" title="{title}">{title}</a>""".format(
        url=self._cw.build_url(str(eid), vid="edition", __mode="normal"),
        title=_("cancel"),
    )
    msg = " ".join(
        (
            _("searching for"),
            f'<strong>"{display_name(self._cw, state[1][3])}"</strong>',
            _("to associate with"),
            value,
            _("by relation"),
            f'<strong>"{display_name(self._cw, state[1][2], state[1][0])}"</strong>',
            cancel_link,
        )
    )
    return self.w(f'<div class="alert alert-info">{msg}</div>')


@monkeypatch(basetemplates.TheMainTemplate)
def nav_column(self, view, boxes, context):
    if boxes:
        stream = UStringIO()
        for box in boxes:
            box.render(w=stream.write, view=view)
        html = stream.getvalue()
        if html:
            # only display aside columns if html availble
            self.w(
                '<aside id="aside-main-%s" class="%s%s cwjs-aside">\n'
                % (context, self.twbs_col_cls, self.twbs_col_size)
            )
            self.w(html)
            self.w("</aside>\n")
    return len(boxes)


@monkeypatch(basetemplates.TheMainTemplate)
def content_column(self, view, content_cols):
    w = self.w
    w(f'<div id="main-center" class="{self.twbs_col_cls}{content_cols}" role="main">')
    components = self._cw.vreg["components"]
    self.content_components(view, components)
    w('<div id="pageContent">')
    self.content_header(view)
    vtitle = self._cw.form.get("vtitle")
    if vtitle:
        w(f'<div class="vtitle">{xml_escape(vtitle)}</div>\n')
    self.state_header()
    self.content_navrestriction_components(view, components)
    nav_html = UStringIO()
    if view and not view.handle_pagination:
        view.paginate(w=nav_html.write)
    w(nav_html.getvalue())
    w('<div id="contentmain">\n')
    view.render(w=w)
    w("</div>\n")  # closes id=contentmain
    w(nav_html.getvalue())
    self.content_footer(view)
    w("</div>\n")  # closes div#pageContent
    w("</div>\n")  # closes div.%(prefix)s-%(col)s


@monkeypatch(basetemplates.TheMainTemplate)
def content_components(self, view, components):
    """TODO : should use context"""
    rqlcomp = components.select_or_none("rqlinput", self._cw, rset=self.cw_rset)
    if rqlcomp:
        rqlcomp.render(w=self.w, view=view)
    msgcomp = components.select_or_none("applmessages", self._cw, rset=self.cw_rset)
    if msgcomp:
        msgcomp.render(w=self.w)


@monkeypatch(basetemplates.TheMainTemplate)
def content_navrestriction_components(self, view, components):
    # display entity type restriction component
    etypefilter = components.select_or_none(
        "etypenavigation", self._cw, rset=self.cw_rset
    )
    if etypefilter and etypefilter.cw_propval("visible"):
        etypefilter.render(w=self.w)


@monkeypatch(basetemplates.TheMainTemplate)
def template_footer(self, view=None):
    self.wview("footer", rset=self.cw_rset, view=view)


# main header

basecomponents.ApplLogo.context = "header-logo"
# use basecomponents.ApplicationName.visible = False
basecomponents.ApplicationName.context = "header-left"
basecomponents.ApplLogo.order = 1
basecomponents.ApplicationName.order = 10
basecomponents.CookieLoginComponent.order = 10
basecomponents.AuthenticatedUserStatus.order = 5
SearchBox.order = -1
SearchBox.context = "header-right"
SearchBox.layout_id = "simple-layout"


@monkeypatch(basetemplates.HTMLPageHeader)  # noqa: F811
def call(self, view, **kwargs):  # noqa: F811
    self.main_header(view)
    self.breadcrumbs(view)


def get_components(self, view, context):  # noqa: F811
    ctxcomponents = self._cw.vreg["ctxcomponents"]
    return ctxcomponents.poss_visible_objects(
        self._cw, rset=self.cw_rset, view=view, context=context
    )


basetemplates.HTMLPageHeader.get_components = get_components
basetemplates.HTMLPageHeader.css = {
    "navbar-extra": "navbar-default",
    "breadcrumbs": "cw-breadcrumb",
    "container-cls": basetemplates.TheMainTemplate.twbs_container_cls,
    "header-left": "",
    "header-right": "navbar-right",
}


@monkeypatch(basetemplates.HTMLPageHeader)
def main_header(self, view):
    w = self.w
    w(f"<nav class=\"navbar {self.css['navbar-extra']}\" role=\"banner\">")
    w(f"<div class=\"{self.css['container-cls']}\">")
    self.display_navbar_header(w, view)
    w('<div id="tools-group" class="collapse navbar-collapse">')
    self.display_header_components(w, view, "header-left")
    self.display_header_components(w, view, "header-right")
    w("</div></div></nav>")


def display_navbar_header(self, w, view):
    w(
        """<div class="navbar-header">
    <button class="navbar-toggle" data-target="#tools-group" data-toggle="collapse" type="button">
    <span class="sr-only">%(toggle_label)s</span>
    <span class="icon-bar"></span>
    <span class="icon-bar"></span>
    <span class="icon-bar"></span>
    </button>"""
        % {"toggle_label": self._cw._("Toggle navigation")}
    )
    components = self.get_components(view, context="header-logo")
    if components:
        for component in components:
            component.render(w=w)
    w("</div>")


basetemplates.HTMLPageHeader.display_navbar_header = display_navbar_header


def display_header_components(self, w, view, context):
    components = self.get_components(view, context=context)
    if components:
        w(f'<ul class="nav navbar-nav {self.css[context]}">')
        for component in components:
            w("<li>")
            component.render(w=w)
            w("</li>")
        w("</ul>")


basetemplates.HTMLPageHeader.display_header_components = display_header_components


@monkeypatch(basetemplates.HTMLPageHeader)
def breadcrumbs(self, view):
    components = self.get_components(view, context="header-center")
    if components:
        self.w(
            '<nav role="navigation" class="%s">'
            % self.css.get("breadcrumbs", "breadcrumbs-defaul")
        )
        for component in components:
            component.render(w=self.w)
        self.w("</nav>")


@monkeypatch(basetemplates.HTMLContentFooter)  # noqa: F811
def call(self, view, **kwargs):  # noqa: F811
    components = self._cw.vreg["ctxcomponents"].poss_visible_objects(
        self._cw, rset=self.cw_rset, view=view, context="navbottom"
    )
    if components:
        # the row is needed here to correctly put the HTML flux
        self.w('<div id="contentfooter">')
        for comp in components:
            comp.render(w=self.w, view=view)
        self.w("</div>")


@monkeypatch(basetemplates.HTMLPageFooter)  # noqa: F811
def call(self, **kwargs):  # noqa: F811
    self.w('<footer id="pagefooter" role="contentinfo">')
    self.footer_content()
    self.w("</footer>\n")


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__)
    vreg.unregister(actions.CancelSelectAction)
